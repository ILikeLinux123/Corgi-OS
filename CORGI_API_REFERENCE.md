# Corgi OS — `corgi` Object Reference

Every command file is loaded and run like this by the kernel:

```python
exec(source, program)
program["run"](self, args)   # self = the Kernel instance = "corgi"
```

So inside any `commands/*.py` file, `corgi` **is the running `Kernel` instance**.
Anything the `Kernel` class has, you can call from a command. This doc lists
literally everything currently on it, plus copy-pasteable patterns for the
stuff you'll want to do 95% of the time (read/write files, walk directories,
print output, check permissions, etc).

> Written against Corgi OS Kernel `0.1.4`.

---

## Table of Contents

1. [State attributes](#1-state-attributes)
2. [Filesystem methods](#2-filesystem-methods)
3. [Output / messaging methods](#3-output--messaging-methods)
4. [Info methods](#4-info-methods)
5. [Command execution](#5-command-execution)
6. [Startup system](#6-startup-system)
7. [Panic](#7-panic-currently-buggy)
8. [Common recipes](#8-common-recipes)
9. [Full minimal command template](#9-full-minimal-command-template)

---

## 1. State attributes

These are plain values sitting on the kernel object. Read them directly,
no `()` needed.

### `corgi.fs`
**Type:** `dict`
The entire filesystem. Folders are dicts, files are strings. The very top
level always has one key, `"root"`.

```python
corgi.fs["root"]["home"]  # the home folder dict
```

### `corgi.cwd`
**Type:** `list[str]`
The current directory, as a list of keys from `corgi.fs` down to where you
are. e.g. `["root", "home", "luke"]` means you're in
`corgi.fs["root"]["home"]["luke"]`.

```python
print(corgi.cwd)          # ['root', 'home', 'luke']
corgi.cwd.append("docs")  # "cd" into docs (only if it exists as a folder!)
corgi.cwd.pop()            # go up one level ("cd ..")
```

⚠️ Mutating `cwd` directly doesn't check that the folder exists — that's
why `cd.py` always validates first. Prefer `resolve_path()` + a `KeyError`
check (see [Common recipes](#8-common-recipes)) instead of hand-editing this.

### `corgi.user`
**Type:** `dict | None`
The currently logged-in user's record, or `None` if nobody's logged in.
Typical shape (see `sudo.py` / `autologin.py`):

```python
{
    "username": "luke",
    "password": "<hashed>",
    "admin": True,
    "autologin": False,
}
```

```python
if corgi.user is None:
    print("not logged in")
else:
    print(corgi.user["username"])
    print(corgi.user.get("admin", False))
```

### `corgi.logger`
**Type:** `Logger` instance (from `logger.py`)
Every `info` / `success` / `warning` / `error` call on the kernel also logs
here automatically — you basically never touch this directly, just use
`corgi.info(...)` etc. (see [section 3](#3-output--messaging-methods)).

### `corgi.running`
**Type:** `bool`
The kernel's main-loop flag. Setting this to `False` is *supposed* to stop
the OS, though right now `exit.py` calls `sys.exit()` instead (which fires
first, so `corgi.running = False` never actually runs — worth knowing if
you're building your own shutdown command).

```python
corgi.running = False
```

### `corgi.start_time`
**Type:** `float` (unix timestamp)
Set once at boot in `__init__`. Used internally by `uptime()`. You'd only
read this if you want to compute your own custom duration.

### `corgi.boot_time`
**Type:** `datetime`
Also set at boot. Handy for a "system has been up since ___" style command.

```python
print(f"Booted at {corgi.boot_time.strftime('%H:%M:%S')}")
```

### `corgi.services`
**Type:** `dict`
Currently initialized empty (`{}`) and nothing writes to it yet — it's a
placeholder for a future service-registry system. Safe to use as a spot to
stash long-lived state for your own background-ish features if you want,
e.g. `corgi.services["treat_counter"] = 0`. Just know nothing currently
reads or persists it automatically.

### `corgi.VERSION`
**Type:** `str`, class attribute (so also `Kernel.VERSION`)
Currently `"0.1.4"`.

```python
print(f"Running Corgi OS {corgi.VERSION}")
```

### `corgi.username`
**Type:** `str`, class attribute, currently unused (`""`, never set anywhere
else in the kernel). `corgi.user["username"]` is the one that's actually
populated — don't confuse the two.

---

## 2. Filesystem methods

### `corgi.get_current_dir()`
**Returns:** `dict`
The single most-used call in the whole codebase. Walks `corgi.fs` using
`corgi.cwd` and hands you back the dict for **wherever you currently are**.

```python
folder = corgi.get_current_dir()
folder["notes.txt"] = "hello"   # create/overwrite a file right here
del folder["notes.txt"]         # delete it
"notes.txt" in folder           # check existence
```

This only ever gives you the *current* folder. For arbitrary paths, see
the `resolve_path` recipe below.

### `corgi.path()`
**Returns:** `str`
The current directory as a human-readable string, built from `corgi.cwd`.

```python
print(corgi.path())   # "/root/home/luke"
```

### `corgi.save_filesystem(fs=None)`
Writes `corgi.fs` (or the `fs` you pass in) to `corgi_fs.json` on disk.
**Called automatically after every command** in `execute()`, so you almost
never need to call this yourself — but it's there if you're doing something
unusual (e.g. writing to `corgi.fs` from a background/startup script rather
than from inside a normal command).

```python
corgi.save_filesystem()
```

Note: this method is defined **twice** in your kernel (once near the top,
once further down) — they're identical, so it's harmless, just a
duplicate worth cleaning up eventually.

### `corgi.load_filesystem()`
**Returns:** `dict`
Loads `corgi_fs.json` off disk, or builds+saves a fresh default filesystem
if the file's missing/corrupt/`FACTORY_RESET` is on. Called once, in
`__init__`. You'd basically never call this yourself mid-session.

### `corgi.default_filesystem()`
**Returns:** `dict`
Builds the "factory" filesystem structure from scratch — `root/SYSTEM/commands/...`
etc — entirely in memory, without touching disk. This is where **all your
built-in commands are defined as strings**. Add new commands by editing
the `"commands": { ... }` dict inside this method.

### `corgi.merge_filesystem(old, new)`
**Returns:** `dict`
Recursively merges `new` into `old`, in place:
- new folders get added if missing
- existing folders get merged recursively
- files get overwritten if the same name shows up in `new`

This is the engine behind `refresh`. You could reuse it yourself if you
ever build an "install a package" style command that needs to merge a
downloaded folder tree into the existing filesystem.

```python
corgi.fs["root"] = corgi.merge_filesystem(
    corgi.fs["root"],
    some_new_folder_tree,
)
```

### `corgi.refresh_filesystem()`
The `refresh` command's implementation. Rebuilds the default filesystem and
merges it into the current one, then saves. **This is your friend whenever
you add new built-in commands to `default_filesystem()`** — just run
`refresh` in the OS instead of deleting your save file.

```python
corgi.refresh_filesystem()
```

---

## 3. Output / messaging methods

Always prefer these over bare `print()` for status messages — they also
write to the log file via `corgi.logger`, and they're color/prefix coded
in the terminal (`terminal.py`).

```python
corgi.info("Starting up...")      # neutral status
corgi.success("Done!")            # good outcome
corgi.warning("Disk getting full") # non-fatal concern
corgi.error("File not found")     # failure
```

Plain `print()` is still totally fine for actual command *output* (file
contents, command results, ASCII art, etc) — use `info/success/warning/error`
specifically for **system-status style messages**, the same way your
built-in commands do (e.g. `git.py`'s `[ OK ] Downloading...` uses plain
`print`, while the kernel's own startup sequence uses `self.info(...)`).

---

## 4. Info methods

### `corgi.uptime()`
**Returns:** `str`, e.g. `"42s"`.

```python
print(f"Up for {corgi.uptime()}")
```

### `corgi.about()`
Prints a small built-in banner (OS name, kernel version, uptime). No
return value — it just `print()`s directly.

```python
corgi.about()
```

---

## 5. Command execution

### `corgi.execute(command)`
**Parameter:** `command` — a full command string, e.g. `"ls -la"`
Runs another command exactly as if the user had typed it: splits off the
command name, looks it up in `root/SYSTEM/commands`, `exec`s it, and saves
the filesystem afterward. Used by `sudo.py` to re-run a command after a
password check.

```python
def run(corgi, args):
    # run another command from inside your own command
    corgi.execute("neofetch")
```

⚠️ Careful with recursion — if your command calls `corgi.execute(name of
itself)` you'll get infinite recursion.

---

## 6. Startup system

You won't call these from a normal command, but they're worth knowing
about if you're building startup scripts.

### `corgi.run_system_startup()`
Called once automatically in `__init__`. Executes every `.py` file found in
`corgi.fs["root"]["SYSTEM"]["STARTUP"]`, calling its `run(corgi)` function
if it defines one (note: **one argument**, not `run(corgi, args)` like
normal commands).

### `corgi.run_user_startup()`
Not currently called automatically anywhere — you'd need to call it
yourself (e.g. from a system startup script) if you want `.pystart` files
to run. Recursively searches the whole filesystem for any file ending in
`.pystart` and runs it the same way as system startup scripts.

### `corgi.find_pystart(folder, path="")`
**Returns:** `list[tuple[str, str]]` — `(path, source)` pairs.
The recursive search helper behind `run_user_startup`. You could reuse this
pattern for your own "find all files with X extension" style command (see
`find.py` in the earlier command pack for a similar recursive walk).

---

## 7. Panic (currently buggy)

### `corgi.panic(reason)`
Intended to be your kernel-panic / fatal-error screen. Heads up before you
build anything that calls this: as currently written it references
`self.kernel` (doesn't exist on `Kernel`) and calls a bare `corgi.panic()`
inside itself (not `self.panic()`, and `corgi` isn't defined in that
method's scope) — so calling it will currently raise its own exception
instead of cleanly panicking. Worth fixing before you rely on it:

```python
def panic(self, reason):
    self.running = False
    print("="*45)
    print(" CORGI OS KERNEL PANIC")
    print("="*45)
    print()
    print("Reason:")
    print(reason)
    self.logger.log(reason, "PANIC")
    print()
    print("System halted.")
```
(drop the `self.kernel` check and the stray `corgi.panic()` call, or replace
them with whatever the real reboot-to-bootloader logic should be)

---

## 8. Common recipes

### Read a file
```python
folder = corgi.get_current_dir()
if "notes.txt" in folder and isinstance(folder["notes.txt"], str):
    print(folder["notes.txt"])
```

### Write / create a file
```python
folder = corgi.get_current_dir()
folder["notes.txt"] = "some content"
```

### Append to a file
```python
folder = corgi.get_current_dir()
folder["notes.txt"] = folder.get("notes.txt", "") + "\nmore content"
```

### Delete a file or folder
```python
folder = corgi.get_current_dir()
if "notes.txt" in folder:
    del folder["notes.txt"]
```

### Make a new folder
```python
folder = corgi.get_current_dir()
folder["my_folder"] = {}
```

### Check file vs folder
```python
item = folder["something"]
if isinstance(item, dict):
    print("it's a folder")
else:
    print("it's a file")
```

### List everything in the current folder
```python
for name in corgi.get_current_dir():
    print(name)
```

### Resolve an arbitrary path string (absolute, relative, or `~`)

This is the pattern from `cd.py` / `ls.py` / `git.py` — reuse it any time
you want a command to work on a path someone typed, not just the current
folder:

```python
def resolve_path(corgi, path):
    if path == "~":
        return ["root", "home", corgi.user["username"]]
    if path == "/":
        return ["root"]
    if path.startswith("/"):
        parts = path.strip("/").split("/")
        if parts[0] == "root":
            parts.pop(0)
        return ["root"] + parts
    return corgi.cwd + path.split("/")


def run(corgi, args):
    path = resolve_path(corgi, args.strip())
    folder = corgi.fs
    try:
        for part in path:
            folder = folder[part]
    except KeyError:
        print("not found")
        return
    # `folder` is now whatever's at that path (dict or str)
```

### Recursively walk every file/folder from here down
```python
def walk(node, path=""):
    for name, item in node.items():
        current = path + "/" + name
        if isinstance(item, dict):
            walk(item, current)
        else:
            print(current)

walk(corgi.get_current_dir(), corgi.path())
```

### Check if the current user is an admin
```python
if corgi.user and corgi.user.get("admin", False):
    print("you're an admin")
else:
    print("nope")
```

### Print system-style status messages
```python
corgi.info("Doing a thing...")
corgi.success("Thing done!")
corgi.warning("Thing was a little weird")
corgi.error("Thing failed")
```

### Run another command from inside yours
```python
corgi.execute("neofetch")
```

### Parse args (see previous message for the full args cheat-sheet)
```python
parts = args.split()                # ["a", "b", "c"]
name, rest = args.split(" ", 1) if " " in args else (args, "")
n = int(parts[1]) if len(parts) > 1 else 10   # optional value w/ default
```

---

## 9. Full minimal command template

Copy-paste starting point for any new command:

```python
def run(corgi, args):

    target = args.strip()

    if not target:
        print("usage: mycommand <thing>")
        return

    folder = corgi.get_current_dir()

    if target not in folder:
        corgi.error(f"mycommand: '{target}' not found")
        return

    # ... do the thing ...

    corgi.success(f"Done with '{target}' 🐶")
```

Drop it into `default_filesystem()` under `"commands"` as `"mycommand.py"`,
then run `refresh` in Corgi OS to load it in.

---

## 10. Coloring text

Terminal color codes aren't on the `corgi` object — they're just plain ANSI
escape codes, so any command can use them directly with regular `print()`.

```python
class C:
    RESET  = "\033[0m"
    RED    = "\033[31m"
    GREEN  = "\033[32m"
    YELLOW = "\033[33m"
    BLUE   = "\033[34m"
    PINK   = "\033[35m"
    CYAN   = "\033[36m"
    BOLD   = "\033[1m"

print(f"{C.GREEN}Success!{C.RESET}")
print(f"{C.RED}{C.BOLD}Error!{C.RESET}")
```

Always end colored text with `C.RESET`, or everything printed after it
stays colored too. This is the same trick `terminal.py` almost certainly
uses under the hood for `info`/`success`/`warning`/`error` — worth peeking
at that file if you want your custom colors to match those exactly.
