# Literature Comparison: How Our Methodology Compares to the Field

Date: 2026-03-24

## Purpose

This note documents a systematic comparison between our STIL paper methodology and
the current state of the art in lexical semantic change detection (LSCD). The goal
is to identify what we do correctly, what gaps exist, and what a knowledgeable
reviewer might flag.

Our paper: **Comparing Lexical, Static-Embedding, and Contextual Drift Signals in
Brazilian Portuguese Political Discourse**

---

## 1. Key Reference Papers

### 1.1 Foundational

- **Hamilton et al. (2016)** — *Diachronic Word Embeddings Reveal Statistical Laws
  of Semantic Change* (ACL 2016). Established Orthogonal Procrustes alignment for
  slice-specific Word2Vec models. This is the basis of our Word2Vec pipeline.
  - URL: https://aclanthology.org/P16-1141/

- **Kutuzov et al. (2018)** — *Diachronic word embeddings and semantic shifts: a
  survey* (COLING 2018). Comprehensive survey of static embedding methods for
  diachronic analysis. Covers SGNS, PPMI, alignment techniques, evaluation.
  - URL: https://aclanthology.org/C18-1117/

- **Tahmasebi et al. (2021)** — *Computational Approaches to Semantic Change*
  (Language Science Press). Book-length overview of the field including methods,
  evaluation, and applications.
  - DOI: 10.5281/zenodo.5040241

### 1.2 Shared Tasks and Evaluation

- **Schlechtweg et al. (2020)** — *SemEval-2020 Task 1: Unsupervised Lexical
  Semantic Change Detection*. The first major shared task for LSCD.
  - 33 teams, 186 systems
  - Two subtasks: binary classification (sense gain/loss) and graded ranking
  - Covers English, German, Latin, Swedish
  - Key finding: Skip-gram with Temporal Referencing achieved best results (66.5%
    accuracy, 51.8% Spearman)
  - BERT-based systems generally did NOT outperform static embeddings in this task
  - URL: https://aclanthology.org/2020.semeval-1.1/

- **Dubossarsky et al. (2019)** — *Time-Out: Temporal Referencing for Robust
  Modeling of Lexical Semantic Change* (ACL 2019). Showed that distributional
  pipelines can react to temporal artifacts and alignment noise.
  - URL: https://aclanthology.org/P19-1044/

### 1.3 Contextual Embeddings for Semantic Change

- **Giulianelli et al. (2020)** — *Analysing Lexical Semantic Change with
  Contextualised Word Representations* (ACL 2020). First unsupervised approach
  using BERT for LSCD.
  - Method: extract BERT embeddings → cluster into usage types → measure change
    with three metrics
  - Created a new evaluation dataset
  - Showed positive correlation with human judgments
  - URL: https://aclanthology.org/2020.acl-main.365/

- **Montariol et al. (2021)** — *Scalable and Interpretable Semantic Change
  Detection* (NAACL 2021). Proposed scalable clustering of BERT embeddings.
  - Uses K-means clustering on BERT embeddings
  - Primary metric: Jensen-Shannon Divergence (JSD) between sense distributions
  - Demonstrated on COVID-19 news corpus
  - Addresses scalability issues of prior clustering approaches
  - URL: https://aclanthology.org/2021.naacl-main.369/

- **Laicher et al. (2021)** — *Explaining and Improving BERT Performance on Lexical
  Semantic Change Detection* (EACL 2021 SRW). Critical paper on why BERT
  underperforms.
  - Found that BERT's low performance is largely due to **orthographic information**
    on the target word, encoded even in higher layers
  - By reducing orthographic influence, they considerably improved BERT's performance
  - Raises the question of why token-based models (BERT) did not translate their
    success on other NLP tasks to LSCD
  - URL: https://aclanthology.org/2021.eacl-srw.25/

- **Laicher et al. (2020)** — *CL-IMS @ DIACR-Ita: Volente o Nolente: BERT does
  not outperform SGNS on Semantic Change Detection*.
  - Used Average Pairwise Distance (APD) of token-based BERT embeddings
  - Could not find robust ways to exploit BERT embeddings for LSCD
  - BERT achieved 0.72 accuracy on Italian data (5th of 8 participants)
  - Title is a direct statement: BERT does not outperform SGNS
  - URL: https://arxiv.org/abs/2011.07247

