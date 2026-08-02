# Security

- Keep API keys in environment variables or a secret manager.
- Keep Chrome profiles outside the repository. They contain cookies and active
  sessions.
- Never commit OAuth client secrets, refresh tokens, Studio screenshots, or
  channel exports.
- Run outreach or comment posting only with explicit human approval. This
  project does not auto-publish comments.
- Record `scheduled` or `published` only after Studio returns a video ID and the
  intended visibility/date can be read back.
- Review generated frames and audio before any upload.
