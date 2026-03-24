# Comparison Panel

Date: 2026-03-22

## What Was Added

A first-class `comparison_panel` stage now exists in the N2 experiment package.

New code paths:

- `src/stil_semantic_change/comparison/panel.py`
- `src/stil_semantic_change/comparison/__init__.py`
- `run/conf/task/comparison_panel.yaml`
- `tests/test_comparison_panel.py`

The stage merges the cleaned method-local panels into one shared downstream term
table for comparative analysis and future contextual scoring.

## Clean Source Run

The current clean source run for the shared panel is:

- `run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce`

The panel was built directly against that frozen run's score artifacts so the
comparison table stays anchored to the clean frozen baseline.

## Important Integrity Note

The later overnight rerun at:

- `run/outputs/experiments/brpolicorpus_floor_yearly/8e15dc2372c5`

should still not be treated as the immutable prepared-artifact source because
its prepared root was touched by an aborted forced rerun after completion.

Use `ba65fe5b9cce` as the source of truth for the current comparison panel.

## Current Outputs

The shared panel artifacts are now written under:

- `scores/comparison_panel/comparison_panel.parquet`
- `scores/comparison_panel/summary.json`
- `scores/comparison_panel/comparison_panel_manifest.json`

For the current frozen run, that resolves to:

- `run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/comparison_panel`

## Current Panel Contents

Current summary on `ba65fe5b9cce`:

- row count: `55`
- `Word2Vec` drift terms: `15`
- `TF-IDF` drift terms: `15`
- stable controls: `20`
- theory seeds: `5`
- shared drift overlap: `0`
- disagreement cases: `30`
- text view: `content_lemma`

This means the first comparison panel is almost entirely a disagreement panel,
which is useful for the comparative paper because it creates a focused universe
for later contextual adjudication instead of pretending that the cheap methods
already agree.

## Current Drift Buckets

Current `Word2Vec`-only drift bucket:

- `intervenção`
- `planalto`
- `renovação`
- `troca`
- `inaceitável`
- `oposto`
- `perigoso`
- `crítico`
- `contradição`
- `excepcional`
- `inédito`
- `exposição`
- `bloqueio`
- `típico`
- `alvo`

Current `TF-IDF`-only drift bucket:

- `crise`
- `trabalhador`
- `saúde`
- `salário`
- `emenda`
- `eleição`
- `previdência`
- `provisório`
- `preço`
- `mínimo`
- `político`
- `voto`
- `real`
- `partido`
- `destaque`

Current theory seeds included in the panel:

- `corrupção`
- `democracia`
- `economia`
- `liberdade`
- `reforma`

## Why This Matters

This panel is now the right common input for:

- contextual `BERT` scoring
- agreement and disagreement analysis
- top-k overlap summaries
- paper-facing examples of cheap-method divergence

It also separates method-specific candidate selection from the shared comparison
universe, which keeps downstream analysis cleaner.

## Recommended Next Step

The next implementation step should be:

1. point contextual `BERT` at this shared `comparison_panel`
2. score sampled contextual usages for the shared term set
3. add agreement and disagreement summaries on top of the shared panel
