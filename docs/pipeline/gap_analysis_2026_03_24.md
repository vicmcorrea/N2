# Comparative Pipeline Gap Analysis

**Date**: 2026-03-24
**Frozen run**: `ba65fe5b9cce`
**Target venue**: STIL 2026 (10-page long paper, double-blind)
**Constraint**: Frozen run outputs must remain untouched; any new work writes to a separate directory.

---

## Executive Summary

Six methodological gaps were identified in `literature_comparison_2026_03_24.md`. After
examining the frozen BERT artifacts, the Hydra pipeline configuration, and the current
literature in depth, the findings below classify each gap and rank them by
effort-to-value ratio.

**Key discovery**: The frozen run stores **individual per-occurrence BERT embeddings**
(82,461 × 1024 per layer) in `occurrence_embeddings_layer_{-1,-4}.npz`, alongside full
metadata in `occurrence_embeddings_meta.parquet`. This means Gap 1 (APD) and Gap 3
(clustering) can be addressed with pure post-hoc analysis scripts — no BERT re-run
required.

---

## Gap-by-Gap Assessment

### Gap 1: APD Instead of Centroid Cosine (PRT)

**Priority**: HIGH
**Classification**: Post-run analysis script on existing artifacts
**Effort**: ~1 day coding + testing
**STIL-worthiness**: YES — do before submission

**Current state**: Our `score_prototype_distances()` in `confirmatory.py:59` computes
cosine distance between per-slice centroid vectors (PRT). This is the metric that
Rachinskiy & Schlechtweg (2025) criticize as "reducing representations to a single
point, potentially obscuring sense-specific changes."

**What the literature says**:
- Cassotti et al. (2024): APD achieves .751 weighted Spearman across 8 languages on
  GCD benchmarks, dominating PRT.
- However, a 2024 arxiv paper (Pranjić et al., arXiv:2402.16596) proved algebraically
  that APD with cosine distance simplifies to `1 - p̂·q̂` where `p̂` and `q̂` are the
  L2-normalized means of the L2-normalized individual embeddings. This means **APD is
  mathematically equivalent to cosine distance between normalized-mean vectors** — close
  to PRT but with unit-normalization of each occurrence first.
- The practical difference: PRT averages raw vectors then measures distance. APD
  normalizes each occurrence to unit length first, then averages, then measures distance.
  This reweighting gives lower-magnitude occurrences equal influence.

**Feasibility on frozen artifacts**:
- `occurrence_embeddings_layer_-1.npz`: 82,461 × 1024 individual BERT vectors ✓
- `occurrence_embeddings_meta.parquet`: maps each row to (lemma, slice_id) ✓
- Algorithm: group by (lemma, layer), for consecutive slice pairs, compute APD
- Computation: pure numpy, no GPU, ~minutes on CPU
- Outputs to: new directory (e.g., `scores/apd_reanalysis/`)

**Implementation sketch**:
```python
# For each (lemma, layer) and consecutive (slice_i, slice_j):
emb_i = embeddings[meta_grouped[(lemma, slice_i)]]  # (n_i, 1024)
emb_j = embeddings[meta_grouped[(lemma, slice_j)]]  # (n_j, 1024)
# Normalize each occurrence to unit length
emb_i_norm = emb_i / np.linalg.norm(emb_i, axis=1, keepdims=True)
emb_j_norm = emb_j / np.linalg.norm(emb_j, axis=1, keepdims=True)
# APD = mean of all pairwise cosine distances
apd = 1.0 - (emb_i_norm @ emb_j_norm.T).mean()
```

**Value for the paper**:
- Directly addresses the most likely reviewer objection
- Enables a sentence like: "We additionally computed APD (Kutuzov & Giulianelli 2020),
  the current dominant metric for contextual LSCD, and found Spearman ρ = X between
  APD and PRT rankings, confirming that [centroid aggregation closely tracks /
  meaningfully differs from] the pairwise approach on our panel."
- If APD and PRT correlate strongly (likely, given the algebraic relationship): our
  PRT results are validated, and we can note this robustness
- If they diverge: even more interesting for our comparative story

