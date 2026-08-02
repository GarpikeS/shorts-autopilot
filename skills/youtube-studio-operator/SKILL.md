---
name: youtube-studio-operator
description: Operate YouTube Studio for validated Shorts through a private authorized Chrome profile. Use when an agent must start muted headless Chrome, connect over CDP, upload or schedule one video, verify visibility and publication time, collect metrics, or update a manifest only after Studio confirmation.
---

# YouTube Studio Operator

Keep browser authorization outside this repository. Work one video at a time
and fail closed when the page state, date, checks, or confirmation is unclear.

## Start Studio

Launch Chrome through the repository script:

```powershell
.\scripts\start-studio-headless.ps1 -ProfilePath C:\private\youtube-profile -Port 9223
```

The launcher must include `--headless=new`, `--mute-audio`,
`--disable-blink-features=AutomationControlled`, and a normal Windows Chrome
user agent without `HeadlessChrome`. Never display a browser window and never
commit the profile.

Connect Playwright to `http://127.0.0.1:9223` with `connect_over_cdp`. Reuse the
authorized context instead of creating a fresh context.

## Upload And Schedule

1. Confirm the media package passed the `shorts-autopilot` skill.
2. Open Studio and verify the expected channel identity before uploading.
3. Upload exactly one video and thumbnail. Set title and description from the
   generated `metadata.json`; do not expose private IDs.
4. Wait for upload and processing checks. Stop on copyright, policy, browser,
   or account warnings.
5. When scheduling, read the selected full date and timezone back from the UI.
   Do not infer the year from a calendar cell alone.
6. Keep at least the configured minimum interval between scheduled items.
7. Submit once, then locate the content row and verify video ID, visibility,
   and date/time.
8. Only after that read-back succeeds, run `shorts-autopilot record`.

Read `references/studio-safety.md` before changing selectors or adding an
automated publication action.

## Metrics And Comments

- Collect metrics only for elapsed checkpoints and leave unavailable values
  empty rather than inventing zeroes.
- Preserve CSV columns by using a CSV parser, not string splitting.
- Classify comments and prepare drafts, but do not send replies or outreach
  comments without explicit human approval.
- Do not perform bulk comment posting.
