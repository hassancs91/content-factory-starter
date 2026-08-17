---
name: lesson_path_scoped_commit_ignores_the_index
description: "`git commit -- <paths>` commits the WORKING TREE for those paths and silently discards your hunk-scoped index — the one technique the ship rule tells you to use."
---

# `git commit -- <paths>` throws away your staged hunks

SKILL.md rule 5 says: never bare `git commit`, always name paths. SKILL.md hard rules also
say path-scoping is not enough on an already-dirty shared file, so hunk-scope the index
first. **Doing both at once quietly does the wrong thing.**

On the `secure-coolify-vps` ship, `apps/guides/registry.py` was already dirty with another
session's in-flight guide entry. The index was carefully rebuilt to contain HEAD plus only
my entry, verified with `git diff --cached`, confirmed clean. Then:

```
git commit -F- -- templates/... static/... apps/guides/registry.py ...
```

When you give `git commit` pathspecs, it commits **the working tree contents of those
paths**, ignoring whatever you staged. So the commit contained the other session's registry
entry, pointing at a template that was still untracked: a live 404 on deploy. Their
`MEMORY.md` index line came along too, pointing at an uncommitted file.

**The rule:** you can hunk-scope the index, or you can path-scope the commit. Never both.

When a shared file is dirty:

1. Rebuild the file to `HEAD` + your changes only, `git add` it.
2. Confirm with `git diff --cached --name-only` that the index holds exactly your files.
3. `git commit` with **no pathspec**, so the index is what lands.
4. Restore the working tree so the other session keeps its uncommitted work.

When no shared file is dirty, path-scoping alone is fine and simpler.

**And verify the COMMITTED tree, not the working tree you just tested.** This was caught
only by `git show HEAD:<file>` after the fact. Worth making a standing ship assertion:

```bash
# every slug in the COMMITTED registry must have a COMMITTED page file
for slug in $(git show HEAD:<registry-file> | <extract slugs>); do
  git cat-file -e HEAD:<pages-dir>/$slug.<ext> || echo "MISSING PAGE: $slug"
done
```

Every registry slug must have a committed page. Fixing it afterwards means
`git commit --amend` with a rebuilt index, which is fine, but only if you notice.

See [[lesson_no_shared_mutable_files]] for why the LEDGER was made generated in the first
place: the same class of problem, solved by removing the shared file instead of guarding it.
`registry.py` cannot be removed that way, so it needs this discipline.