### 1.4 Systematic Comparisons and Surveys

- **Cassotti et al. (2024)** — *A Systematic Comparison of Contextualized Word
  Embeddings for Lexical Semantic Change* (submitted NAACL 2024).
  - **Most directly comparable to our work in spirit**
  - Compared: BERT, mBERT, XLM-R, XL-LEXEME, GPT-4
  - Evaluated across 8 languages on standardized benchmarks
  - Three tasks: Word-in-Context (WiC), Word Sense Induction (WSI), Graded Change
    Detection (GCD)
  - URL: https://arxiv.org/html/2402.12011

  Key findings:
  - **APD dominates GCD**: Form-based approaches (APD) substantially outperform
    sense-based ones (JSD on clusters). APD achieved weighted average correlation
    of .751 across benchmarks.
  - **Early/mid layers work better**: "Using early layers consistently results in
    higher performance." Optimal at layers 8–10, not the final layer. No benefit
    from concatenating last four layers.
  - **XL-LEXEME superiority**: Consistently exceeded BERT, mBERT, XLM-R across
    all tasks.
  - **GPT-4 comparable but expensive**: Matched XL-LEXEME performance but authors
    call its cost "unjustifiable" vs. smaller open-source models.
  - **Sense-based limitations**: Low WSI and GCD performance raises concerns about
    whether clustering methods "capture meaningful patterns or produce noisy
    aggregation."
  - **Critical recommendation**: Focus should shift from merely quantifying change
    magnitude to understanding "how, when, and why" meanings change.

- **Survey on Contextualised Semantic Shift Detection (2023)** — Comprehensive
  survey covering form-based vs. sense-based paradigms.
  - URL: https://arxiv.org/pdf/2304.01666
  - Establishes three dimensions: meaning representation (form vs. sense),
    time-awareness (oblivious vs. aware), learning modality (supervised vs.
    unsupervised)
  - Most successful recent work remains time-oblivious and unsupervised

- **Rachinskiy & Schlechtweg (2025)** — *Rethinking Metrics for Lexical Semantic
  Change Detection*.
  - Introduces AMD (Average Minimum Distance) and SAMD (Symmetric Average Minimum
    Distance)
  - Criticizes APD: "captures global divergence but is dominated by the bulk of
    points, making it less sensitive to small or emerging usage clusters"
  - Criticizes PRT (prototype/centroid): "reduces representations to a single point,
    potentially obscuring sense-specific changes"
  - Both APD and PRT "aggregate information globally, which can obscure localised
    phenomena such as the emergence of a new sense"
  - Recommends pairing metrics with PCA dimensionality reduction
  - AMD and SAMD are "complementary additions, not replacements"
  - URL: https://arxiv.org/html/2602.15716

- **LLMs on Lexical Semantic Change Detection (2023)** — Evaluation of GPT-4 vs.
  BERT vs. traditional methods.
  - Dataset: TempoWiC (3,287 instances, 34 target words, tweets 2019–2021)
  - Corpus-level: GPT-4 r=−0.66, BERT r=0.63, SGNS r=0.47
  - Instance-level: GPT-4 72% accuracy, BERT 64%
  - Traditional methods "require a much larger corpus to take significant variations
    into account"
  - Prompt engineering dramatically affects LLM performance
  - URL: https://arxiv.org/html/2312.06002

### 1.5 Political Discourse

- **Hofmann et al. (2020)** — *Comparing Lexical Usage in Political Discourse
  across Diachronic Corpora* (ParlaClarin 2020). Compared lexical usage in Austrian
  political discourse across time.
  - URL: https://aclanthology.org/2020.parlaclarin-1.11/

- **Zeng et al. (2024)** — *Achieving Semantic Consistency: Contextualized Word
  Representations for Political Text Analysis*.
  - Compared Word2Vec and BERT using 20 years of People's Daily articles
  - BERT outperforms Word2Vec in maintaining semantic stability
  - Word2Vec better for long-term changes but suffers from embedding fluctuations
    with unbalanced data
  - Word2Vec aligned with Orthogonal Procrustes (same as our approach)
  - URL: https://arxiv.org/abs/2412.04505

