# Five Windows harness traps that each cost a failed experiment run

All hit on `react-native-docs-polish` (2026-07-31) inside one afternoon. None are about
the product under test; all of them look like the product failing.

## 1. An em dash in a `.ps1` breaks the parser, and the error points somewhere else

Write tools emit UTF-8 **without BOM**. Windows PowerShell 5.1 then decodes the file as
cp1252, so `—` (E2 80 94) becomes `â€"` — and that last byte is U+201D, a **right double
quote**, which the PS parser treats as a real string delimiter. Every string after it
shifts by one, and you get:

```
Missing expression after ','.
Unexpected token '7:N1' in expression or statement.
The string is missing the terminator: ".
```

pointing at a line 70 lines below the actual em dash.

**Rule: keep every `.ps1` pure ASCII.** Check with `grep -nP '[^\x00-\x7F]' file.ps1` (note: git-bash grep needs
a UTF-8 locale for `-P`; `python -c` is the portable check).

## 2. `2>&1` on a native exe is a terminating error under `$ErrorActionPreference='Stop'`

PS 5.1 wraps each stderr line from a native binary in a `NativeCommandError`
`ErrorRecord`. `git clone` writes its ordinary progress ("Cloning into...") to stderr,
so the very first command of the run dies with `RemoteException`.

**Rule: redirect native stderr to a file (`2> path`) and gate on `$LASTEXITCODE`.**
Never pipe a native exe through `2>&1` in a script that stops on error.

## 3. `Start-Process -FilePath 'pnpm'` cannot work

`pnpm`, `npm`, `npx` are `.cmd`/`.ps1` shims, not executables:
`%1 is not a valid Win32 application`. Launch through
`Start-Process cmd.exe -ArgumentList '/c','pnpm ...'`.

## 4. Background servers die when the harness reaps the launching shell

A dev server started via `Start-Process` from a script that then exits gets torn down
with its parent, and the symptom arrives much later as a connection reset mid-capture.
Start long-lived servers as **harness-tracked background tasks** instead, so they
outlive the turn.

Related: `tsx watch` leaves orphaned **`esbuild.exe`** workers holding the scratch
directory open. `Remove-Item -Recurse` then fails with "used by another process" and no
node process is listening on the port. Find them with
`Get-CimInstance Win32_Process | Where CommandLine -like '*<scratch>*'`, which matches
by command line rather than by port, and kill those before teardown.

## 5. `sed -i` in git-bash rewrites a droplet script to CRLF, and bash dies far from the cause

Hit on `self-host-supabase` (2026-08-11). Scripts written by the Write tool are LF and
run fine on the droplet — until you touch one with `sed -i` from git-bash on Windows,
which rewrites the WHOLE file with CRLF. Uploaded to Linux, `#!/usr/bin/env bash\r`
plus a `\r` before a continuation `|` produce `syntax error near unexpected token '|'`
lines away from anything you edited; run detached with a bare `touch done` wrapper and the
sentinel still fires, so the failure looks like a silent no-op (empty log, done-file
present).

**Rule: upload droplet scripts through `tr -d '\r'`** (`... -- 'tr -d "\r" > /root/x.sh'
< local.sh`) and `bash -n` on the box before launching detached. Same disease as writing a patch file
in text mode on Windows: the tooling silently rewrites your line endings and the failure
surfaces somewhere else entirely.

## Why this belongs in memory

Each one presents as "the product is broken" or "the clone is corrupt". Three of the
four produced a red run that had nothing to do with the thing being tested. Recognising
them costs seconds; rediscovering them costs a stage.
