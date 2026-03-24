# Runtime And Config Cleanup

Date: 2026-03-21

This note records the runtime and configuration cleanup applied after the prepared-artifact refactor.

## Why This Was Needed

The codebase had three quiet mismatches between implementation and project expectations:

1. optional `BERT` dependencies were imported even during non-BERT runs
2. `model.text_view` was configurable but not validated early
3. `preprocess.preserve_accents` existed in config but did not affect normalization

These did not break every run, but they made the project heavier to start, easier to misconfigure, and harder to reproduce cleanly.

## What Changed

### 1. Lazy loading for optional contextual code

- `torch` and `transformers` are no longer imported at core runner import time
- the `bert_confirmatory` stage imports its heavy stack only when that stage is invoked
- reporting is also imported lazily inside the reporting stage

Practical effect:

- the main yearly `Word2Vec` pipeline is lighter to start
- preprocessing worker startup should avoid paying the contextual import cost

### 2. Early validation for `model.text_view`

`model.text_view` now fails fast at config-load time.

Valid values:

- `normalized_surface`
- `content_surface`
- `content_lemma`

Practical effect:

- typos now produce a clear config error instead of a later `KeyError`

### 3. Active accent normalization switch

`preprocess.preserve_accents` is now implemented in preprocessing normalization.

Behavior:

- `true`
  - keeps forms such as `corrupção`, `aliás`, `democrática`
- `false`
  - normalizes them to `corrupcao`, `alias`, `democratica`

The stopword list, function-word heuristics, and lemma overrides are normalized consistently with the chosen setting.

## Current Recommended Defaults

For the current Portuguese political-discourse experiments:

- keep `model.text_view=content_lemma` for the default `Word2Vec` baseline
- keep `preprocess.preserve_accents=true` unless there is a deliberate normalization comparison
- treat `bert_confirmatory` as optional and invoke it only after the cheaper yearly pipeline is stable

## Things Future Changes Should Respect

- do not reintroduce a single universal `clean_text` abstraction
- do not add new prepared text views without documenting them in `prepared_artifact_layout_2026_03_21.md`
- do not add config keys without wiring them into actual behavior or explicitly marking them as reserved