- **Greek Parliament Proceedings Dataset (NeurIPS 2022)** — Curated diachronic
  dataset from parliamentary proceedings spanning decades.
  - URL: https://proceedings.neurips.cc/paper_files/paper/2022/file/b96ce67b2f2d45e4ab315e13a6b5b9c5-Paper-Datasets_and_Benchmarks.pdf

---

## 2. Methodology Comparison: Our Paper vs. the Field

### 2.1 What We Do Correctly

| Aspect | Our approach | Literature support |
|--------|-------------|-------------------|
| Multi-method comparison | TF-IDF, Word2Vec, BERT on same panel | Cassotti et al. 2024 does similar systematic comparison; field recognizes no single method dominates |
| Orthogonal Procrustes alignment | Top 20K anchors per Hamilton et al. | Standard since 2016, widely used |
| Shared comparison panel with stable controls | 55 lemmas: 15 W2V + 15 TF-IDF + 20 stable + 5 theory seeds | Novel contribution; permutation-based controls increasingly recommended |
| Exploratory framing (no ground-truth claims) | Explicit in abstract, conclusion, limitations | Best practice for corpora without gold annotations |
| Cost/complexity comparison | Relative ratios (1×, ~56×, ~600×) | Cassotti et al. 2024 make same argument about GPT-4 vs. XL-LEXEME |
| BERT not outperforming Word2Vec | Our finding: modest 0.21 correlation | Validated by Laicher et al. 2020/2021, SemEval-2020 results |
| Disagreement as informative signal | Core contribution | Increasingly recognized in the field |
| Portuguese political discourse | Underrepresented in literature | Only Hofmann (Austrian), Zeng (Chinese), Greek Parliament exist; no Brazilian Portuguese |

### 2.2 Methodological Gaps

#### Gap 1: BERT Distance Metric — Centroid Cosine vs. APD (HIGH)

**What we do**: Mean cosine distance between slice-level centroid embeddings
(PRT/prototype approach).

**What the field recommends**: Average Pairwise Distance (APD) is now the dominant
metric for LSCD with contextual embeddings.

**Evidence**:
- Cassotti et al. (2024): APD achieves .751 weighted correlation vs. lower for PRT
  on GCD benchmarks across 8 languages
- Rachinskiy & Schlechtweg (2025): PRT "reduces representations to a single point,
  potentially obscuring sense-specific changes"
- The centroid approach compresses all usages into a single vector per slice, which
  **loses the polysemy information** that makes contextual models valuable over
  static ones
- Newer AMD/SAMD metrics offer further improvements but are very recent (2025)

**Risk**: A reviewer familiar with LSCD literature could argue that our centroid-based
approach underestimates BERT's discriminative power, making the comparison with
Word2Vec unfair to BERT.

**Mitigation**: Acknowledge in Limitations that we use centroid-based aggregation
rather than APD, and note this may underestimate BERT's full potential. Our
conclusion (BERT adds modest value) is actually conservative, which is defensible.

#### Gap 2: BERT Layer Choice — Layer −1 vs. Mid-Layers (MEDIUM)

**What we do**: Extract layers −1 and −4, designate −1 as "preferred."

**What the field recommends**: Mid-range layers (8–10 in a 12-layer model, or
equivalently layers −4 to −16 in a 24-layer model) often perform better.

**Evidence**:
- Cassotti et al. (2024): "using early layers consistently results in higher
  performance," optimal at layers 8–10
- Laicher et al. (2021): higher layers encode orthographic bias that hurts LSCD
- Our model (`rufimelo/bert-large-portuguese-cased-sts`) has 24 layers, so layer
  −1 = layer 24 (final) and layer −4 = layer 21. Both are in the "higher" range
  that the literature suggests may be suboptimal.

**Mitigation**: Our layer agreement analysis (Spearman 0.858 between −1 and −4)
already shows the broad picture is stable across extraction depths. We could note
that this consistency aligns with the recommendation to consider mid-range layers,
and that future work could explore earlier layers.

