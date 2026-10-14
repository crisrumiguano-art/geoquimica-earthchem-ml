# OpenWiki: ask

Answer the user's question — **$ARGUMENTS** — using the repository's OpenWiki wiki as the primary
source, instead of re-deriving everything from raw source.

## Steps

1. **Check for a wiki.** If `openwiki/` doesn't exist, say so and offer to run `/openwiki:generate`.
   You can still answer from source, but note the wiki is missing.
2. **Start at the entrypoint.** Read `openwiki/quickstart.md` to orient, then follow its links to
   the relevant section pages. Use Grep across `openwiki/` for the question's key terms to find the
   canonical page for the concept.
3. **Answer from the wiki**, citing the specific wiki page(s) you used. Where the wiki gives inline
   source references (e.g. `src/...:42`), surface them so the user can jump to the code.
4. **Verify only if needed.** If the wiki seems stale or doesn't cover the question, say so, then
   confirm against the actual source before answering — and suggest `/openwiki:update` if you found
   the wiki out of date.

Keep the answer focused and grounded. Prefer the wiki's canonical explanation over guessing.
