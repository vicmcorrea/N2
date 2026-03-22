# Word2Vec Baseline Freeze

Date: 2026-03-21

This note freezes the cleaned yearly `Word2Vec` baseline run:

- run id: `ba65fe5b9cce`
- run root:
  - `run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce`

## Why This Run Is Frozen

This run is the first cleaned baseline that is mechanically complete after the preprocessing and artifact-structure fixes.

It is worth freezing because:

- the full pipeline completed successfully
- the prepared multi-view artifact structure was written correctly
- malformed lemmas such as `digar`, `repitar`, `estarer`, `deverer`, and whitespace lemmas are absent from scored outputs
- the stage manifests are complete for:
  - `prepare_corpus`
  - `train_word2vec`
  - `align_embeddings`
  - `score_candidates`
  - `report_candidates`

## Completed Stage Times

Finished on March 21, 2026:

- `prepare_corpus`: 19:58:32 BRT
- `train_word2vec`: 20:15:26 BRT
- `align_embeddings`: 20:16:05 BRT
- `score_candidates`: 20:21:23 BRT
- `report_candidates`: 20:21:27 BRT

## What This Baseline Is Good For

- freezing the cleaned technical `Word2Vec` reference run
- comparing future selection/filter changes against a stable baseline
- preserving a reproducible point before introducing stronger lexical panel filters

## Main Caveat

The raw top drift ranking is still too dominated by low-content rhetorical or evaluative terms such as:

- `acaso`
- `novidade`
- `óbvio`
- `impossível`
- `refiro`
- `propósito`

So this run should be treated as the frozen cleaned baseline, not as the final paper-facing candidate panel.

## Next Step After Freeze

Keep this run unchanged and improve the candidate-panel filtering layer before launching the next long rerun.

That validation step is now recorded in:

- `docs/candidate_panel_filter_2026_03_21.md`