#### Gap 3: No Sense-Based / Clustering Approach (MEDIUM)

**What we do**: Purely form-based (centroid distance). We never cluster BERT
embeddings into discrete senses.

**What the field offers**:
- Giulianelli et al. (2020): cluster BERT embeddings → measure change via JSD
  between sense distributions
- Montariol et al. (2021): scalable K-means clustering + JSD
- Sense-based approaches can distinguish *which* sense changed and detect emergence
  of new senses

**However**: Cassotti et al. (2024) showed that form-based APD actually outperforms
sense-based JSD on graded change detection benchmarks. So the absence of clustering
is not inherently a weakness for our task (ranking words by degree of change).

**Mitigation**: Mention in Limitations or future work. Not fatal for an exploratory
comparison paper.

#### Gap 4: No Orthographic Bias Mitigation (LOW-MEDIUM)

**What we do**: Use BERT embeddings as-is.

**What the field recommends**: Laicher et al. (2021) showed BERT encodes the target
word's surface form even in higher layers, causing spurious similarity between
occurrences of the same word regardless of meaning. Techniques to reduce this
include:
- Masking the target token before extracting embeddings
- Averaging only subword tokens excluding the target
- Using models fine-tuned to reduce orthographic bias (e.g., XL-LEXEME)

**Mitigation**: This is a known issue but addressing it would require re-running the
BERT pipeline. Worth mentioning in Limitations as a direction for future work.

#### Gap 5: Context Sample Size (LOW)

**What we do**: Up to 64 occurrences per lemma per slice.

**What the field uses**: Varies widely. Some studies use 100–200+ contexts. With
24 slices and many of our lemmas being high-frequency political terms, 64 may
introduce variance but is not unusually low.

**Mitigation**: Acceptable for an exploratory study. Could mention in Limitations.

#### Gap 6: No Comparison with XL-LEXEME or Specialized Models (LOW)

**What we do**: Use `rufimelo/bert-large-portuguese-cased-sts`.

**What the field offers**: XL-LEXEME (Cassotti et al. 2024) consistently
outperforms vanilla BERT. However, XL-LEXEME is English-focused and there may not
be a Portuguese equivalent.

**Mitigation**: Our paper's contribution is the Portuguese political setting and
the three-way comparison, not state-of-the-art BERT performance. A reviewer might
mention this but it's not a fatal flaw for our framing.

### 2.3 Comparison of Distance Metrics Across the Field

| Metric | Type | Used by | Strengths | Weaknesses |
|--------|------|---------|-----------|------------|
| **Cosine distance between centroids (PRT)** | Form-based | **Our paper**, early LSCD work | Simple, fast, interpretable | Compresses all usages to one point; loses polysemy info |
| **Average Pairwise Distance (APD)** | Form-based | Laicher et al. 2020, Cassotti et al. 2024, many SemEval systems | Exploits full usage distribution; best GCD performance | Dominated by bulk of points; sensitive to outliers |
| **Jensen-Shannon Divergence (JSD)** | Sense-based | Giulianelli et al. 2020, Montariol et al. 2021 | Captures sense emergence/loss; interpretable clusters | Requires clustering; noisy; underperforms APD on GCD |
| **AMD / SAMD** | Form-based | Rachinskiy & Schlechtweg 2025 | Local correspondence; sensitive to emerging senses | Very recent (2025); limited adoption |
| **Cosine distance (Word2Vec)** | Static | **Our paper**, Hamilton et al. 2016 | Standard for aligned static embeddings | Single vector per word; no polysemy |
| **Mean absolute TF-IDF change** | Lexical | **Our paper** | Extremely cheap; captures salience shifts | No semantic content; purely distributional |

### 2.4 BERT Layer Recommendations from the Literature

| Study | Model | Recommended layers | Notes |
|-------|-------|--------------------|-------|
| Cassotti et al. 2024 | BERT-base (12 layers) | Layers 8–10 | "early layers consistently result in higher performance" |
| Laicher et al. 2021 | BERT-base (12 layers) | Avoid final layers | Higher layers encode orthographic bias |
| Contextual survey 2023 | Various | Last layer most common; last-4 sum also used | No strong consensus |
| **Our paper** | bert-large (24 layers) | Layer −1 (=24) preferred, −4 (=21) robustness | Both in the "higher" range the literature warns about |

