# Comparative Drift Methodology And Implementation Map

Date: 2026-03-20

## Purpose

This note translates the comparative-drift literature into concrete decisions for the
`Articles/N2` pipeline and paper.

It is meant to answer four practical questions:

1. Which method families are justified by the literature for our Portuguese political setting?
2. Which parts of the current codebase already implement those ideas?
3. Which parts still reflect the earlier Word2Vec-first framing?
4. What should be implemented next so the paper is useful, comparable, and citable?

This note complements `docs/semantic_change_literature_guide.md`. That guide is the
broader reading map. This file is the implementation-facing bridge from literature to
pipeline decisions.

## Current Code Reality

The current default pipeline remains:

1. `prepare_corpus`
2. `train_word2vec`
3. `align_embeddings`
4. `score_candidates`
5. `report_candidates`

The strongest implemented path is therefore still the static aligned-embedding arm.

Current code locations:

- Shared corpus preparation: `src/stil_semantic_change/data/loaders.py`
- Shared preprocessing: `src/stil_semantic_change/preprocessing/text.py`
- Word2Vec training: `src/stil_semantic_change/word2vec/train.py`
- Word2Vec alignment: `src/stil_semantic_change/word2vec/align.py`
- Word2Vec scoring: `src/stil_semantic_change/word2vec/score.py`
- Current contextual follow-up: `src/stil_semantic_change/contextual/confirmatory.py`
- Current reporting: `src/stil_semantic_change/reporting/plots.py`
- Current readiness heuristic: `src/stil_semantic_change/reporting/evaluation.py`

Important constraint: the contextual code is still tied to `candidate_sets.json` produced
by Word2Vec scoring, so it is not yet a first-class peer method.

Important paper-facing mismatch: the code currently uses
`rufimelo/bert-large-portuguese-cased-sts`, while some older notes discuss `BERTimbau`.
Those are not the same model. For the article we should either:

- keep the current `rufimelo/...` model as an engineering choice and document it clearly, or
- switch to a Portuguese model with a cleaner article citation path

We should not cite `BERTimbau` as if it were the exact model currently being run.

## Literature-Backed Method Decisions

### 1. Keep slice-specific Word2Vec with alignment as one main arm

This remains well supported by the literature and is already the best-implemented method
in the repository.

Why it still belongs:

- Hamilton, Leskovec, and Jurafsky (2016) is the canonical reference for training
  embeddings per slice and aligning them with Orthogonal Procrustes.
- Shoemark et al. (2019) found that independently trained and aligned embeddings are
  preferable to continuous training when comparing long time series.
- Dubossarsky et al. (2019) warns that alignment-based change scores can overstate
  drift if we do not guard against temporal referencing and noise.

What this means for N2:

- keep the slice-specific `SGNS 300d + Procrustes` path
- keep replicate training
- report it as one comparison arm, not as the paper's privileged truth

What is already implemented:

- slice-specific SGNS training
- alignment
- per-lemma trajectory scoring
- candidate summaries and qualitative reports

What should change:

- the outputs should feed a shared comparison panel instead of directly driving the whole
  narrative
- the final paper should discuss Word2Vec as a strong static baseline, not the method that
  everything else must confirm

### 2. Add a cheap count/profile baseline, with TF-IDF as the practical first choice

The current repository has no count-based baseline yet, but the literature says the paper
needs one if the main question is when cheaper methods are enough.

Why it belongs:

- Schlechtweg et al. (2019) explicitly compare count-based and predictive vector spaces
  and treat count-based approaches as legitimate semantic-change baselines.
- SemEval-2020 Task 1 includes count-based baselines and evaluates graded change with
  Spearman ranking, which is directly relevant to our comparative framing.
- The new advisor direction is explicitly about cheap-versus-heavy methods.

What this means for N2:

- implement a first-class `tfidf_drift` scorer over the same prepared slice artifacts
- use identical lemma eligibility filters across TF-IDF, Word2Vec, and contextual scoring
- write results into the same long-form schema as the other methods

Practical recommendation:

- represent each lemma in each slice with a context-profile vector built from its local
  context distribution
- start with a transparent TF-IDF or PPMI-weighted profile
- score drift with consecutive-slice cosine distance plus first-vs-last distance

This is the cheapest arm to run, easiest to explain, and easiest to use as the baseline
for the paper's cost-versus-insight argument.

### 3. Reshape contextual BERT into a peer comparison arm, not a Word2Vec appendage

The code already has a useful contextual prototype path, but it is still confirmatory in
structure.

Why a contextual arm belongs:

- Giulianelli, Del Tredici, and Fernandez (2020) supports contextualized token
  representations for semantic change analysis.
- Kutuzov and Giulianelli (2020) gives practical scoring ideas like prototype distance
  and average pairwise distance.
- Kutuzov, Velldal, and Ovrelid (2022) shows that contextual methods can work well but
  also produce false positives and method-specific artifacts.