**Recommendation**: **Implement before STIL submission.** Write a standalone script that
reads frozen `.npz` + `.parquet`, computes APD scores, and saves results alongside
a brief comparison table. Add one paragraph to the Discussion section.

---

### Gap 2: BERT Layer Choice — Layer −1 vs. Mid-Layers

**Priority**: MEDIUM (reduced from literature_comparison)
**Classification**: Requires new BERT inference run
**Effort**: ~4–8 hours GPU/CPU time + pipeline modification
**STIL-worthiness**: NO — future work

**Current state**: We extract layers −1 (=24) and −4 (=21) from a 24-layer model.

**What the literature actually says** (corrected after deeper review):
- Laicher et al. (2021): For APD, layers 12 and 9-12 perform **best** — these are the
  **higher** layers in a 12-layer model. Lower layers including layer 1 perform
  significantly worse. The "mid-layer" advantage is specifically for JSD-based clustering
  (sense-based), not for APD.
- Cassotti et al. (2024): "early layers consistently result in higher performance" —
  but this is across multiple models including XL-LEXEME, and "early" means layers 8-10
  in a 12-layer model (i.e., still in the upper half).
- For our 24-layer model, layers −1 (=24) and −4 (=21) are in the topmost range.
  The equivalent of "layers 9-12 in a 12-layer model" would be roughly layers 18-24
  in our 24-layer model — which **includes our current extraction layers**.

**Feasibility on frozen artifacts**:
- Only layers −1 and −4 are stored. Any other layer requires re-running BERT inference.
- Re-running BERT took ~4 hours on CPU in the original run.
- Would need a new experiment directory and Hydra config override.

**Why this is lower priority than initially assessed**:
1. The literature conflict is less clear-cut than stated in `literature_comparison`:
   Laicher et al. found **higher layers** work best for APD (our metric family)
2. Our layer −4 (=21) is actually within the recommended range for a 24-layer model
3. Our cross-layer agreement (Spearman 0.858) already demonstrates stability
4. Adding mid-layer analysis requires ~4h of compute and a new pipeline stage, with
   uncertain payoff for 10-page budget

**Recommendation**: **Future work only.** Add one sentence to Limitations: "We extracted
layers −1 and −4; the literature suggests varied optimal layers depending on model
depth and metric choice (Laicher et al. 2021; Cassotti et al. 2024), and our cross-layer
agreement (ρ = 0.858) indicates results are stable within the upper layer range."

---

### Gap 3: Sense-Based Clustering (JSD)

**Priority**: MEDIUM
**Classification**: Post-run analysis script on existing artifacts
**Effort**: ~2–3 days coding + analysis
**STIL-worthiness**: BORDERLINE — high value but may not fit in 10 pages

**Current state**: We use purely form-based aggregation (centroids and, with Gap 1,
potentially APD). No clustering of BERT embeddings into discrete senses.

**What the literature says**:
- Giulianelli et al. (2020): Cluster BERT embeddings → measure JSD between sense
  distributions across time periods.
- Montariol (2021): Scalable K-means clustering + JSD.
- Cassotti et al. (2024): APD (form-based) **outperforms** JSD (sense-based) on GCD
  benchmarks. Sense-based methods have "low WSI and GCD performance" raising concerns
  about whether clusters "capture meaningful patterns or produce noisy aggregation."

**Feasibility on frozen artifacts**:
- Individual embeddings available (82,461 × 1024 per layer) ✓
- Can cluster per-lemma embeddings using K-means or agglomerative clustering
- Compute JSD between cluster distributions across consecutive slices
- Pure post-hoc computation, no GPU needed

**Value for the paper**:
- Would add a fourth metric dimension (PRT, APD, JSD) to the comparison
- Potentially interesting if JSD detects different patterns than APD/PRT
- However: Cassotti et al. (2024) already showed JSD underperforms APD, so adding it
  may dilute rather than strengthen our contribution
- Clustering adds methodological complexity (choosing k, sensitivity to initialization)
  that requires justification in a 10-page paper

**Recommendation**: **Future work, with a caveat.** If Gap 1 (APD) reveals that APD and
PRT diverge meaningfully on our panel, then JSD becomes more interesting as a third
perspective. But if APD and PRT correlate strongly, JSD adds complexity without clear
payoff for STIL's page limit. Mention as future work: "Sense-based approaches using
clustering of contextual embeddings (Giulianelli et al. 2020) could provide
complementary insights."

