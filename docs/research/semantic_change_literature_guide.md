# Semantic Change And Drift-Technique Literature Guide

## Purpose

This note collects the papers and dataset references that give the strongest methodological and experimental basis for the current N2 paper on **drift-technique comparison in Portuguese political discourse**.

The goal is not only to find papers to cite later, but also to identify:

- which method families are most useful for our setting
- which robustness checks are expected in the literature
- which Portuguese resources and benchmarks matter most
- which papers are most similar to the experiment we are actually planning

## Current Experiment We Need To Support

Our current design is:

- main corpus: `BrPoliCorpus floor`
- complementary corpus: `Roda Viva V0-2`
- main task: compare drift signals across multiple technique families on Portuguese political discourse
- main methods: `TF-IDF`, Word2Vec Skip-Gram by time slice + alignment, and contextual `BERT`
- optional support layer: symbolic or lexical-feature analysis, potentially using selected `NILC-Metrix` measures
- main granularity: yearly
- first robustness check: semester

Because of that, the most important literature is not generic Portuguese NLP. It is specifically literature on:

1. lexical and concept drift in temporal corpora
2. embedding alignment and robustness
3. contextual drift methods
4. count/profile baselines and simpler lexical representations
5. Portuguese historical or temporal resources
6. corpora similar to ours in time structure, genre, or interpretability

## Recommended Citation Backbone

If we want a compact but strong methodological backbone, these are the highest-priority references:

1. Hamilton, Leskovec, and Jurafsky (2016)
2. Dubossarsky et al. (2019)
3. Schlechtweg et al. (2020)
4. Antoniak and Mimno (2018)
5. Giulianelli, Del Tredici, and Fernandez (2020)
6. Periti and Tahmasebi (2024)
7. Tian et al. (2021) BAHP
8. Souza, Nogueira, and Lotufo (2020) BERTimbau
9. de Miranda Jr. et al. (2024) Roda Viva boundaries
10. BrPoliCorpus dataset DOI

## How To Use This Guide Now

The current paper should not use this literature guide to argue that one method is objectively correct on unlabeled data.

Instead, use it to support:

- why each technique family is a legitimate comparison point
- why method instability and disagreement matter
- why corpus-specific interpretation is necessary
- why Portuguese resources and political discourse are worth studying on their own terms

One practical extension for this paper is to use selected `NILC-Metrix` features as a symbolic support layer. Those features are more useful for interpreting rhetorical, stylistic, cohesion, or complexity shifts than for replacing the main drift detectors.

## Papers and Resources

### 1. Foundational diachronic semantic change methods

#### Hamilton, Leskovec, and Jurafsky (2016)