- Periti and Tahmasebi (2024) emphasizes that comparisons across contextual methods are
  often misleading unless the setup is controlled and equalized.

What this means for N2:

- keep contextual scoring bounded and sampled
- do not run it over the whole vocabulary first
- do not let Word2Vec alone decide the contextual candidate set

Practical recommendation:

- create a shared candidate panel with:
  - top drift terms from each method
  - stable controls
  - theory seeds
  - a few disagreement cases
- run the contextual scorer on that panel only
- record sample counts, runtime, and layers used alongside drift scores

What is already implemented:

- occurrence sampling by lemma and slice
- contextual embedding extraction
- prototype-distance scoring

What should change:

- rename and restructure `bert_confirmatory` into a neutral contextual stage
- read from a shared panel, not from `candidate_sets.json`
- write standardized outputs such as `method=contextual_bert`

### 4. Use NILC-Metrix as an interpretive support layer, not as a competing drift detector

NILC-Metrix is useful for Portuguese interpretability, but it should not replace the core
drift methods.

Why it belongs:

- Leal et al. (2023/2024) presents NILC-Metrix as a broad Brazilian Portuguese text
  complexity and cohesion toolkit with lexical, syntactic, psycholinguistic, and semantic
  metrics.

What this means for N2:

- use NILC-Metrix on selected slices, terms, or supporting corpora to explain rhetoric,
  complexity, cohesion, or style shifts around candidate words
- do not market it as the main drift detector

Good use in the paper:

- explain why a term looks stable in one representation but appears in changing rhetorical
  or complexity environments
- enrich qualitative case studies for political-discourse interpretation

### 5. Evaluate agreement and disagreement, not only absolute drift rankings

The new paper is strongest when it studies method agreement, disagreement, and cost.

Why this belongs:

- Shoemark et al. (2019) directly studies how evaluation choices affect change rankings.
- Schlechtweg et al. (2019) and SemEval-2020 frame graded change as a ranking problem and
  evaluate with Spearman correlation.
- Kutuzov et al. (2022) and Periti and Tahmasebi (2024) both reinforce that setup choices
  can strongly alter conclusions.

What this means for N2:

- the article should avoid claiming that one method reveals the true semantic change
- instead it should compare the rankings and inspect disagreement structure

Minimum comparison outputs to implement:

- Spearman correlation between method rankings
- Kendall correlation between method rankings
- top-k overlap and Jaccard overlap
- agreement on stable controls
- disagreement case packets for manual analysis
- runtime and memory summaries per method

These are exactly the artifacts needed to answer the advisor's question about when a
cheaper method is enough.

## Pipeline Design Implications

### A. Keep one shared preparation stage

All methods should consume the same prepared slice artifacts and the same lemma-eligibility
table. This avoids hidden methodological differences.

The current preparation stage is already reusable for that purpose.

### B. Introduce a method-neutral comparison panel

The project now needs a canonical artifact such as:

`comparison_panel.parquet`

Recommended columns:

- `lemma`
- `slice_count`
- `total_frequency`
- `slice_presence_ratio`
- `bucket`
- `selected_by_word2vec`
- `selected_by_tfidf`
- `selected_by_contextual`
- `selected_as_stable_control`
- `selected_as_theory_seed`

This panel should be the handoff between single-method scoring and cross-method analysis.

### C. Standardize method outputs

Each method should write a long-form score table with the same core columns:

- `lemma`
- `method`
- `primary_drift`
- `first_last_drift`
- `slice_count`
- `sample_count_total`
- `sample_count_min`
- `runtime_seconds`
- `notes`

This is the cleanest path to later comparison plots and paper tables.

### D. Separate exploratory runs from preserved baselines

The repository currently preserves logs of exploratory or incomplete runs more clearly than
one clean finished baseline package.

For the comparative paper, artifact naming should distinguish:

- `quicklook`
- `baseline_clean`
- `ablation`
- `comparison_panel`
- `paper_release`

The point is not cosmetic. It prevents the quick exploratory path from being mistaken for
the paper-quality baseline.

## What The Current Repository Already Supports Well

- shared corpus preparation for `BrPoliCorpus floor` and `Roda Viva`
- reproducible Hydra + `uv` configuration
- SGNS training by slice
- Orthogonal Procrustes alignment
- replicate-aware static drift scoring
- qualitative reporting around top Word2Vec candidates

## What Is Still Too Tied To The Old Framing

- default task graph assumes Word2Vec is the main experiment
- contextual scoring depends on Word2Vec candidate selection
- reporting titles and summaries remain Word2Vec-centered
- readiness heuristics are single-method heuristics
- there is no first-class cheap baseline yet
- there is no cross-method agreement stage yet

## Recommended Next Implementation Order

### 1. Preserve one clean Word2Vec baseline run

Before broadening the comparison, produce one inspectable completed baseline with:

- manifests for every stage
- preserved scores
- preserved reports
- resolved config
- explicit note of the preprocessing variant used

This is the reference point for all later comparisons.

### 2. Implement `tfidf_drift`

This is the highest-value missing method because it directly supports the article's
cheap-versus-heavy question.

Recommended outputs:

- `scores/tfidf_drift/scores.parquet`
- `scores/tfidf_drift/trajectory.parquet`
- `scores/tfidf_drift/summary.json`

### 3. Create `comparison_panel`

Build one stage that merges:

- top terms from Word2Vec
- top terms from TF-IDF
- theory seeds
- stable controls

This stage should own the candidate universe for contextual scoring.

### 4. Convert contextual scoring into `contextual_drift_panel`

Reuse the current sampling and prototype code, but read from the shared panel and write
method-standard outputs.

### 5. Implement `compare_methods`

This stage should write:

- rank-correlation tables
- top-k overlap tables
- disagreement packets
- runtime summary
- paper-ready comparison figures

### 6. Replace STIL readiness with comparison readiness

The current `reporting/evaluation.py` logic should be complemented or replaced by a new
paper-readiness report that checks:

- whether all methods ran on the same eligible set
- whether agreement statistics were computed
- whether disagreement cases were sampled
- whether runtime metadata is present

## Paper Usefulness Criteria

The paper becomes much stronger if it can answer these questions with artifacts instead of
impressions:

1. Which terms are surfaced by all methods?
2. Which terms are method-specific?
3. Does TF-IDF recover enough of the interpretable high-drift set to be useful as a cheap
   screen?
4. Which kinds of disagreements are linguistic, and which look like model artifacts?
5. What extra cost does the contextual arm buy us in practice?

If the pipeline produces those answers cleanly, the paper can be useful even without a
Portuguese gold benchmark.

## Cited References

- Hamilton, William L., Jure Leskovec, and Dan Jurafsky. 2016. "Diachronic Word
  Embeddings Reveal Statistical Laws of Semantic Change." ACL 2016.
  Link: <https://arxiv.org/abs/1605.09096>
- Shoemark, Philippa, Farhana Ferdousi Liza, Dong Nguyen, Scott A. Hale, and Barbara
  McGillivray. 2019. "Room to Glo: A Systematic Comparison of Semantic Change Detection
  Approaches with Word Embeddings." EMNLP-IJCNLP 2019.
  Link: <https://aclanthology.org/D19-1007/>
- Dubossarsky, Haim, Simon Hengchen, Nina Tahmasebi, and Dominik Schlechtweg. 2019.
  "Time-Out: Temporal Referencing for Robust Modeling of Lexical Semantic Change."
  ACL 2019.
  Link: <https://aclanthology.org/P19-1044/>
- Schlechtweg, Dominik, Anna Hätty, Marco Del Tredici, and Sabine Schulte im Walde.
  2019. "A Wind of Change: Detecting and Evaluating Lexical Semantic Change across Times
  and Domains." ACL 2019.
  Link: <https://arxiv.org/abs/1906.02979>
- Schlechtweg, Dominik, Barbara McGillivray, Simon Hengchen, Haim Dubossarsky, and Nina
  Tahmasebi. 2020. "SemEval-2020 Task 1: Unsupervised Lexical Semantic Change Detection."
  SemEval 2020.
  Link: <https://aclanthology.org/2020.semeval-1.1/>
- Giulianelli, Mario, Marco Del Tredici, and Raquel Fernandez. 2020. "Analysing Lexical
  Semantic Change with Contextualised Word Representations." ACL 2020.
  Link: <https://aclanthology.org/2020.acl-main.365/>
- Kutuzov, Andrey, and Mario Giulianelli. 2020. "UiO-UvA at SemEval-2020 Task 1:
  Contextualised Embeddings for Lexical Semantic Change Detection." SemEval 2020.
  Link: <https://aclanthology.org/2020.semeval-1.17/>
- Kutuzov, Andrey, Erik Velldal, and Lilja Ovrelid. 2022. "Contextualized Embeddings for
  Semantic Change Detection: Lessons Learned." Northern European Journal of Language
  Technology.
  Link: <https://aclanthology.org/2022.nejlt-1.9/>
- Periti, Francesco, and Nina Tahmasebi. 2024. "A Systematic Comparison of Contextualized
  Word Embeddings for Lexical Semantic Change." NAACL 2024.
  Link: <https://aclanthology.org/2024.naacl-long.240/>
- Leal, Sidney Evaldo, Magali Sanches Duran, Carolina Scarton, Nathan Siegle Hartmann,
  and Sandra Maria Aluisio. 2023/2024. "NILC-Metrix: assessing the complexity of written
  and spoken language in Brazilian Portuguese." Language Resources and Evaluation.
  Link: <https://link.springer.com/article/10.1007/s10579-023-09693-w>
