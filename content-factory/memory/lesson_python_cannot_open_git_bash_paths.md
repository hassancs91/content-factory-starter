---
name: lesson_python_cannot_open_git_bash_paths
description: Windows Python cannot open a Git Bash path like /d/repos/...; hand it the native path from `pwd -W`, above all once MSYS_NO_PATHCONV=1 is set.
---

# Python can't open `/d/...` paths from Git Bash

**What happened (Windows + Git Bash):** the boot probe
built its summary path from `$(pwd)`, which in Git Bash is `/d/projects/your-site/...`, and
passed it to `python` to write a JSON file. Two runs ended the same way, after every
measurement had already been taken:

```
FileNotFoundError: [Errno 2] No such file or directory: '/d/projects/your-site/content-lab/<slug>/evidence/probe-00-boot.json'
```

Windows Python is a native program and does not know MSYS paths. Git Bash normally rewrites
a path-looking argument for a native program (`/d/repos` arrives as `D:/repos`), but only
when the whole argument looks like a path, and not at all with `MSYS_NO_PATHCONV=1` set.
This script had set it for docker (see [[lesson_msys_path_conversion]]), so the conversion
that would have saved it was switched off.

**Rule:** hand Python, and any other native Windows program, a native path. `pwd -W` prints
`D:/repos/...` in Git Bash. A line that also works on Linux and macOS:

```bash
HERE_NATIVE="$(cd "$HERE" && (pwd -W 2>/dev/null || pwd))"
```

Use it for every path a native program opens or writes. A path inside a `python -c` string
or a here-doc is never converted, with or without the variable.
