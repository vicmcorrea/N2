I am continuing work on the STIL paper in `Articles/N2`. Please use `Articles/N2` as the main workspace and read the core docs before making decisions. The project is already past exploratory coding and now has a frozen comparative baseline, a shared evaluation panel, contextual BERT results, a cross-method agreement layer, and a paper-facing figure package integrated into the LaTeX draft.

Start by reading:

- `README.md`
- `docs/chat_handoff.md`
- `docs/project_overview.md`
- `docs/advisor_feedback_2026_03_20.md`
- `docs/paper_writing_status_2026_03_23.md`
- `docs/progress_status_2026_03_20.md`
- `docs/cross_method_agreement_2026_03_23.md`
- `docs/comparison_panel_2026_03_22.md`
- `docs/tfidf_drift_baseline_2026_03_22.md`
- `docs/word2vec_baseline_freeze_2026_03_21.md`
- `docs/ptparl_v_vote_label_note.md`
- `2026S1_STIL_conceptDrift/main.tex`
- `2026S1_STIL_conceptDrift/figs/paper/figure_inventory.md`

Important advisor motivation:

My advisor said the earlier framing was too close to claiming validated semantic-change detection without an external ground-truth layer. The paper should therefore be written as an exploratory comparative study of drift techniques in Brazilian Portuguese political discourse, not as a benchmark-style proof that one detector is correct. The advisor explicitly wanted `TF-IDF`, `Word2Vec`, and `BERT` compared directly, with attention to agreement, disagreement, and whether expensive models add enough value over cheaper ones. He also suggested a possible symbolic support layer such as `NILC-Metrix` and said disagreement between methods may reveal different kinds of drift rather than simple failure.

Current paper framing:

- main corpus: `BrPoliCorpus floor`
- complementary corpus: `Roda Viva`
- optional later validation-oriented corpus: `PTPARL-V`
- paper goal: compare lexical-profile, static-embedding, and contextual drift signals in Brazilian Portuguese political discourse
- paper emphasis: agreement, disagreement, interpretability, and computational tradeoffs

Important constraints:

- do not write the paper as if we have external semantic ground truth
- do not merge `BrPoliCorpus` and `Roda Viva` into one uncontrolled timeline
- keep `BrPoliCorpus floor` as the main discovery corpus
- treat `PTPARL-V` as a separate noisy supervision source that still needs explicit deduplication/aggregation rules

Current frozen source of truth:

- `run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce`

Do not use `8e15dc2372c5` as the immutable prepared-artifact source because it was touched by an aborted forced rerun after completion.

Current key results:

- corpus: 24 yearly slices, 428,366 speeches, 63,071,705 retained tokens
- shared comparison panel: 55 lemmas
- panel composition: 15 `Word2Vec` drift terms, 15 `TF-IDF` drift terms, 20 stable controls, 5 theory seeds
- `Word2Vec` vs `TF-IDF` Spearman: `-0.540`
- `BERT(-1)` vs `Word2Vec` Spearman: `0.208`
- `BERT(-1)` vs `TF-IDF` Spearman: `0.125`
- BERT layer agreement Spearman: `0.858`
- top-15 overlap: BERT/Word2Vec `7`, BERT/TF-IDF `6`, Word2Vec/TF-IDF `0`

Current filtered contextual top terms:

- `bloqueio`, `típico`, `exposição`, `salário`, `mínimo`
- `troca`, `preço`, `voto`, `real`, `intervenção`
- `excepcional`, `renovação`, `eleição`, `crítico`, `político`

Current main manuscript and figures:

- manuscript: `2026S1_STIL_conceptDrift/main.tex`
- paper figures:
  - `2026S1_STIL_conceptDrift/figs/paper/figure_01_corpus_profile.pdf`
  - `2026S1_STIL_conceptDrift/figs/paper/figure_02_method_agreement.pdf`
  - `2026S1_STIL_conceptDrift/figs/paper/figure_03_overlap_and_rank_statistics.pdf`
  - `2026S1_STIL_conceptDrift/figs/paper/figure_04_representative_trajectories.pdf`

The draft already has a title, abstract, methodology, results framing, and integrated figures. The next chat should focus on improving the article itself rather than rebuilding the pipeline.

Please help continue the article from the current draft by:

1. tightening the introduction and related-work framing with real citations
2. sharpening the methods and results prose around the current frozen results
3. proposing or writing compact paper tables, especially a runtime/cost comparison table across `TF-IDF`, `Word2Vec`, and `BERT`
4. improving the discussion of what each method seems to capture and why disagreement is informative
5. deciding how to mention `PTPARL-V` and symbolic analysis in limitations or future work
6. keeping the writing natural, non-robotic, and submission-oriented for STIL

When writing or revising the article:

- use the existing figures and frozen results instead of inventing new ones
- keep prose in full paragraphs, not bullet lists, inside the manuscript
- preserve LaTeX citations, labels, and cross-references carefully
- do not fabricate bibliography entries
- prefer high-signal academic prose over inflated claims

Useful local skills for the new chat:

- `scientific-writing`
- `latex-paper-en`
- `citation-management`
- `stop-slop`

The new chat should assume the implementation work is largely done and the main job is now turning the frozen comparative pipeline into a strong STIL paper.
