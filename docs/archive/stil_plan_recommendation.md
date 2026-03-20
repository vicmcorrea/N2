# STIL Plan Recommendation

## Recommendation

The best STIL paper direction is the **semantic-change-over-time line in Brazilian Portuguese**, with:

- **BrPoliCorpus floor speeches** as the main corpus
- **Roda Viva V0-2** as a complementary validation corpus
- **BrPoliCorpus inaugural speeches** as a small historical contrast set when useful

This is the strongest option because it:

- respects the advisor's request for a **new result line**
- does **not** reuse the submitted financial-disclosures article as the paper core
- gives a clean Portuguese-focused narrative
- now rests on audited datasets that are already organized and documented

## Current Corpus Decision

### Main corpus

**BrPoliCorpus `floor`**

Why:

- largest usable text volume
- exact dates from `2000-10-10` to `2023-12-21`
- strongest continuity for year-by-year and semester-level analysis
- best support for robust semantic-change experiments

Current data location:

- `Articles/N2/RawDatasets/BrPoliCorpus-Dataset/exports/floor`

### Complementary corpus

**Roda Viva `V0-2/csv`**

Why:

- exact interview dates from `1986-01-01` to `2009-10-19`
- richer dialogic language
- useful for qualitative interpretation and cross-corpus validation

Current data location:

- `Articles/N2/RawDatasets/Roda-Viva-Dataset/exports/V0-2/csv`

Metadata:

- `Articles/N2/RawDatasets/Roda-Viva-Dataset/exports/Metadata`

### Historical support corpus

**BrPoliCorpus `inaugural`**

Why:

- exact dates from `1889-11-15` to `2023-01-01`
- good for long-range historical contrast
- too small to be the main corpus

## Best Paper Framing

### Preferred framing

**Working title idea:** Semantic evolution of political vocabulary in Brazilian Portuguese

### Main contribution

- Track semantic drift of political vocabulary in Brazilian Portuguese over time.
- Show that a Portuguese-focused diachronic setup can recover interpretable changes in usage.
- Compare institutional political discourse and interview discourse without collapsing them into one undifferentiated corpus.

### Supporting contribution

- Use multi-word political expressions as an important secondary angle when they show clearer drift than isolated words.
- Use contextual models only as confirmatory or robustness analysis, not as the only signal.

## Core Experimental Shape

### Main setup

- Main corpus: `BrPoliCorpus floor`
- Main temporal granularity: **yearly**
- First finer-grained robustness check: **semester**

### Supporting setup

- Cross-corpus validation on `Roda Viva`
- Historical examples from `BrPoliCorpus inaugural`

### Word selection

Use the procedure documented in:

- `word_selection_protocol.md`

## What Not To Do

- Do not reuse the financial-disclosures article's main results, tables, or narrative.
- Do not pool BrPoliCorpus and Roda Viva into a single raw timeline without controlling for genre.
- Do not try to make month-level analysis the default unless term sparsity is explicitly checked first.

## Suggested Paper Structure

1. Introduction
2. Related work
3. Corpora and temporal setup
4. Word selection and semantic-change method
5. Results on BrPoliCorpus
6. Cross-corpus validation on Roda Viva
7. Discussion
8. Conclusion

## Minimal Submission Package

- one main semantic-change pipeline
- one main corpus
- one complementary validation corpus
- one clear word-selection protocol
- 3 to 4 strong figures
- 2 to 3 carefully interpreted qualitative examples

## Immediate Next Actions

1. Freeze the main corpus as `BrPoliCorpus floor`.
2. Freeze the complementary corpus as `Roda Viva V0-2`.
3. Implement the word-selection protocol.
4. Decide the main time slicing:
   - yearly as default
   - semester as robustness
5. Build a first candidate list of drift words, stable controls, and theory-driven seeds.
6. Start drafting the method and dataset sections directly in the cleaned STIL template in `Articles/N2/2026S1_STIL_conceptDrift`.

## Related Docs

- `project_overview.md`
- `research_readiness_datasets.md`
- `word_selection_protocol.md`
- `notes.md`
--------------------------

Make mean consecutive drift more clear

More than 1 drift technique, to see which is better and hows more correlation
Word embedding was almost same but almost same perf as bert which is heavy.
TF-IDF


Even if they are all same level of quality its good aswell.

Hard to analyze this dataset because there are no labels.

Comparisons with drift techniques.


try to defend that results whatever they are would be usefull in cotnext in it beween portguese and politiical.


talk about analyzing concept drift in political discourse if useful.

TRY TO FIND MOTIVAITON.

in portufese

https://pln.venturus.dev.br/nilcmetrix



some are lexical like emotivess is already a dictionary based.

Emotiveness.

nornalize scores from NIILC METRICS (BR-LIWC)

https://github.com/nilc-nlp/nilcmetrix

----

exploratory analysis for correlation in drift and embeddings techniqyes
--
IF we find anything.



metrics and drifts, and SHOW if techniques is correlated.

correlation between technques that find drift.

Like there could be technques that are good at identifying soome types of drift.

Drifts by fact, or writting style,etc...