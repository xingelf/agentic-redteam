---
title: "jsonpickle: How py/reduce Turns Deserialization into RCE"
tags: ["security-basics", "deserialization", "python"]
---

# jsonpickle: How py/reduce Turns Deserialization into RCE

**TL;DR** — `jsonpickle` can rebuild arbitrary Python objects from JSON. Its
`py/reduce` marker lets the serialized data name a callable and its arguments, so
decoding attacker-controlled JSON with `unsafe=True` is remote code execution. The
fix is not a filter; it is: do not deserialize untrusted data with it.

## What jsonpickle does

`jsonpickle` serializes complex Python objects to JSON and restores them later.
To rebuild objects that plain JSON cannot represent, it embeds type information in
special markers:

- `py/type` — the type to construct
- `py/tuple` — constructor arguments
- `py/reduce` — combines a callable with its arguments to reconstruct the object

That last one is the problem. `py/reduce` mirrors Python's `__reduce__` protocol,
which says "to rebuild me, call this callable with these arguments." If the data
decides the callable, the data decides what runs.

## The attack

This looks like it handles ordinary user data:

```python
import jsonpickle

# untrusted input
malicious = '{"info": {"py/reduce": [{"py/type": "subprocess.Popen"}, {"py/tuple": [["id"]]}]}}'

obj = jsonpickle.decode(malicious, unsafe=True)
```

Decoding this calls `subprocess.Popen(["id"])`. Swap `["id"]` for anything and
that runs instead. Breaking the payload down:

1. `"py/type": "subprocess.Popen"` — a class that runs system commands
2. `"py/tuple": [["id"]]` — the arguments to pass
3. `"py/reduce"` — call the first with the second

The command runs with the privileges of the process doing the decode. That is
full RCE from a single JSON string.

## Why the feature exists

`py/reduce` is not a bug; it is the mechanism that makes jsonpickle able to
round-trip custom classes and objects standard JSON cannot express. It is only
dangerous when pointed at input you do not control. The same shape of bug exists
in Python `pickle`, PyYAML `yaml.load` (pre-safe defaults), and many other
language runtimes — any deserializer that can instantiate arbitrary types is a
code-execution primitive.

## Defense

### Do not deserialize untrusted data with it

The only reliable control. If the data crosses a trust boundary, do not hand it to
`jsonpickle.decode(..., unsafe=True)`. Note that `unsafe=True` is required for the
dangerous path — never set it on external input.

### Use a format that cannot execute

For data interchange, plain `json` moves values, not types, so it cannot
instantiate a class:

```python
import json
data = json.loads(untrusted_str)   # dict/list/str/number/bool/None only
```

### Validate against a schema

If you must accept structured input, parse as plain JSON and check it against an
explicit schema before use:

```python
import json

def safe_load(s):
    data = json.loads(s)
    if not isinstance(data.get("admin"), bool):
        raise ValueError("bad admin")
    if not isinstance(data.get("username"), str):
        raise ValueError("bad username")
    return data
```

A dataclass with typed fields and a checked `from_json` makes this the default
path rather than an afterthought.

### Contain the blast radius

Defense in depth for the case something slips through:

- Run the service with least privilege, so RCE is not root.
- Keep deserialization off network-facing paths where you can.
- Log and alert on decode errors and unexpected process spawns.

## Takeaway

Any deserializer that can build arbitrary objects is an execution engine, not just
a parser. With jsonpickle the trigger is `py/reduce` plus `unsafe=True`. Treat
serialized input from outside your trust boundary as code, and use a format that
can only carry data when you do not need to rebuild real objects.
