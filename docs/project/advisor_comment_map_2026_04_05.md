# Advisor Comment Map

## 1. Corpus choice
- Advisor comment: "Recomendo citar aqui ou discutir na seção dos trabalhos correlatos, outros exemplo de córpus históricos para justificar melhor o uso desse. Não usou o córpus diacrônicos como o Tycho-Brahe, ou História do Português Brasileiro (PHPB) porque não são políticos, não está todo digitalizado, não possui informação temporal, são muito pequenos, etc? Comente também pq você usou esse subconjunto e não usou por exemplo falas dos presidentes que são ainda mais antigas."
- Original text: "The experiments use the floor subset of BrPoliCorpus \cite{lima-lopes-2025-brpolicorpus}, which contains Brazilian Chamber floor speeches from 2000 to 2023 organized into 24 yearly slices."
- Likely meaning: justify why `BrPoliCorpus floor` is the best fit for this paper's political, temporally anchored, year-by-year comparative design.

## 2. Eligibility thresholds
- Advisor comment: "Explique como você chegou nesses valores. Foi escolha empírica?"
- Original text: "A lemma enters the scored vocabulary only if it appears at least 50 times per slice, in at least 5 documents per slice, and in at least 80\% of the 24 slices."
- Likely meaning: explain whether `50 / 5 / 80%` came from a principled corpus-stability decision or from arbitrary tuning. It likely came from empirical reaons of the corpus we have itself. The eligibility thresholds were fixed as practical corpus-stability defaults rather than tuned to maximize any method.

## 3. Workflow design
- Advisor comment: "Como você chegou nesse workflow? Foi baseado em algum trabalho ou foi você que pensou nisso? Deixe isso mais claro. Se foi você que inventou, mesmo assim dê uma explicação lógica de como chegou na ideia."
- Original text: "Figure~\ref{fig:study_design} summarizes the workflow. The preprocessed discovery corpus feeds two cheaper baselines; their method-led candidates are then combined with stable controls and theory seeds to create the shared panel used for contextual inspection and agreement analysis."
- Likely meaning: clarify whether the workflow was adopted from prior literature or assembled by you for this article and why that sequence makes methodological sense.The workflow is a study design assembled for this paper rather than a procedure copied from a single prior work. Its components are literature-backed, but their orchestration is ours. 



## 4. Figure 2 interpretation
- Advisor comment: "Explique melhor como interpretar a Figura 2."
- Original text: "Figure~\ref{fig:method_agreement} shows that contextual top ranks draw support from both camps, while the two cheap methods remain sharply separated."
- Likely meaning: guide the reader on what the figure is supposed to show about separation, overlap, and partial mediation across methods.

## 5. Conclusion and RQs
- Advisor comment: "Atualize as conclusões, respondendo explicitamente as perguntas da pesquisa que você levantou na introdução."
- Original text: "The results support an exploratory comparative study rather than an argument for a single best detector of semantic change. TF-IDF and Word2Vec highlight clearly different regions of the candidate space, and contextual BERT adds a useful but higher-cost inspection layer that remains distinct from both."
- Likely meaning: rewrite the conclusion so it answers the research questions directly instead of only summarizing the general result.