---

## 3. Summary of What a Reviewer Might Flag

### Likely to be flagged

1. **Centroid-based BERT aggregation instead of APD**: This is the most well-known
   methodological distinction in the current LSCD literature. A reviewer who knows
   the field will notice we use PRT rather than APD.

2. **Final-layer preference**: The recommendation to use mid-layers is increasingly
   well-known. Our use of layer −1 as "preferred" goes against this.

### Possibly flagged

3. **No clustering / sense-based analysis**: Less critical since APD (also
   form-based) outperforms sense-based methods, but some reviewers value the
   interpretability of sense clusters.

4. **No orthographic bias mitigation**: Known issue since 2021, though not always
   addressed in applied work.

### Unlikely to be flagged

5. **Context sample size**: 64 is reasonable for an exploratory study.
6. **No XL-LEXEME**: Too new and not available for Portuguese.
7. **Word2Vec / TF-IDF methodology**: Both are standard and well-executed.

---

## 4. Recommended Paper Edits

### High Priority (add to Limitations)

Add one sentence acknowledging that our contextual stage uses centroid-based cosine
distance (PRT) rather than Average Pairwise Distance (APD), which has become the
dominant metric for contextual LSCD. Note that this design choice may underestimate
BERT's full discriminative power over the shared panel.

### Medium Priority (add to Discussion)

Add one sentence noting that our layer −4 results' consistency with layer −1
(Spearman 0.858) is encouraging, and that recent literature suggests mid-range
layers may offer further improvements for contextual change detection.

### Low Priority (optional additions to Future Work)

- Mention sense-based clustering (JSD) as an alternative contextual approach
- Mention orthographic bias mitigation techniques
- Mention specialized models like XL-LEXEME if Portuguese-adapted versions become
  available

---

## 5. What the Literature Validates About Our Contribution

Despite the gaps above, several of our core findings are well-supported:

1. **BERT not outperforming Word2Vec is a known result**, not a pipeline failure.
   Multiple papers (Laicher 2020, SemEval-2020 results) confirm this pattern.

2. **Multi-method comparison on understudied languages is valuable.** The field
   overwhelmingly uses English, German, Latin, and Swedish. Brazilian Portuguese
   political discourse is genuinely underrepresented.

3. **Cost-vs-benefit analysis is a real contribution.** Cassotti et al. (2024)
   make the same argument about GPT-4 vs. smaller models. Our version for
   TF-IDF vs. Word2Vec vs. BERT is in the same practical spirit.

4. **Disagreement between methods is informative.** The field is moving away from
   seeking a single "best" detector and toward understanding what different methods
   capture.

5. **Exploratory framing without gold-standard claims is appropriate.** The field
   explicitly recognizes that most real-world corpora lack external labels.

---

## 6. Additional References Not Currently in Our Bibliography

These papers are relevant but not currently cited in our manuscript:

- Cassotti et al. (2024). *A Systematic Comparison of Contextualized Word
  Embeddings for Lexical Semantic Change.* https://arxiv.org/abs/2402.12011
- Laicher et al. (2021). *Explaining and Improving BERT Performance on Lexical
  Semantic Change Detection.* EACL 2021 SRW.
  https://aclanthology.org/2021.eacl-srw.25/
- Laicher et al. (2020). *CL-IMS @ DIACR-Ita: BERT does not outperform SGNS on
  Semantic Change Detection.* https://arxiv.org/abs/2011.07247
- Rachinskiy & Schlechtweg (2025). *Rethinking Metrics for Lexical Semantic Change
  Detection.* https://arxiv.org/abs/2602.15716
- Zeng et al. (2024). *Achieving Semantic Consistency: Contextualized Word
  Representations for Political Text Analysis.* https://arxiv.org/abs/2412.04505
- Periti & Montanelli (2023). *A Survey on Contextualised Semantic Shift Detection.*
  https://arxiv.org/abs/2304.01666

Whether to add any of these to the paper depends on page budget and whether the
Limitations additions reference them explicitly.
