# OpenWiki format specification (shared reference)

This file is the single source of truth for the on-disk format the `openwiki` skills produce.
It is distilled from the upstream OpenWiki agent prompt (`langchain-ai/openwiki`,
`src/agent/prompt.ts` / `src/constants.ts`) so that wikis produced here are **byte-compatible**
with wikis produced by the OpenWiki CLI. Keep this file faithful to upstream.

## On-disk layout

- Wiki lives entirely under **`openwiki/`** at the repository root.
- **`openwiki/quickstart.md`** is the mandatory entrypoint. It must contain a high-level repository
  overview and links to every major section.
- Optional section directories, one per real documentation area, e.g. `architecture/`, `workflows/`,
  `domain/`, `api/`, `data-models/`, `operations/`, `integrations/`, `testing/`.
- **`openwiki/.last-update.json`** — run metadata (see below).
- A temporary **`openwiki/_plan.md`** may be created during a run and **must be deleted** before the
  run finishes. Never leave it behind.

## Metadata file — `openwiki/.last-update.json`

Upstream, the OpenWiki *CLI* writes this after the agent finishes. There is no CLI here, so **the
skill writes it directly**. Exact shape:

```json
{
  "updatedAt": "2026-07-06T12:34:56.000Z",
  "command": "init",
  "gitHead": "<full HEAD commit SHA>",
  "model": "claude-code"
}
```

- `updatedAt`: ISO-8601 timestamp (UTC). **Get the real time from the shell** — run
  `date -u +%Y-%m-%dT%H:%M:%S.000Z` via Bash. Do not guess or use midnight; you do not have a
  reliable wall-clock otherwise.
- `command`: `"init"` for a first/full generation, `"update"` for a maintenance run.
- `gitHead`: output of `git rev-parse HEAD` at write time (empty string if not a git repo).
- `model`: the Claude Code model doing the work (e.g. `claude-opus-4-8`); use `"claude-code"` if
  the exact id is unknown. This records that a Claude Code run — not an API-key CLI run — produced
  the update, while staying compatible with the OpenWiki CLI's field set.

## Root agent instruction files (`AGENTS.md` / `CLAUDE.md`)

Ensure the repository's **top-level** `AGENTS.md` and/or `CLAUDE.md` reference the wiki. Rules
(verbatim intent from upstream):

- Only touch top-level `/AGENTS.md` and `/CLAUDE.md`. Never edit nested ones.
- If one or both exist, add or update the OpenWiki reference section in them. If both exist, put the
  same section in both.
- If neither exists, create top-level `AGENTS.md` containing only the reference section.
- On update runs, refresh the section only if it is missing or semantically stale. Preserve all
  surrounding content. Replace an existing section in place — never duplicate it. Do not make
  formatting-only edits.

Use this **exact** section every time (do not reword — this is what upstream dedupes against):

```markdown
## OpenWiki

This repository has documentation located in the /openwiki directory.

Start here:
- [OpenWiki quickstart](openwiki/quickstart.md)

OpenWiki includes repository overview, architecture notes, workflows, domain concepts, operations, integrations, testing guidance, and source maps.

When working in this repository, read the OpenWiki quickstart first, then follow its links to the relevant architecture, workflow, domain, operation, and testing notes.
```

## Writing principles

- **Ground every important claim** in source files, existing docs, or git evidence you inspected.
  Never invent files, modules, APIs, business rules, or behavior.
- **Targeted discovery, not exhaustive reads.** Inspect the repo tree, package/config files,
  README-style docs, entrypoints, routing, schema/data files, and representative files per domain.
  Prefer `rg --files` / grep / glob and short targeted reads over full-file reads. Never glob
  `**/*` from the root; exclude `.git`, `node_modules`, `dist`, `build`, caches, and `openwiki/`.
- **Use git for the "why."** `git log`/`show`/`blame` selectively on high-signal files; focus on
  recent, high-signal history. Do not embed persistent commit-hash lists unless a specific historical
  decision matters.
- **One canonical home per concept**; link to it from elsewhere instead of duplicating.
- **Inline source references** where they help a reader verify or continue, e.g. ``(see
  `src/server/auth.ts` lines 42–58)``. Source Map sections are optional — add only when they
  materially aid navigation.
- **Explain why code exists**, capture business/product logic, and add change-oriented guidance for
  future agents: where to start, what to watch for, which tests/checks matter for each area.
- **Concise and maintainable.** Organize like human docs, not a file inventory.

## Section quality rules

- Don't create a directory unless it's a real documentation area. Avoid one-file directories unless
  the page is substantial and likely to grow. Prefer headings in broader pages over many tiny dirs.
- Avoid thin/stub pages — merge them into `quickstart.md` or a broader page.
- **Init cap:** at most ~8 pages unless the repo is clearly large. For small repos (~≤10 primary
  source files), prefer `quickstart.md` plus at most 1–2 supporting pages.
- Before finishing, review the `openwiki/` tree and merge/move/remove low-value pages.

## Security & privacy

- Never read or document secret values, credentials, private keys, tokens, or `.env` files.
  `.env.example`/sample configs are OK only if they contain placeholders.
- If a secret-bearing file seems relevant, document only that such config exists and where
  non-sensitive setup belongs.
- Keep all documentation under `openwiki/`. Do not modify source outside `openwiki/`, except the
  top-level `AGENTS.md`/`CLAUDE.md` reference section.

## Interoperability contract

Because this format matches the OpenWiki CLI exactly, the two are interchangeable on the same repo:
an existing OpenWiki user can keep their wiki fresh from Claude Code (keyless), and a Claude
Code–generated wiki can later be updated by the CLI. Therefore: **detect an existing `openwiki/` and
continue it — never clobber it.**
