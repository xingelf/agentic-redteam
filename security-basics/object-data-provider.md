---
title: "ObjectDataProvider: A .NET Deserialization Gadget"
tags: ["security-basics", "deserialization", "dotnet"]
---

# ObjectDataProvider: A .NET Deserialization Gadget

**TL;DR** — WPF's `ObjectDataProvider` was built to call a method on an object and
expose the result to data binding, declaratively in XAML. That same ability —
"construct this type, call this method, with these arguments" — is exactly what a
deserialization attacker needs. It is one of the best-known gadgets for turning
unsafe .NET deserialization into command execution.

## What it is meant to do

`ObjectDataProvider` is a WPF helper that instantiates a class, invokes one of its
methods, and makes the return value bindable to the UI. Normal, benign use:

```xml
<ObjectDataProvider x:Key="FileList"
                    ObjectType="{x:Type local:FileService}"
                    MethodName="GetFiles">
  <ObjectDataProvider.MethodParameters>
    <system:String>C:\Docs</system:String>
  </ObjectDataProvider.MethodParameters>
</ObjectDataProvider>
```

The key properties:

- `ObjectType` / `ObjectInstance` — which object to use
- `MethodName` — which method to call
- `MethodParameters` — the arguments to pass

So it is a declarative way to say: make this object, call this method, with these
arguments. Hold that thought.

## Why attackers care

Many .NET serializers (`BinaryFormatter`, `NetDataContractSerializer`,
`SoapFormatter`, and others, depending on configuration) reconstruct whatever type
the serialized data names, and set its properties. If an attacker controls that
data, they can embed an `ObjectDataProvider` whose `MethodName` is `Start` on a
`Process` with `MethodParameters` pointing at `cmd.exe`. When the target
deserializes the blob, the property setters fire — and `ObjectDataProvider`
invokes the method.

The chain, conceptually:

```
attacker-controlled serialized data
  -> deserializer rebuilds an ObjectDataProvider
  -> its MethodName + MethodParameters are set
  -> the named method runs (e.g. Process.Start("cmd.exe", "/c calc"))
```

This is the gadget that `ysoserial.net` ships as its `ObjectDataProvider`
chain (often wrapped in `ExpandedWrapper` and a serializer-specific outer type).
It is popular because it is self-contained: it does not need the target app to
have any particular logic, only an unsafe deserializer and the WPF assemblies on
the classpath.

## The root cause

The gadget is not a bug in `ObjectDataProvider`. The bug is deserializing
untrusted data with a serializer that can instantiate arbitrary types and run
setters. `ObjectDataProvider` is just a convenient, always-available way to reach
a method call once that door is open. Remove the unsafe deserialization and the
gadget has nothing to stand on.

## Defense

### Do not use type-permissive serializers on untrusted data

`BinaryFormatter` is obsolete and unsafe by design; Microsoft recommends against
it and has disabled it by default in modern .NET. Do not feed attacker-reachable
data to it, `NetDataContractSerializer`, `SoapFormatter`, or
`LosFormatter`/`ObjectStateFormatter` without strong controls.

### Prefer serializers that only carry data

`System.Text.Json` and a correctly configured `DataContractSerializer` or
`XmlSerializer` with fixed expected types move values, not arbitrary types. Use
`System.Text.Json` for new work.

### If you must use a flexible serializer, bind the types

- Use a strict `SerializationBinder` that allowlists the exact expected types and
  rejects everything else (including `ObjectDataProvider`, `Process`,
  `ExpandedWrapper`).
- In Json.NET, never use `TypeNameHandling` other than `None` on untrusted input;
  `Auto`/`All` reintroduce the same gadget surface.

### Contain and detect

- Run the process with least privilege.
- Watch for deserialization endpoints spawning child processes.
- Keep dependencies patched; new gadget chains appear regularly.

## Takeaway

`ObjectDataProvider` is a legitimate WPF feature whose "call a method with these
arguments" design makes it an ideal deserialization gadget. The lesson is not
"avoid this class" — it is "never deserialize untrusted data with a serializer
that can build arbitrary types." Lock the types down and the gadget never gets to
run.

## References

- Microsoft — BinaryFormatter security guide / obsoletion
- ysoserial.net — ObjectDataProvider gadget
- OWASP — Deserialization Cheat Sheet
