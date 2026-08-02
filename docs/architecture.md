# Architecture

The pipeline has four explicit boundaries:

1. `EpisodeSpec` is the portable content contract.
2. `novelty.py` is a fail-closed gate against the recent manifest.
3. `render.py` and `qa.py` produce and validate local media without publishing.
4. `manifest.py` records publication only after an external confirmation.

Image generation is a provider boundary. The built-in Polza adapter can be
replaced without changing the episode model or renderer. YouTube credentials
and browser state are deliberately not modeled as project files.