- Category: Foundational method
- Reference: *Diachronic Word Embeddings Reveal Statistical Laws of Semantic Change*
- Link: [ACL Anthology](https://aclanthology.org/P16-1141.pdf)
- Why it matters: This is one of the core papers behind embedding-based semantic change detection. It compares several approaches and helps justify aligned diachronic embeddings as a serious methodology.
- Brief summary: The paper evaluates diachronic embeddings against attested semantic changes and proposes broad regularities relating frequency and polysemy to semantic change.
- How we can use it: This is the main citation for the basic idea of training embeddings per time slice and comparing word vectors across time. It supports our Word2Vec-based main pipeline and gives us language for explaining why semantic change can be operationalized distributionally.

#### Kulkarni, Al-Rfou, Perozzi, and Skiena (2015)

- Category: Foundational method / change-point framing
- Reference: *Statistically Significant Detection of Linguistic Change*
- Link: [arXiv](https://arxiv.org/abs/1411.3315)
- Why it matters: This paper is important if we later want to discuss time-series style change detection rather than only ranking global drift.
- Brief summary: The authors build time series of linguistic properties and use statistical change-point detection to identify significant shifts in meaning and usage.
- How we can use it: We do not need to copy their full pipeline, but it is useful if we want to justify event-sensitive analysis, local change bursts, or a later extension from yearly drift ranking to change-point analysis for selected words.

#### Dubossarsky, Hengchen, Tahmasebi, and Schlechtweg (2019)

- Category: Foundational method / robustness against alignment noise
- Reference: *Time-Out: Temporal Referencing for Robust Modeling of Lexical Semantic Change*
- Link: [ACL Anthology](https://aclanthology.org/P19-1044.pdf)
- Why it matters: This is one of the most relevant cautionary papers for our experiment.
- Brief summary: The paper argues that alignment-based semantic change models can be noisy and proposes temporal referencing as a more robust alternative in some settings.
- How we can use it: Even if we keep aligned Word2Vec as the main method, this paper helps us discuss alignment noise honestly and motivates our robustness checks. It is especially useful in the methods and limitations sections.

#### Schlechtweg, McGillivray, Hengchen, Dubossarsky, and Tahmasebi (2020)

- Category: Evaluation benchmark / task framing
- Reference: *SemEval-2020 Task 1: Unsupervised Lexical Semantic Change Detection*
- Link: [ACL Anthology](https://aclanthology.org/2020.semeval-1.1.pdf)
- Why it matters: This is the most visible shared-task reference in lexical semantic change detection.
- Brief summary: The paper defines benchmark tasks and datasets for unsupervised lexical semantic change detection and highlights the evaluation challenges of the field.
- How we can use it: This supports the broader framing of the task and gives us a reference point for how the community defines lexical semantic change detection. It is also useful when explaining why manual validation of candidate words is still necessary.

### 2. Contextual and neural semantic change methods

#### Giulianelli, Del Tredici, and Fernandez (2020)

- Category: Contextual semantic change method
- Reference: *Analysing Lexical Semantic Change with Contextualised Word Representations*
- Link: [ACL Anthology](https://aclanthology.org/2020.acl-main.365.pdf)
- Why it matters: This is one of the clearest references for using contextual embeddings rather than static embeddings in lexical semantic change.
- Brief summary: The paper uses BERT-based contextualized representations, clusters usage instances, and measures change over time with metrics that correlate with human judgements.
- How we can use it: This is the strongest citation for our confirmatory `BERTimbau` analysis. It supports using contextual embeddings on the final selected words instead of on the whole vocabulary from the start.

#### Martinc, Kralj Novak, and Pollak (2020)

- Category: Contextual semantic change method
- Reference: *Leveraging Contextual Embeddings for Detecting Diachronic Semantic Shift*
- Link: [ACL Anthology](https://aclanthology.org/2020.lrec-1.592.pdf)
- Why it matters: This is especially relevant because it shows contextual methods being used on shorter and domain-specific timelines.
- Brief summary: The paper builds time-specific representations from BERT embeddings and shows that contextual embeddings can work well for yearly semantic shift detection, including multilingual settings.
- How we can use it: This is a good citation for arguing that contextual models can be useful even without enormous historical corpora. It fits our confirmatory use of `BERTimbau` on selected Portuguese words in `Roda Viva` and `BrPoliCorpus`.

#### Periti and Tahmasebi (2024)

- Category: Contextual semantic change comparison
- Reference: *A Systematic Comparison of Contextualized Word Embeddings for Lexical Semantic Change*
- Link: [ACL Anthology](https://aclanthology.org/2024.naacl-long.240.pdf)
- Why it matters: This is the best recent paper for not overclaiming with contextual methods.
- Brief summary: The paper compares contextualized approaches under controlled settings and shows that performance depends strongly on setup, task decomposition, and evaluation conditions.
- How we can use it: This supports using contextual embeddings as a focused secondary analysis rather than as the only method. It also helps justify why we want a simple main method plus a carefully bounded confirmatory contextual analysis.

#### Souza, Nogueira, and Lotufo (2020)

- Category: Portuguese contextual model resource
- Reference: *BERTimbau: Pretrained BERT Models for Brazilian Portuguese*
- Link: [Springer](https://link.springer.com/chapter/10.1007/978-3-030-61377-8_28)
- Why it matters: This is the canonical citation for `BERTimbau`.
- Brief summary: The authors present pretrained BERT models for Brazilian Portuguese and show that they outperform multilingual baselines on several downstream tasks.
- How we can use it: We should cite this whenever we use `BERTimbau` for contextual representations. It supports our claim that the confirmatory contextual analysis is Portuguese-specific rather than relying on generic multilingual models.

### 3. Robustness, instability, and practical safeguards

#### Antoniak and Mimno (2018)

- Category: Embedding stability / robustness
- Reference: *Evaluating the Stability of Embedding-based Word Similarities*
- Link: [ACL Anthology](https://aclanthology.org/Q18-1008/)
- DOI: `10.1162/tacl_a_00008`
- Why it matters: This paper is directly relevant to our decision to rerun Word2Vec multiple times.
- Brief summary: The authors show that embedding neighborhoods and distances can vary substantially across runs, especially on smaller corpora.
- How we can use it: This is the main reference for our robustness check of training Word2Vec multiple times. It supports the idea that we should not trust one run blindly, especially for `Roda Viva`, which is much smaller than `BrPoliCorpus floor`.

#### Englhardt, Willkomm, Schaler, and Bohm (2020)

- Category: Drift scoring / frequency-aware analysis
- Reference: *Improving Semantic Change Analysis by Combining Word Embeddings and Word Frequencies*
- Link: [Author PDF](https://dbis.ipd.kit.edu/download/SCAF_IJDL19_Englhardt.pdf)
- DOI: `10.1007/s00799-019-00271-6`
- Why it matters: This paper is very relevant to our candidate ranking and selection strategy.
- Brief summary: The paper argues that semantic drift analysis improves when embedding-based signals are combined with frequency information rather than treated in isolation.
- How we can use it: This supports adding simple frequency-aware sanity checks to drift ranking. We do not need to reproduce their full method, but the paper helps justify why we should inspect frequency shifts alongside embedding shifts.

#### Nicholson, Alquaddoomi, Rubinetti, and Greene (2023)

- Category: Multi-run robustness / temporal modeling practice
- Reference: *Changing word meanings in biomedical literature reveal pandemics and new technologies*
- Link: [BMC Bioinformatics](https://doi.org/10.1186/s13040-023-00332-2)
- Why it matters: The domain is different, but the methodological lesson is very useful.
- Brief summary: The paper trains multiple Word2Vec models per year, aligns them, and explicitly separates inter-year change from intra-year instability.
- How we can use it: This is a strong practical citation for our decision to rerun models and not interpret raw distances without checking model variability. It is especially useful if we want to justify stability-aware drift scores or repeated training.

### 4. Portuguese resources and corpus-specific references

#### Tian, Jarrett, Escalona Torres, and Amaral (2021)

- Category: Portuguese historical embedding evaluation
- Reference: *BAHP: Benchmark of Assessing Word Embeddings in Historical Portuguese*
- Link: [ACL Anthology](https://aclanthology.org/2021.latechclfl-1.13.pdf)
- Why it matters: This is one of the most directly relevant Portuguese papers for our project.
- Brief summary: The paper introduces a benchmark for evaluating word embeddings in historical Portuguese using analogy, similarity, outlier detection, and coherence tests.
- How we can use it: This helps us justify intrinsic evaluation of Portuguese diachronic embeddings. Even if our corpora are modern and not historical in the same sense, BAHP is still useful for motivating Portuguese-specific embedding quality checks.

#### Osorio and Cardoso (2024/2025)

- Category: Portuguese corpus landscape / resource survey
- Reference: *Historical Portuguese corpora: a survey*
- Link: [Springer](https://link.springer.com/article/10.1007/s10579-024-09757-5)
- Why it matters: This is the strongest broad survey for Portuguese historical corpora.
- Brief summary: The paper surveys historical Portuguese corpora, detailing coverage, accessibility, and thematic scope.
- How we can use it: This is useful in related work and dataset motivation. It helps position our choice of `Roda Viva` and `BrPoliCorpus` within the broader Portuguese corpus landscape and supports claims about resource scarcity.

#### de Miranda Jr., Wick-Pedro, de Barros, and Vale (2024)

- Category: Corpus resource
- Reference: *Roda Viva boundaries: an overview of an audio-transcription corpus*
- Link: [ACL Anthology](https://aclanthology.org/2024.propor-2.22/)
- Why it matters: This is the key paper for the corpus we are already using.
- Brief summary: The paper presents the `Roda Viva` corpus, its transcription layers, and the distinction between cleaner and more speech-faithful representations.
- How we can use it: This is the main citation for `Roda Viva`, especially for explaining why `V0-2` is the right analysis layer. It also helps us describe the corpus as a resource rather than only as a locally collected dataset.

#### Lima-Lopes (2025 dataset citation)

- Category: Corpus resource
- Reference: *BrPoliCorpus: Brazilian political corpus*
- Link: [Unicamp dataset DOI page](https://redu.unicamp.br/dataset.xhtml?persistentId=doi%3A10.25824%2Fredu%2FYCFPIV)
- DOI: `10.25824/redu/YCFPIV`
- Why it matters: This is the canonical citable reference we currently have for `BrPoliCorpus`.
- Brief summary: The dataset provides Brazilian political texts including floor speeches, committees, CPI material, inaugural speeches, and government programmes, with metadata and temporal coverage.
- How we can use it: This is the citation we should use for the main corpus itself. I did not find a dedicated peer-reviewed corpus paper as strong as the dataset DOI page, so the dataset citation is currently the safest reference.

### 5. Similar or adjacent applied papers

#### Tsakalidis, Bazzi, Cucuringu, Basile, and McGillivray (2019)

- Category: Similar applied study / web archive temporal corpus
- Reference: *Mining the UK Web Archive for Semantic Change Detection*
- Link: [ACL Anthology](https://aclanthology.org/R19-1139.pdf)
- Why it matters: This is useful because it deals with real temporal corpora outside the classic historical-book setup.
- Brief summary: The paper studies semantic change detection on a temporally structured web archive and discusses challenges around corpus quality and fine-grained temporal analysis.
- How we can use it: This supports our use of real-world temporal corpora rather than synthetic data. It is also helpful when discussing the tradeoff between temporal granularity and corpus noise.

#### Basile, Caputo, Caselli, Cassotti, and Varvara (2021)

- Category: Similar applied study / newspaper corpus
- Reference: *The Corpora They Are a-Changing: a Case Study in Italian Newspapers*
- Link: [ACL Anthology](https://aclanthology.org/2021.lchange-1.3.pdf)
- Why it matters: This is close to our setting in spirit: semantic change on a real, time-organized, public-discourse corpus.
- Brief summary: The paper studies lexical semantic change on newspaper corpora and highlights that benchmark behavior depends strongly on the corpus used to construct the evaluation setting.
- How we can use it: This is useful for justifying careful corpus-specific interpretation. It helps us argue that results on `BrPoliCorpus` and `Roda Viva` should be interpreted with respect to genre and corpus composition rather than as universal truth.

#### Garcia and Garcia-Salido (2019)

- Category: Multiword expressions / collocational change
- Reference: *A Method to Automatically Identify Diachronic Variation in Collocations*
- Link: [ACL Anthology](https://aclanthology.org/W19-4709.pdf)
- Why it matters: This is especially relevant if we keep multiword expressions in the paper.
- Brief summary: The paper proposes a method to track collocational variation over time and identify phraseological change in diachronic corpora.
- How we can use it: This is one of the best references if we want to study expressions such as `direitos humanos`, `reforma economica`, or `crise politica` instead of focusing only on isolated words. It gives direct support for a phrase-level analysis.

## What This Literature Suggests For Our Design

Across these papers, the most defensible version of our experiment looks like this:

1. Use **static embeddings as the main pipeline**.
   - Hamilton et al. gives the core basis.
   - Antoniak and Mimno warns us not to trust a single run.
   - Dubossarsky et al. reminds us to be careful with alignment noise.

2. Use **contextual embeddings as confirmation, not as the only method**.
   - Giulianelli et al. and Martinc et al. support this move.
   - Periti and Tahmasebi shows that contextual comparisons can be misleading if the setup is not controlled.
   - BERTimbau is the right Portuguese model citation for this part.

3. Keep **manual validation of candidate words**.
   - SemEval 2020 makes clear that evaluation is still a central problem in lexical semantic change.
   - This supports our planned manual inspection and annotator validation step.

4. Add **robustness checks based on repeated training and frequency-aware interpretation**.
   - Antoniak and Mimno supports repeated runs.
   - Nicholson et al. supports separating model instability from temporal drift.
   - Englhardt et al. supports checking frequency together with vector drift.

5. Cite **Portuguese resource papers explicitly**.
   - BAHP supports Portuguese embedding evaluation.
   - Historical Portuguese corpora survey helps with resource framing.
   - Roda Viva boundaries and the BrPoliCorpus dataset citation are necessary dataset references.

6. Consider a **small phrase-level component**.
   - Garcia and Garcia-Salido is the strongest methodological support for this if we decide to analyze multiword political expressions.

## Best Immediate Uses In Our Paper

### Methods section

Use:

- Hamilton et al. (2016)
- Dubossarsky et al. (2019)
- Antoniak and Mimno (2018)
- Giulianelli et al. (2020)
- Souza et al. (2020) for `BERTimbau`

### Dataset section

Use:

- de Miranda Jr. et al. (2024) for `Roda Viva`
- BrPoliCorpus dataset DOI
- Osorio and Cardoso (2024/2025) for Portuguese corpus context

### Evaluation and limitations section

Use:

- Schlechtweg et al. (2020)
- Periti and Tahmasebi (2024)
- Antoniak and Mimno (2018)
- Englhardt et al. (2020)

### If we include phrase-level analysis

Use:

- Garcia and Garcia-Salido (2019)

## My recommendation

For the first draft, I would treat the following as the most important references to read closely before running the final experiment:

1. Hamilton et al. (2016)
2. Dubossarsky et al. (2019)
3. Antoniak and Mimno (2018)
4. Giulianelli et al. (2020)
5. Periti and Tahmasebi (2024)
6. Tian et al. (2021) BAHP
7. Souza et al. (2020) BERTimbau
8. de Miranda Jr. et al. (2024) Roda Viva boundaries
9. BrPoliCorpus dataset citation

That set gives us a solid basis for:

- main method
- confirmatory method
- robustness checks
- Portuguese resource justification
- corpus citation

## Notes

- I found a strong citable dataset page for `BrPoliCorpus`, but I did **not** find a dedicated peer-reviewed corpus paper that looked stronger than citing the dataset DOI itself.
- I intentionally prioritized **primary sources** such as ACL Anthology, Springer, OpenReview, and dataset DOI pages.
- I did **not** include synthetic-drift-centered papers as the main basis, since that is not the paper we want to write.
