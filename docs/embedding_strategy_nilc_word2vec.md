# NILC Word2Vec Strategy Note

## Question

Should we use the Hugging Face model [`nilc-nlp/word2vec-skip-gram-300d`](https://huggingface.co/nilc-nlp/word2vec-skip-gram-300d) in the current N2 drift-technique comparison?

Short answer:

- **Yes** as a **Portuguese static-embedding reference and design inspiration**
- **No** as the **direct diachronic model**

The right interpretation for the current paper is:

- keep Word2Vec as one method family in the comparison
- adopt a **NILC-style setup**
- train a separate Word2Vec Skip-Gram 300d model for each time slice on our own corpora
- align slices with **Orthogonal Procrustes**

## What the official NILC model actually is

According to the official Hugging Face model card, `nilc-nlp/word2vec-skip-gram-300d` is:

- a **static** Portuguese Word2Vec Skip-Gram model
- **300 dimensions**
- trained on a **large mixed Portuguese corpus**
- covering **Brazilian + European Portuguese**
- built from **17 corpora**
- totaling about **1.39B tokens**

Official source:

- [Hugging Face model card](https://huggingface.co/nilc-nlp/word2vec-skip-gram-300d)

The model card also links the underlying paper:

- Hartmann et al. (2017), *Portuguese Word Embeddings: Evaluating on Word Analogies and Natural Language Tasks*
- [ACL Anthology / STIL 2017](https://aclanthology.org/W17-6615.pdf)

## What this means for us

This NILC model is **not diachronic**. It is one single static embedding space trained on a pooled corpus. That means:

- it is useful for Portuguese lexical semantics in general
- it is **not** enough to measure drift over time by itself
- it does **not** preserve our corpus-specific temporal signal

For N2, the time information has to come from the training setup itself. In practice, that means training:

- one embedding model per year or per semester
- on `BrPoliCorpus floor`
- and optionally one per period on `Roda Viva`

Then we compare those time-specific spaces against other method families such as `TF-IDF` and contextual `BERT`.

## What the literature says

### 1. Skip-Gram 300d is a sensible choice

Hartmann et al. (2017) is the main Portuguese reference here.

- It evaluates several Portuguese embedding families.
- It shows that **300d** is a strong practical choice.
- It also argues that dimensions larger than 300 often do not justify the extra memory cost.

Source:

- [Hartmann et al. 2017](https://aclanthology.org/W17-6615.pdf)

This supports your idea of using a **300d Portuguese Word2Vec setup**.

### 2. Alignment-based diachronic embeddings are standard, but noisy

Hamilton, Leskovec, and Jurafsky (2016) is the foundational reference for aligned diachronic embeddings.

- It supports training embeddings per time slice and comparing them across time.
- It is the main citation behind the standard diachronic Word2Vec approach.

Source:

- [Hamilton et al. 2016](https://aclanthology.org/P16-1141.pdf)

But later work warns us to be careful:

- Dubossarsky et al. (2019) shows that **alignment can introduce noise**
- Antoniak and Mimno (2018) shows that embeddings can be unstable across runs, especially on smaller corpora

Sources:

- [Dubossarsky et al. 2019](https://aclanthology.org/P19-1044.pdf)
- [Antoniak and Mimno 2018](https://aclanthology.org/Q18-1008/)

So the method is valid, but it needs robustness checks.

### 3. Portuguese-specific static embeddings are useful, but not a replacement for temporal training

The official NILC model card and the Hartmann et al. paper support the idea that Portuguese-specific static embeddings are high-quality resources.

However, nothing in those sources suggests that a single pretrained static embedding should replace time-sliced diachronic training for semantic-change detection.

That would collapse the temporal variation we are trying to measure.

## My recommendation

### Best use of the NILC model

Use it as:

- a **Portuguese baseline/reference embedding**
- a **sanity-check resource** for nearest neighbors and lexical quality
- a **methodological justification** for using Portuguese-specific Skip-Gram 300d

Do **not** use it as:

- the direct embedding space for semantic change measurement
- an initialization that all time slices inherit from by default

## Why I would avoid using the NILC model as initialization

At first glance, initializing each time slice from the NILC model may sound attractive.

I do **not** recommend making that the default approach, because it can blur the signal we care about:

- the NILC model is trained on a pooled multi-genre corpus, not our specific temporal corpora
- its vocabulary and geometry reflect mixed Portuguese usage, not `BrPoliCorpus floor` or `Roda Viva`
- shared initialization may reduce apparent drift and make slices artificially similar

For our paper, the cleaner design is:

- train each slice on its own corpus data
- align afterward
- measure drift

That is easier to justify and more faithful to the literature.

## Best practical experiment design

If we want a strong first implementation, I would do this:

1. Preprocess each corpus slice consistently.
2. Keep only content words or at least mark them clearly for later filtering.
3. Train **Word2Vec Skip-Gram 300d** separately for each slice.
4. Use the same training recipe across slices.
5. Align adjacent or all slices with **Orthogonal Procrustes**.
6. Compute drift scores.
7. Repeat training **3 times** to test stability.
8. Use `rufimelo/bert-large-portuguese-cased-sts` only on the final candidate words as a confirmatory analysis.

## Concrete recommendation for our project

### Main experiment

- `BrPoliCorpus floor`
- yearly slices
- Word2Vec Skip-Gram 300d
- Orthogonal Procrustes alignment

### First robustness check

- same pipeline on semester slices for frequent words only

### Complementary experiment

- `Roda Viva V0-2`
- yearly slices
- smaller candidate set

### Confirmatory model

- `rufimelo/bert-large-portuguese-cased-sts`
- only for selected drift words, stable controls, and seeds

## Final judgement

Your idea is **good**, with one correction:

- **good idea**: use **NILC-style Portuguese Skip-Gram 300d**
- **correction**: do **not** rely on the single pretrained NILC static model as the diachronic representation itself

So the best formulation is:

> We use a Portuguese-specific static-embedding design inspired by NILC Word2Vec Skip-Gram 300d, but train embeddings separately for each temporal slice of our corpora and align them with Orthogonal Procrustes for semantic-change analysis.

That would be methodologically much stronger.

## Sources

- [Hugging Face NILC model card](https://huggingface.co/nilc-nlp/word2vec-skip-gram-300d)
- [Hartmann et al. 2017](https://aclanthology.org/W17-6615.pdf)
- [Hamilton et al. 2016](https://aclanthology.org/P16-1141.pdf)
- [Dubossarsky et al. 2019](https://aclanthology.org/P19-1044.pdf)
- [Antoniak and Mimno 2018](https://aclanthology.org/Q18-1008/)
