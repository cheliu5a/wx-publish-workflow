---
name: aosp-linux-source
description: Use when looking up AOSP or Linux kernel source code, searching for kernel symbols or Android framework APIs, reading upstream implementation of a system call, driver, or Android service, or verifying upstream code behavior via cs.android.com, elixir.bootlin.com, source.android.com, or android.googlesource.com.
---

# AOSP & Linux Kernel Online Source Browser

Access upstream source code using `web_fetch` against four authoritative sites. No local clone required.

## Site Quick Reference

| Site | Best For | Base URL |
|------|----------|----------|
| cs.android.com | AOSP symbol/text search + file view | `https://cs.android.com` |
| elixir.bootlin.com | Linux kernel symbol cross-ref, multi-version | `https://elixir.bootlin.com` |
| source.android.com | AOSP architecture docs | `https://source.android.com` |
| android.googlesource.com | Browse git repos, raw file download | `https://android.googlesource.com` |

---

## cs.android.com — AOSP Code Search

### Search code
```
https://cs.android.com/search?q=<query>&ss=android
```
Example — find all callers of `lowMemoryKiller`:
```
https://cs.android.com/search?q=lowMemoryKiller&ss=android
```

### View a file
```
https://cs.android.com/android/platform/superproject/+/master:<path-from-root>
```
Example:
```
https://cs.android.com/android/platform/superproject/+/master:frameworks/base/services/core/java/com/android/server/am/ActivityManagerService.java
```

### Tips
- Append `&lang=java` / `&lang=cpp` / `&lang=kotlin` to filter by language.
- Use `symbol:<name>` in the query to restrict to symbol definitions.
- The result page HTML contains `<div class="result">` blocks with file paths and line numbers.

---

## elixir.bootlin.com — Linux Kernel Cross-Reference

### View source file (latest stable)
```
https://elixir.bootlin.com/linux/latest/source/<path>
```
Example:
```
https://elixir.bootlin.com/linux/latest/source/mm/oom_kill.c
```

### View specific kernel version
```
https://elixir.bootlin.com/linux/v6.6/source/<path>
```

### Find all definitions/uses of an identifier
```
https://elixir.bootlin.com/linux/latest/A/ident/<identifier>
```
Example:
```
https://elixir.bootlin.com/linux/latest/A/ident/lowmem_reserve
```

### List available versions
```
https://elixir.bootlin.com/linux/
```

### Tips
- The identifier page lists **defined in**, **referenced in** with file+line links.
- Supports `android-*` and `stable/*` branches too.
- Raw source lines appear in `<code>` blocks; fetch and grep for the relevant function.

---

## source.android.com — AOSP Official Docs

### Direct access
```
https://source.android.com/<section>/<page>
```
Common sections: `devices/tech/perf`, `devices/tech/debug`, `setup/start`, `reference/hal`

Example:
```
https://source.android.com/docs/core/perf
```

---

## android.googlesource.com — Git Repo Browser

### List all AOSP repos
```
https://android.googlesource.com/
```

### Browse a repo tree
```
https://android.googlesource.com/<repo>/+/refs/heads/main/
```
Example:
```
https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/
```

### View raw file content (best for web_fetch)
```
https://android.googlesource.com/<repo>/+/refs/heads/main/<path>?format=TEXT
```
The `?format=TEXT` returns base64-encoded raw content; decode with `base64 -d`.

### View file with syntax highlight
```
https://android.googlesource.com/<repo>/+/refs/heads/main/<path>
```

---

## Common Workflows

### Find a kernel struct definition
1. `web_fetch` → `https://elixir.bootlin.com/linux/latest/A/ident/<struct_name>`
2. Click the **defined in** link to get the file+line.
3. `web_fetch` → the file URL to read the full definition.

### Trace an AOSP Java API
1. `web_fetch` → `https://cs.android.com/search?q=symbol:<MethodName>&ss=android&lang=java`
2. Identify the canonical file path from results.
3. `web_fetch` → the cs.android.com file URL for the full implementation.

### Verify upstream vs vendor diff
1. Fetch upstream via googlesource raw URL.
2. Compare against local vendor file with `diff`.

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Fetching googlesource without `?format=TEXT` for raw content | Add `?format=TEXT`; decode base64 output |
| Using `latest` on elixir for Android-specific kernel patches | Use `android-<version>` branch instead |
| Searching cs.android.com without `&ss=android` | Without `ss=`, results include non-AOSP Google repos |
| Fetching elixir source page and parsing HTML as code | The `<code>` tag wraps the file; extract between tags |
