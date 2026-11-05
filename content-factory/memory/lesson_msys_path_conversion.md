---
name: lesson_msys_path_conversion
description: Git Bash rewrites an argument that starts with / before a native program sees it (a container path, a bind mount, even a slash command to `claude -p`); MSYS_NO_PATHCONV=1 stops it.
---

# Git Bash rewrites `/paths` before docker or claude sees them

**What happened (Windows + Git Bash):** the run's opening
slash command, sent from Git Bash with `claude -p`, reached Claude Code as
`C:/Program Files/Git/<command> new how to <topic>`. Git Bash saw an argument
starting with `/`, took it for a path, and rewrote it against Git's install folder before
the program ever ran. The clean re-test needed `MSYS_NO_PATHCONV=1`. The probe script in the
same run exported that variable up front, so its docker container paths would not be
rewritten the same way.

What gets rewritten, checked with an argv echo on Git for Windows 2.49:

| Argument to a native program | Arrives as |
|---|---|
| `"/content-factory new how to x"` | `C:/Program Files/Git/content-factory new how to x` |
| `/app/data` (as in `docker exec box ls /app/data`) | `C:/Program Files/Git/app/data` |
| `-w /app` | `C:/Program Files/Git/app` |
| `-v /d/repos/x:/app/data` (a bind mount) | `D:\repos\x;C:\Program Files\Git\app\data` |
| `-v name:/app/data` (a named volume) | unchanged |
| `/d/repos` (a host path) | `D:/repos`, the conversion you want |

**Rule:** in Git Bash, set `MSYS_NO_PATHCONV=1` for any command that hands a native program
a container path, a bind mount, or a slash command: `export` it at the top of a script, or
prefix the one command (`MSYS_NO_PATHCONV=1 claude -p "/content-factory new ..."`). Linux and
macOS ignore it. The price: host paths are no longer converted either, so hand native
programs native paths from `pwd -W`; see [[lesson_python_cannot_open_git_bash_paths]].
