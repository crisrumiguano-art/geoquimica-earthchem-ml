# OpenWiki: generate

Build a first-pass OpenWiki-format wiki for the current repository, doing the work **yourself** with
your own tools (Read, Grep, Glob, Write, Edit, Bash for git). Do **not** call the `openwiki` CLI and
do **not** require any API key — you are the inference engine, which is what the user already pays
for.

**First, read the format spec:** `references/openwiki-format.md`. It is the
source of truth for layout, the metadata file, the exact AGENTS.md/CLAUDE.md reference block,
writing principles, section rules, and security rules. Follow it precisely so output is compatible
with the OpenWiki CLI.

## Steps

1. **Check for an existing wiki.** If `openwiki/` already exists with real content, tell the user
   and switch to the update behavior (`/openwiki:update`) instead of overwriting. Never clobber an
   existing wiki.
2. **Confirm repo + git context.** Determine the repo root. Run `git rev-parse HEAD` (capture for
   metadata) and skim recent history (`git log --oneline -20`) for high-signal context. If it's not
   a git repo, proceed and use an empty `gitHead`.
3. **Inventory (targeted discovery).** Identify existing docs, entrypoints, package/config files,
   major domain folders, routing, data/schema files, tests, and operational scripts. Use
   `rg --files` with excludes (`.git`, `node_modules`, `dist`, `build`, caches, `openwiki/`) and
   short targeted reads. Do not read every file. For a large repo with several independent domains,
   you may dispatch 1–2 read-only Explore subagents to summarize domains in parallel — they must
   only inspect and report, never write.
4. **Plan.** Write a temporary `openwiki/_plan.md` listing intended pages, the source evidence for
   each, and open questions. You will delete it in step 7.
5. **Write the wiki.** Create `openwiki/quickstart.md` first (overview + links to every section),
   then the smallest set of linked section pages that explains the repo well. Respect the init cap
   (~8 pages max; tiny repos: quickstart + 1–2 pages). Ground every claim in evidence with inline
   source references. Capture both technical detail and business/product logic, and change-oriented
   guidance for future agents.
6. **Wire up agent instruction files.** Add the exact OpenWiki reference section (see the format
   spec) to top-level `AGENTS.md`/`CLAUDE.md` per the rules there.
7. **Finalize.** Delete `openwiki/_plan.md`. Review the `openwiki/` tree and merge/remove any thin
   or single-file-directory pages.
8. **Write metadata.** Create `openwiki/.last-update.json` with `command: "init"`, `updatedAt` from
   `date -u +%Y-%m-%dT%H:%M:%S.000Z` (run it — don't guess the time), the `gitHead` from step 2, and
   `model` set to your Claude Code model id (or `"claude-code"`).
9. **Report.** Summarize the pages created and the AGENTS.md/CLAUDE.md changes. Do not paste
   subagent notes; give a clean summary and any important caveats.

Keep everything under `openwiki/` except the top-level agent instruction files. Never document
secrets or read `.env` files.
