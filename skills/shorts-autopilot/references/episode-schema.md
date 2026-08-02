# Episode Schema

Required top-level fields:

- `id`: stable private identifier; never expose it as episode numbering.
- `title`: public title.
- `topic`: semantic topic used by novelty comparison.
- `hook`: what happens in the first one or two seconds.
- `visual_language`: composition and medium, not just a color palette.
- `punchline`: final comedic turn.
- `template`: abstract sequence of beats. Make it specific enough to detect
  repeated structures.
- `scenes`: two to eight scene objects.

Recommended fields are `description`, `tags`, `characters`, `props`, `voice`,
and `image_provider`.

Each scene requires `caption`, `narration`, and exactly one practical source:

- `image`: path relative to the episode JSON, or
- `image_prompt`: prompt sent to the configured image provider.

`min_duration` defaults to 2 seconds. The renderer extends a scene when its
narration is longer.