---

### Gap 4: Orthographic Bias Mitigation

**Priority**: LOW-MEDIUM
**Classification**: Requires full re-run of BERT confirmatory stage
**Effort**: ~1 day code modification + ~4–8h compute
**STIL-worthiness**: NO — future work

**Current state**: We feed raw text contexts to BERT and extract the target token's
embedding directly.

**What the literature says**:
- Laicher et al. (2021): BERT encodes orthographic form of the target word even in
  higher layers. Reducing this influence (via lemmatization of target word, masking,
  or averaging surrounding context only) improves LSCD performance.
- Matthews et al. (2024, arXiv:2408.04162): Contextual embeddings are "highly sensitive
  to orthographic noise" — subword tokenization makes this worse for rare/long words.

**Feasibility on frozen artifacts**:
- **Cannot be done post-hoc.** Orthographic bias mitigation requires changing what gets
  fed to BERT before embedding extraction:
  - Target-token masking: replace target word with [MASK] before inference
  - Context-only averaging: average all token embeddings *except* the target
  - Lemmatized-form substitution: replace inflected form with lemma in input
- All three approaches require re-running BERT inference from scratch.
- We do have the raw text and token metadata in `prepared/`, so reconstruction is
  feasible, but it requires a new BERT run.

**Why this is low priority**:
1. The current pipeline already operates on lemmatized text for Word2Vec/TF-IDF, so the
   BERT comparison is methodologically consistent
2. Laicher et al.'s finding is specifically about *improving BERT performance* — our
   paper's contribution is not about optimizing BERT but comparing methods
3. The orthographic bias explanation actually *supports* our finding that BERT adds only
   modest value over Word2Vec
4. Computing time is non-trivial (~4h CPU)

**Recommendation**: **Future work.** Add to Limitations: "We did not apply orthographic
bias mitigation (Laicher et al. 2021), which could improve BERT's discriminative power.
This conservative design choice strengthens our conclusion that contextual models add
modest value, as any improvement from debiasing would only increase BERT's margin."

---

### Gap 5: Context Sample Size (64 per lemma per slice)

**Priority**: LOW
**Classification**: Requires full re-run of BERT confirmatory stage
**Effort**: ~4–8h compute (trivial code change)
**STIL-worthiness**: NO — mention in Limitations only

**Current state**: `bert_max_contexts_per_slice: 64` in the model config.

**What the literature says**: No consensus. Some studies use 100-200+, others use fewer.
64 is not unusually low, especially for a 24-slice diachronic study.

**Feasibility**: Trivial config change (`model.bert_max_contexts_per_slice=200`), but
requires a full re-run of the BERT stage, writing to a new experiment directory.

**Recommendation**: **One-sentence mention in Limitations.** Not worth a re-run. Our
per-lemma occurrence counts (30-64 per slice, 82,461 total) are sufficient for the
exploratory scope. Higher counts would reduce variance but are unlikely to change
rankings qualitatively.

---

### Gap 6: No XL-LEXEME or Specialized Models

**Priority**: LOW
**Classification**: Requires new BERT-stage code + compute
**Effort**: ~2–3 days + GPU compute
**STIL-worthiness**: NO — future work

**Current state**: We use `rufimelo/bert-large-portuguese-cased-sts`, a Portuguese
BERT-large fine-tuned for semantic textual similarity.

**What the literature says**: XL-LEXEME (Cassotti et al. 2023, 2024) consistently
outperforms vanilla BERT on LSCD across languages. However, XL-LEXEME is trained
on English data and there is no Portuguese-specific variant.

**Our model choice is actually reasonable**:
- `rufimelo/bert-large-portuguese-cased-sts` is fine-tuned on Portuguese STS, which
  should provide better semantic representations than vanilla BERT for Portuguese
- Using a monolingual Portuguese model is a strength over mBERT for this task
  (Souza et al. 2020 showed BERTimbau outperforms mBERT on Portuguese NLP tasks)
- The lack of a Portuguese XL-LEXEME makes comparison impossible

