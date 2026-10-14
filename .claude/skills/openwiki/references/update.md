# OpenWiki: update

Refresh the existing `openwiki/` wiki so it reflects recent source changes — doing the work
**yourself** with your own tools (Read, Grep, Glob, Edit, Bash for git). Do **not** call the
`openwiki` CLI and do **not** require any API key.

**First, read the format spec:** `references/openwiki-format.md` (layout,
metadata, exact AGENTS.md/CLAUDE.md block, principles, security). Updates must stay compatible with
the OpenWiki CLI.

## Steps

1. **Locate the wiki.** If `openwiki/` doesn't exist yet, tell the user to run `/openwiki:generate`
   first and stop.
2. **Read prior metadata.** Read `openwiki/.last-update.json`. Prefer its `gitHead` as the baseline;
   fall back to `updatedAt` if no `gitHead`.
3. **Find what changed.** Use git: `git diff <gitHead>..HEAD --stat`, then targeted diffs on the
   high-signal changed files. Also `git status`/`git diff` for uncommitted changes touching docs or
   important source. If shell/git is unavailable, infer from file timestamps and source inspection.
4. **Build a docs-impact plan** (do not write it to disk unless helpful): for each meaningful source
   change → which wiki page is affected → what edit is needed → why. If a page can't be tied to a
   relevant change, do not touch it.
5. **Edit surgically.**
   - Only edit pages made inaccurate/incomplete/misleading by the changes.
   - Prefer replacing a stale sentence over adding paragraphs. Preserve accurate structure/wording.
   - **No formatting-only edits.** Don't reformat tables, normalize blank lines, reorder lists, or
     polish wording unless you're already changing that content for accuracy.
   - Don't refresh Source Map / git-evidence / generic "things to watch" sections unless they are
     materially wrong now.
   - **Soft diff budget:** if fewer than ~5 source files changed, edit at most 1–2 pages. Avoid
     touching `quickstart.md` unless top-level product behavior, setup, or navigation changed. If
     you think >3 pages need edits, reconsider carefully first.
6. **Check the reference section.** Ensure the top-level `AGENTS.md`/`CLAUDE.md` OpenWiki section is
   present and current (see the format spec). Refresh only if missing or semantically stale.
7. **No-op is allowed.** If nothing relevant changed and the wiki is already accurate, make no edits
   at all — leave every file, including `openwiki/.last-update.json`, untouched — and tell the user
   the wiki is already current. (Upstream only records metadata when content actually changes.)
8. **Write metadata (only if you changed wiki content).** Update `openwiki/.last-update.json` with
   `command: "update"`, `updatedAt` from `date -u +%Y-%m-%dT%H:%M:%S.000Z` (run it — don't guess),
   the current `git rev-parse HEAD`, and your `model`.
9. **Report** which pages changed and why, or that the wiki was already current.

Keep everything under `openwiki/` except the top-level agent instruction files. Never document
secrets or read `.env` files.
