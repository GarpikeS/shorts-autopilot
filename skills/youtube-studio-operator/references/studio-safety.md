# Studio Safety

## Authorization

Store the Chrome profile outside Git. A profile may contain reusable session
cookies and should be treated as a credential.

## Browser Process

- Use `--headless=new` and `--mute-audio` on every launch.
- Hide the root process window on Windows.
- Use a normal current Windows Chrome user agent.
- Use a dedicated CDP port and verify `/json/version` before connecting.
- Stop the dedicated process after the operation unless it is intentionally
  shared with another active task.

## Publication Confirmation

Do not treat clicking the final button as success. Success requires a Studio
content row or confirmation response that provides a video ID and matches the
requested visibility and schedule. Calendar controls can display adjacent-month
days, so verify full date, year, time, and timezone after selection.

## State Updates

Keep generated media as `ready` until Studio is confirmed. Require a video ID
for `scheduled` and `published` manifest states. On an ambiguous result, leave
the manifest unchanged and preserve diagnostics for review.