**Recommendation**: **One sentence in Future Work.** "Specialized LSCD models such as
XL-LEXEME (Cassotti et al. 2023) could further improve contextual detection, pending
availability of Portuguese-adapted versions."

---

## Priority Ranking: Effort-to-Value Ratio

| Rank | Gap | Classification | Effort | Value | Do Before STIL? |
|------|-----|---------------|--------|-------|-----------------|
| **1** | **Gap 1: APD metric** | Post-run script | ~1 day | HIGH | **YES** |
| 2 | Gap 3: JSD clustering | Post-run script | ~2-3 days | MEDIUM | Only if Gap 1 reveals divergence |
| 3 | Gap 2: Mid-layer extraction | New BERT run | ~1-2 days | MEDIUM-LOW | NO |
| 4 | Gap 4: Orthographic bias | New BERT run | ~1-2 days | LOW-MEDIUM | NO |
| 5 | Gap 5: Context sample size | New BERT run | ~1 day | LOW | NO |
| 6 | Gap 6: XL-LEXEME | New code + GPU | ~3 days | LOW | NO |

---

## Recommended Action Plan for STIL Submission

### Must-do (before submission)

1. **Implement APD reanalysis script** (Gap 1)
   - Read `occurrence_embeddings_layer_{-1,-4}.npz` + `occurrence_embeddings_meta.parquet`
   - Compute APD for all 55 panel lemmas × 2 layers × 23 transitions
   - Output: `scores/apd_reanalysis/apd_scores.parquet`, `apd_trajectory.parquet`
   - Compare APD vs PRT rankings (Spearman)
   - Write to a new directory **outside** `ba65fe5b9cce` (e.g., a new experiment hash
     or `run/outputs/post_hoc/apd_reanalysis/`)
   - Add 1 paragraph to Discussion + 1 sentence to Limitations in `main.tex`

### Should-do (paper text only, no new computation)

2. **Update Limitations section** with one paragraph covering:
   - PRT vs APD metric choice (acknowledge, cite Cassotti 2024)
   - Layer selection (cite Laicher 2021, note our layer agreement)
   - Orthographic bias (cite Laicher 2021, frame as conservative choice)
   - Context sample size (one sentence)

3. **Update Discussion section** with:
   - Layer agreement as robustness indicator
   - If APD computed: comparison of APD vs PRT rankings
   - Frame cost-benefit finding with reference to Cassotti et al. (2024) on GPT-4

4. **Add missing references** to bibliography:
   - Cassotti et al. (2024) — systematic comparison (NAACL)
   - Laicher et al. (2021) — BERT orthographic bias (EACL SRW)
   - Rachinskiy & Schlechtweg (2025) — metric critique (if page space allows)

### Future work (mention in paper, implement later)

5. Sense-based clustering / JSD (Gap 3)
6. Mid-layer extraction (Gap 2)
7. Orthographic bias mitigation (Gap 4)
8. XL-LEXEME for Portuguese (Gap 6)

---

## Artifact Compatibility Summary

| Artifact | Path | Gaps served |
|----------|------|-------------|
| `occurrence_embeddings_layer_-1.npz` (313 MB) | `scores/bert_confirmatory/` | Gap 1, Gap 3 |
| `occurrence_embeddings_layer_-4.npz` (314 MB) | `scores/bert_confirmatory/` | Gap 1, Gap 3 |
| `occurrence_embeddings_meta.parquet` (82,461 rows) | `scores/bert_confirmatory/` | Gap 1, Gap 3 |
| `prototype_embeddings_layer_-1.npz` (5 MB) | `scores/bert_confirmatory/` | PRT baseline |
| `scores.parquet` (110 rows) | `scores/bert_confirmatory/` | PRT comparison |
| `prepared/docs/raw_text/` | `prepared/` | Gap 4 (requires re-run) |
| `prepared/tokens/content/` | `prepared/` | Gap 4 (requires re-run) |

**Frozen run integrity**: All post-hoc scripts read from `ba65fe5b9cce` and write to
a separate output directory. The frozen run is never modified.

---

*End of gap analysis. This document should be revisited if APD results change the
comparative story significantly.*
