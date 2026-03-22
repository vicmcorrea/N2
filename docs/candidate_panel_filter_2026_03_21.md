# Candidate Panel Filter

Date: 2026-03-21

This note records the rationale for adding a stronger filter layer on top of the cleaned `Word2Vec` baseline.

## Problem

The cleaned baseline removed malformed lemmas and whitespace artifacts, but the raw top drift list still overemphasized low-content terms.

Examples from the frozen baseline:

- `acaso`
- `novidade`
- `separar`
- `óbvio`
- `impossível`
- `dizer-se`
- `refiro`
- `propósito`

These are not necessarily preprocessing errors. They are often real words, but they are poor paper-facing drift candidates because they are too generic, rhetorical, evidential, evaluative, or discourse-structural.

## Design Decision

Do **not** alter the underlying score table just to hide these terms.

Instead:

1. keep the raw `scores_aggregated.parquet` ranking intact
2. add a separate candidate-panel exclusion layer for:
   - drift candidates
   - stable controls
3. make the report distinguish between:
   - the selected candidate panel
   - the raw top drift ranking before panel filtering

## Current Filter Strategy

### Drift-candidate POS gate

The drift panel now uses dominant POS aggregated from `prepared/tokens/content` and keeps only lemmas whose dominant POS is:

- `NOUN`
- `ADJ`

This removes a large amount of verbal residue before lexical exclusions are even applied.

### Drift-candidate exclusions

The drift-panel lexical exclusions are now centralized in:

- `src/stil_semantic_change/selection/lexicons.py`

The list removes generic discourse nouns, broad evaluative adjectives, rhetorical fillers, and known residue such as:

- `acaso`
- `novidade`
- `sinal`
- `resto`
- `espécie`
- `jeito`
- `pergunta`
- `interessante`
- `volta`
- `termo`
- `ademal`

### Stable-control exclusions

The stable-control panel also uses dominant POS gating (`NOUN` and `ADJ`) and excludes overtly procedural forms such as:

- `art.`
- `cumprimentá-lo`
- `ocupo`
- `sessão`

## Why This Is Safer Than Post-Hoc Editing

- the raw score distribution remains available for audit
- the candidate-panel logic becomes explicit and reproducible
- future runs can be compared both at the raw-score level and at the filtered-panel level

## Validation On Frozen Baseline

This filter was validated against the frozen cleaned baseline:

- `run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce`

Using the existing raw `scores_aggregated.parquet` plus dominant POS from the prepared token shards, the validated preview drift panel became:

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

This is not a claim that every selected term is ideal. It is a practical validation that the panel is materially more interpretable than the raw top drift list dominated by discourse residue.

## Practical Goal

Before the next full rerun, the goal is not to prove that every selected term is perfect.

The goal is to ensure that the top paper-facing drift panel is substantially more likely to contain:

- substantive political concepts
- policy or institutional terms
- clearly interpretable public-discourse vocabulary

and much less likely to contain:

- generic speech acts
- evidential fillers
- broad evaluative adjectives
- parliamentary procedural residue
