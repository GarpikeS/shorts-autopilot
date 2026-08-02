---
name: shorts-autopilot
description: Create, validate, and package independent vertical Shorts with this repository. Use when an agent must develop a standalone Short concept, reject repetition against the latest manifest, generate scene media and narration, render a 1080x1920 video, or review ffprobe, silence, and contact-sheet QA before upload.
---

# Shorts Autopilot

Use the repository CLI as the source of truth for novelty, rendering, and media
QA. Do not bypass a failed novelty check to fill a publishing slot.

## Workflow

1. Read the latest 10 active records from the manifest. Ignore `deleted` and
   `cancelled` records as queue items, but keep their concepts in mind when
   reviewing repetition manually.
2. Write one standalone entertainment-first concept. It must have a new topic,
   hook, visual language, characters or objects, punchline, and structural
   template.
3. Put the concept in an episode JSON using the schema in
   `references/episode-schema.md`.
4. Run `shorts-autopilot novelty`. If it exits with code 2, revise the concept
   rather than lowering thresholds.
5. Run `shorts-autopilot build`. Use existing licensed images by setting
   `image`, or an approved provider by setting `image_prompt`.
6. Open the generated contact sheet and listen to the final media. Confirm that
   the conflict is visible in the first two seconds, captions fit, narration is
   intelligible, and the ending lands without channel lore.
7. Read the `.qa.json` report. Do not upload a file with decode, dimension,
   audio, or unexplained long-silence failures.
8. Hand the validated package to the `youtube-studio-operator` skill.

## Creative Constraints

- Treat every Short as an independent work.
- Do not use episode numbering, recurring characters, cliffhangers, lore, or a
  repeated setup-to-explanation formula.
- Target 12 to 16 seconds. Go longer only when the joke needs it.
- Put a visual conflict or punchline in the first one or two seconds.
- Keep advertising and brand solution claims out of the content.
- Allow at most one brief practical takeaway.
- Never add internal IDs such as `series`, `episode`, or `meme 12` to public
  titles, descriptions, captions, or frames.

## Commands

```powershell
shorts-autopilot novelty --episode examples\episode.json --manifest workspace\manifest.json
shorts-autopilot build --episode examples\episode.json --manifest workspace\manifest.json --output output
shorts-autopilot qa output\ITEM\ITEM.mp4
```

Do not run `record` with `scheduled` or `published` until YouTube Studio has
confirmed the video ID and intended publication state.
