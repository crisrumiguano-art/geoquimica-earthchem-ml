---
name: openwiki
description: Generate, update, query, or schedule OpenWiki-format documentation for this repository. Trigger when the user mentions /openwiki, /openwiki:generate, /openwiki:update, /openwiki:ask, or /openwiki:schedule.
---

# OpenWiki

This skill helps you generate, update, query, or schedule automatic updates for an [OpenWiki](https://github.com/langchain-ai/openwiki)-format documentation wiki for the current repository, using the agent's own inference without requiring any external API key.

## Subcommand Routing

When this skill triggers, identify which action the user is requesting (based on the command name or natural language request) and immediately open and follow the corresponding instruction file in the `references/` directory:

1. **Generate Wiki** (`/openwiki:generate`): Build a first-pass wiki (max ~8 pages). 
   - *Instruction file:* [references/generate.md](generate.md)
   
2. **Update Wiki** (`/openwiki:update`): Surgically refresh the wiki based on git changes since the last run.
   - *Instruction file:* [references/update.md](2_Notes/Tech/Design_UI-UX_Webpage/Documentacion_Graphify-Openwiki/skills/openwiki/references/update.md)
   
3. **Ask Question** (`/openwiki:ask <question>`): Answer a question using the maintained wiki.
   - *Instruction file:* [references/ask.md](ask.md)
   
4. **Schedule Updates** (`/openwiki:schedule`): Set up automatic (e.g. daily) updates.
   - *Instruction file:* [references/schedule.md](schedule.md)

## Reference Material

* For the layout, metadata schema (`.last-update.json`), the exact agent reference block, and security rules, consult [references/openwiki-format.md](openwiki-format.md).
