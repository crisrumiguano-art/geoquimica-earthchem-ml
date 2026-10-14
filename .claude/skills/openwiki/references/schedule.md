# OpenWiki: schedule automatic updates

Help the user keep the wiki fresh automatically by running `/openwiki:update` on a schedule. Every
option here is **keyless** — Claude Code does the work under the plan the user already pays for.

**Critical safety rule:** for any scheduled `claude -p` invocation, **never use `--bare`**. Bare
mode skips OAuth and demands `ANTHROPIC_API_KEY`, which silently bills API rates instead of using
the subscription. Always use a normal (non-bare) `claude -p "/openwiki:update"`.

## Step 1 — pick a mechanism

Use AskUserQuestion to let the user choose, explaining the tradeoffs:

| Option | Durable? | Needs machine on | Notes |
| :-- | :-- | :-- | :-- |
| **Cloud Routine** (`/schedule`) | Yes | No | Runs on Anthropic infra under the user's plan. Min interval 1h. Fresh clone → the routine must commit & push the updated `openwiki/`. Best "daily at a set time, unattended." |
| **Desktop scheduled task** | Yes | Yes | Runs locally on the user's machine via `claude -p "/openwiki:update"` (non-bare) in the repo. Good when it needs local files. |
| **In-session `/loop` / CronCreate** | No — expires in 7 days | Yes + open session | Quick and fully keyless in the current session, but session-scoped and auto-expires after 7 days. Good for a trial, not set-and-forget. |
| **OpenWiki GitHub Action** | Yes (CI) | No | Only for users already running the OpenWiki CLI in CI. **Not keyless** — CI needs a provider API secret. Mention only if they ask. |

Also ask for the time (default: daily 09:00 local). Note cron uses **local timezone** and adds
jitter, so times like `3 9 * * *` fire more predictably than `0 9 * * *`.

## Step 2 — set up the chosen option

- **In-session (CronCreate):** create a recurring task with a daily cron expression (e.g.
  `3 9 * * *`) whose prompt is `/openwiki:update`. Confirm the job id, and clearly warn the user it
  runs only while this session is open and idle, and expires after 7 days (recreate to extend).
- **Cloud Routine:** guide the user to run the `/schedule` skill to create a routine that runs
  `/openwiki:update` on the repo, then commits and pushes the changed `openwiki/`. Explain it runs
  unattended on their plan.
- **Desktop scheduled task:** guide the user to create a daily OS/desktop task running
  `claude -p "/openwiki:update"` (non-bare) from the repo directory, with appropriate
  `--permission-mode`/`--allowedTools` so it can edit files and run git without prompting.

## Step 3 — confirm

Summarize what was scheduled: mechanism, cadence, whether it's durable, and how to change or cancel
it (for in-session tasks, list/cancel via the cron tools or `Esc`). Reiterate the no-`--bare` rule
for any subprocess form.
