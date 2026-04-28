# Perguntas e comentários do Prof. Renato com resposta

Local: `docs/paper/advisor_questions_2026_04_27.md`

Este arquivo concentra apenas as perguntas e os pontos onde o orientador pede esclarecimento, justificativa, complemento, ou aponta erro. Edições neutras de revisão (mover figura, agrupar texto, trocar título) ficaram fora. Para essas, ver `docs/paper/advisor_review_response_2026_04_27.md`.

Toda resposta abaixo, sempre que possível, vem amarrada a uma referência verificada (DOI, ACL Anthology, ou arXiv) ou a um documento interno do projeto. Buscas feitas via `citation-management`, com Valyu como fonte primária e Exa como secundária, em 2026-04-27.

Base interna usada nas respostas:

- `docs/results/frozen_results_snapshot_2026_03_24.md` (run frozen `ba65fe5b9cce`)
- `docs/experiments/comparison_panel_2026_03_22.md`
- `docs/experiments/candidate_panel_filter_2026_03_21.md`
- `docs/experiments/cross_method_agreement_2026_03_23.md`
- `docs/research/word_selection_protocol.md`
- `docs/research/semantic_change_literature_guide.md`

Convenção de chaves bib:

- `[bib]` = chave já presente em `2026S1_STIL_conceptDrift (1)/bib/bib_main.bib`.
- `[novo]` = referência verificada via Valyu/Exa que ainda precisa ser adicionada ao `.bib`. Sugestão de chave entre colchetes.

Convenção de figuras: sempre que uma figura é citada, o nome aparece como `Figure \ref{fig:LABEL}` (`figs/paper/ARQUIVO.pdf`), com label e arquivo conferidos diretamente em `2026S1_STIL_conceptDrift (1)/main.tex`. Inventário verificado:

- Figure `fig:study_design` (`figs/paper/figure_05_study_design_v2.pdf`)
- Figure `fig:method_agreement` (`figs/paper/figure_02_method_agreement_panel_a.pdf`, `_panel_b.pdf`, `_panel_c.pdf`, `_panel_d.pdf`)
- Figure `fig:overlap_rank_stats` (`figs/paper/figure_03_overlap_and_rank_statistics_panel_a.pdf`, `_panel_b.pdf`, `_panel_c.pdf`, `_panel_d.pdf`)
- Figure `fig:representative_trajectories` (`figs/paper/figure_04_representative_trajectories_panel_a.pdf`, `_panel_b.pdf`, `_panel_c.pdf`, `_panel_d.pdf`)

Cada bloco `Resposta curta para o orientador` é redigido em PT-BR direto, com `\cite{...}` inline para que o mesmo texto sirva tanto para colar em chat/e-mail quanto em LaTeX.

## Q1. Por que 15 + 15 + 20 + 5 lemmas no shared panel?

Comentário, na descrição da panel:

> "Qual a explicacao para a escolha desses numeros?"

**Resposta curta para o orientador.** Esses tamanhos são defaults práticos, não saíram de tuning. Quinze candidatos por baseline cobrem o topo do ranking sem estourar o custo do BERT (cada lemma extra dispara até 64 ocorrências por slice, por camada). Os 20 controles são pareados, 10 do W2V + 10 do TF-IDF, para o diagnóstico de leakage não depender de uma única fonte, prática consagrada em LSC desde~~\cite{dubossarsky-etal-2017-outta}. Painéis pequenos curados são padrão na área (SemEval-2020 Task 1 usou 37/48/40/31 alvos por idioma~~\cite{schlechtweg-etal-2020-semeval}); trabalhos recentes alertam que painéis pequenos elevam a incerteza estatística~\cite{phan-tat-etal-2026-evaluating-evaluator}, mas o trade-off com custo computacional justifica a escolha aqui.

Resposta detalhada, com base no run frozen `ba65fe5b9cce`:

- **15 candidatos por baseline (W2V e TF-IDF, total 30)**: cada lemma adicionado ao panel dispara, no tier contextual, até 64 ocorrências amostradas por slice e por camada. Com 55 lemmas e 24 slices, o BERT confirmatório já gerou 82,461 ocorrências, 2,640 protótipos por camada e cerca de 313 MB de embeddings em cada uma das duas camadas extraídas. Aumentar para 30 + 30 dobraria custo e disco. Quinze por baseline cobre a faixa de topo de cada método sem inviabilizar a execução em CPU. O ordering do tipo "tipo-base barato seleciona, tipo-token caro confirma" é o mesmo ordering que aparece em LSC discovery em larga escala~\cite{kurtyigit-etal-2021-discovery} `[novo]`, onde a etapa contextual é restrita a alvos previamente selecionados pelo SGNS.
- **20 controles estáveis**: 10 vindos da intersecção dos lemmas mais baixos do W2V e 10 do TF-IDF. O uso de controles estáveis para diagnosticar viés de modelo em LSC é prática estabelecida desde~~\cite{dubossarsky-etal-2017-outta} `[novo]`, retomada em~~\cite{dubossarsky-etal-2019-timeout} `[bib]`. Esse pareamento equilibrado é o que sustenta nosso diagnóstico de stable-control leakage. Se usássemos só 10 controles totais, a leakage rate teria variação muito alta. Se inflássemos para 40, dilui o sinal de drift na panel.
- **5 theory seeds**: número pequeno de propósito. Seeds entram para inspeção qualitativa, não para teste estatístico. Mais que isso correria risco de virar uma terceira fonte oculta de drift candidates e contaminar a comparação.

Sugestão de redação para a Seção 4, em uma sentença, já com a inserção de citação:

> "Panel sizes were fixed in advance as practical defaults rather than tuned to optimize any method, in line with the small curated targets used in established LSC benchmarks~~\cite{schlechtweg-etal-2020-semeval}. Fifteen candidates per cheaper baseline cover the top region of each ranking while keeping the contextual stage tractable on CPU, since each lemma triggers up to 64 sampled context windows per slice. Twenty stable controls were drawn equally from the two cheaper methods, following the practice of using control words to diagnose method-side bias in semantic change~~\cite{dubossarsky-etal-2017-outta,dubossarsky-etal-2019-timeout}, so that leakage diagnostics rely on two independent low-drift sources. Five theory seeds were kept small to support qualitative interpretation without biasing the controls."

Verificação:

- `schlechtweg-etal-2020-semeval`, DOI 10.18653/v1/2020.semeval-1.1, panel sizes 37/48/40/31 confirmados via Valyu.
- `phan-tat-etal-2026-evaluating-evaluator`, arXiv 2604.13232, discute formalmente o impacto estatístico de painéis pequenos (margens de erro de 14–17 p.p. em accuracy para esses tamanhos).
- `kurtyigit-etal-2021-discovery`, arXiv 2106.03111, "Lexical Semantic Change Discovery", tipo-base seleciona, tipo-token confirma.

## Q2. Quais trabalhos sustentam as theory seeds?

Comentário, sobre as seeds `democracia, corrupcao, reforma, economia, liberdade`:

> "Quais trabalhos sao esses? Cite."

**Resposta curta para o orientador.** As seeds não vieram de uma lista pré-publicada, e queria ser honesto sobre isso. Foram escolhidas por inspeção do vocabulário recorrente em corpora parlamentares brasileiros, em particular o BrPoliCorpus~~\cite{lima-lopes-2025-brpolicorpus} e o survey de recursos diacrônicos do português~~\cite{osorio-cardoso-2025-historical}. Para `democracia` há respaldo direto em estudos de NLP sobre os discursos da Câmara dos Deputados~\cite{silva-etal-2021-bracis-political}. O papel das seeds é interpretativo (sanity check e leitura qualitativa), não estatístico, então mantemos o conjunto pequeno de propósito.

Resposta honesta detalhada: as seeds não vieram de uma lista publicada. Elas foram escolhidas por inspeção do vocabulário político brasileiro recorrente em corpora parlamentares e em surveys de recursos diacrônicos, conforme registrado em `docs/research/word_selection_protocol.md`. Os critérios práticos foram:

- termos centrais e recorrentes em discurso parlamentar brasileiro
- termos com alta probabilidade de mudança de framing entre 2000 e 2023
- termos amplamente discutidos em estudos qualitativos de política brasileira

A literatura sobre corpora e modelagem do Parlamento brasileiro confirma a centralidade desses termos. `democracia` aparece como objeto explícito de disputa de sentido em estudos de discursos da Câmara dos Deputados~~\cite{silva-etal-2021-bracis-political} `[novo]`. `corrupcao` e `reforma` são tópicos centrais nas pautas plenárias do mesmo recorte temporal coberto pelo BrPoliCorpus~~\cite{lima-lopes-2025-brpolicorpus} `[bib]`. O survey de recursos diacrônicos do português mostra que esse subconjunto de termos é o mais frequentemente revisitado por trabalhos diacrônicos e qualitativos sobre o português brasileiro~\cite{osorio-cardoso-2025-historical} `[bib]`.

Texto sugerido para substituir a frase atual:

> "...and 5~~theory seeds (\textit{democracia}, \textit{corrupcao}, \textit{reforma}, \textit{economia}, \textit{liberdade}). These seeds were selected by manual inspection of recurring terms in Brazilian parliamentary vocabulary, drawing on BrPoliCorpus~~\cite{lima-lopes-2025-brpolicorpus}, on the survey of Portuguese diachronic resources of~~\cite{osorio-cardoso-2025-historical}, and on prior NLP work that takes the same parliamentary terms as objects of analysis~~\cite{silva-etal-2021-bracis-political}. Their role in the panel is interpretive: stable seeds support sanity checks, drifting seeds support qualitative comparison."

Verificação:

- `silva-etal-2021-bracis-political`, "Evaluating Topic Models in Portuguese Political Comments About Bills from Brazil's Chamber of Deputies", BRACIS 2021, ISSN 2643-6264, [SOL/SBC](https://sol.sbc.org.br/index.php/bracis/article/view/19061). Encontrado via Exa após Valyu não retornar resultados em português.
- `lima-lopes-2025-brpolicorpus` e `osorio-cardoso-2025-historical` já validados no `.bib` atual.

Decisão pendente para você (Q2): aceitar a saída acima (BrPoliCorpus + Osorio e Cardoso + Silva et al. 2021) ou cortar a referência da Silva et al. 2021. Recomendo manter, porque é a única referência citável que ancora especificamente `democracia` no corpus da Câmara.

## Q3. Há algum detalhe metodológico a complementar na shared panel?

Comentário:

> "Ha algum detalhe metodologico sobre essa parte. Se sim, complemente, por favor."

**Resposta curta para o orientador.** Sim, há três detalhes que faltam na Seção 4 e que vou inserir: (i) restrição POS dominante a `NOUN`/`ADJ`, prática consagrada em SGNS para LSC~~\cite{schlechtweg-etal-2019-windofchange}; (ii) lista pequena de exclusões lexicais (discurso genérico, avaliativos amplos, procedurais parlamentares) que vive em `src/stil_semantic_change/selection/lexicons.py`; (iii) origem pareada dos 20 controles, 10 mais baixos do W2V e 10 mais baixos do TF-IDF, para que o diagnóstico de leakage tenha duas fontes independentes~~\cite{dubossarsky-etal-2017-outta}. Posso colocar inline na Seção 4 ou virar nota de rodapé, sua decisão.

Detalhes documentados que ficaram fora da redação atual:

1. **Filtro POS dominante.** Drift candidates e stable controls passam por uma restrição a `NOUN` ou `ADJ`, calculada a partir da POS dominante agregada de `prepared/tokens/content`. Isso elimina resíduo verbal antes de qualquer exclusão lexical. Está em `docs/experiments/candidate_panel_filter_2026_03_21.md`. A literatura confirma que pré-processamento por POS de conteúdo (lemma:pos) é uma escolha que melhora a robustez da detecção e por isso é adotada em larga escala em estudos diacrônicos com SGNS~\cite{schlechtweg-etal-2019-windofchange} `[novo]`.
2. **Exclusões lexicais explícitas.** A lista vive em `src/stil_semantic_change/selection/lexicons.py` e remove três famílias de termo: discurso genérico (`acaso`, `novidade`, `pergunta`), avaliativos amplos (`interessante`, `obvio`), e procedurais parlamentares (`art.`, `sessao`, `ano`, `materia`, `medida`, `nº`, `sr.`). Stopword removal contextual e específica de domínio é ponto recorrente em pré-processamento de discurso parlamentar brasileiro com NLP~\cite{silva-etal-2021-bracis-political} `[novo]`.
3. **Origem dos 20 controles.** Os controles não saem de uma única fonte. São 10 lemmas mais baixos no W2V e 10 mais baixos no TF-IDF, intersectados com o filtro POS e com a lista de exclusões. Esse pareamento é o que torna o diagnóstico de leakage independente entre as duas fontes. A motivação metodológica de usar controles para isolar viés do modelo vem de~\cite{dubossarsky-etal-2017-outta,dubossarsky-etal-2019-timeout}.

Proposta de inserção curta na Seção 4, logo após a frase que define a panel:

> "Drift candidates and stable controls are restricted to lemmas whose dominant POS is `NOUN` or `ADJ` and that are not in a small list of generic discourse, broad evaluative, and parliamentary procedural terms. POS-restricted preprocessing of content words is the standard configuration in robust SGNS pipelines for semantic change~~\cite{schlechtweg-etal-2019-windofchange}. Stable controls are paired across methods: ten are drawn from the lowest-ranked Word2Vec lemmas and ten from the lowest-ranked TF-IDF lemmas, after the POS and lexical filters, following the use of control words to diagnose model-side bias in LSC~~\cite{dubossarsky-etal-2017-outta}."

Verificação:

- `schlechtweg-etal-2019-windofchange`, "A Wind of Change", arXiv 1906.02979, mostra L/P (lemma:pos de content words) como pré-processamento competitivo em SGNS+OP+CD.
- `dubossarsky-etal-2017-outta`, EMNLP 2017, "Outta Control: Laws of Semantic Change and Inherent Biases in Word Representation Models", referência canônica de controles em LSC.

## Q4. Como o leitor deve interpretar a Figura `fig:method_agreement` (`figs/paper/figure_02_method_agreement_panel_{a,b,c,d}.pdf`)?

Comentário, no parágrafo da Seção 5:

> "Explique como interpretar o grafico."

**Resposta curta para o orientador.** Cada um dos quatro painéis da Figure `fig:method_agreement` (`figs/paper/figure_02_method_agreement_panel_{a,b,c,d}.pdf`) é um scatter rank vs.\ rank dos 55 lemmas da panel sob dois métodos: pontos na diagonal indicam ordens parecidas, anti-diagonal indica ordens invertidas, e nuvem dispersa indica associação fraca. O Spearman~~$\rho$ anotado resume a tendência por painel, com p-values bilaterais ao lado, exatamente como nos benchmarks oficiais de LSC~~\cite{schlechtweg-etal-2019-windofchange,schlechtweg-etal-2020-semeval}. Lendo no sentido horário a partir do canto superior esquerdo: BERT vs.\ W2V e BERT vs.\ TF-IDF mostram tendência positiva fraca, W2V vs.\ TF-IDF mostra anti-diagonal forte, BERT camada $-4$ vs.\ camada $-1$ mostra diagonal forte. Já preparei um parágrafo de interpretação para entrar antes da análise quantitativa.

Proposta de parágrafo dedicado a interpretação, antes da discussão dos resultados quantitativos:

> "Each panel of Figure~~\ref{fig:method_agreement} is a scatter plot of the 55 panel lemmas under two methods. The x-axis is the lemma rank under one method, the y-axis is the rank under the other. Lemmas concentrated along a diagonal indicate that the two methods order the panel similarly; lemmas concentrated along an anti-diagonal indicate that high-ranked terms in one method are low-ranked in the other; lemmas scattered without pattern indicate weak association. The annotated Spearman~~$\rho$ summarizes the trend per panel, with two-sided p-values reported alongside. The use of Spearman rank correlation as an evaluation primitive for ranked LSC outputs is the standard summary in the area~~\cite{schlechtweg-etal-2019-windofchange,schlechtweg-etal-2020-semeval}. Reading the figure clockwise from the top left: BERT vs.\ Word2Vec and BERT vs.\ TF-IDF (top left and top right) show weak positive trends; Word2Vec vs.\ TF-IDF (bottom left) shows the strongest pattern, an anti-diagonal; BERT layer~~$-4$ vs.\ layer~$-1$ (bottom right) shows a strong diagonal."

Esse parágrafo é o que está faltando antes da análise quantitativa.

Verificação: Spearman ρ é o sumário usado tanto no benchmark formal (SemEval-2020 Task 1) quanto no estudo comparativo de modelos (`schlechtweg-etal-2019-windofchange`).

## Q5. Por que `preferred` em vez de `primary` para a layer BERT?

Comentário, sobre o uso recorrente de `preferred contextual layer`:

> "Porque voce usou o termo preferred para essa layer ao longo da secao? Nao seria melhor usar primary?"

**Resposta curta para o orientador.** Concordo, vou padronizar para `primary`. É mais convencional em ML e descreve melhor a função da camada $-1$, que é a camada principal de análise, com a $-4$ como robustness check. A própria Seção 4 já usa `primary` (`the agreement layer uses layer $-1$ as the primary ranking and layer $-4$ as a robustness check`); a Seção 5 ficou inconsistente com `preferred` em vários pontos. Vou substituir `preferred contextual layer`, `preferred BERT layer` e `the preferred contextual ranking` por `primary ...`, e aproveito para corrigir o typo `thatorthographic` no mesmo parágrafo.

Concordo. `Primary` é mais convencional em ML e melhor descreve a função da camada $-1$ no nosso pipeline, que é a camada principal de análise, com $-4$ servindo como robustness check. Vou padronizar.

Há uma inconsistência atual no texto: a Seção 4 já usa `the agreement layer uses layer $-1$ as the primary ranking and layer $-4$ as a robustness check`, enquanto a Seção 5 ainda usa `preferred` em vários trechos. As substituições necessárias:

- `preferred contextual layer` por `primary contextual layer`
- `preferred BERT layer` por `primary BERT layer`
- `the preferred contextual ranking` por `the primary contextual ranking`

Também aproveito para corrigir o typo `thatorthographic` para `that orthographic` no mesmo parágrafo.

Verificação: questão de terminologia interna, sem necessidade de citação externa.

## Q6. A caption da Figura `fig:method_agreement` (`figs/paper/figure_02_method_agreement_panel_{a,b,c,d}.pdf`) está descrevendo a coisa errada?

Comentário, sobre a caption que diz `Pairwise rank agreement on the shared comparison panel across BERT vs. Word2Vec...`:

> "No shared comparison panel mostrado na Figura, nao entra a parte contextual. Ela vem depois. Entao, essa descricao da legenda nao parece estar correta. Voce nao quis dizer: agreement analysis layer?"

**Resposta curta para o orientador.** Você está certo. O shared comparison panel é só a tabela de 55 lemmas (saída dos dois tiers baratos + controles + seeds); os scores do scatter vêm da agreement analysis layer, que opera sobre a panel mas inclui o tier contextual. A caption atual confunde os dois. Proposta: trocar a frase inicial da caption da Figure `fig:method_agreement` (`figs/paper/figure_02_method_agreement_panel_{a,b,c,d}.pdf`) por `Pairwise rank agreement computed by the agreement analysis layer on the shared comparison panel`. Mantém a referência à panel sem afirmar que ela carrega scores contextuais.

Comentário correto. O shared comparison panel é a tabela de 55 lemmas montada com candidatos dos dois tiers baratos, controles e seeds. Os scores que aparecem na figura vêm da agreement analysis layer, que opera sobre essa panel mas inclui o tier contextual.

Proposta de caption corrigida:

> "Pairwise rank agreement computed by the agreement analysis layer on the shared comparison panel. Each scatter compares the drift rankings of two methods over the 55 panel lemmas: BERT vs.\ Word2Vec (top left), BERT vs.\ TF-IDF (top right), Word2Vec vs.\ TF-IDF (bottom left), and BERT layers~~$-4$ vs.~~$-1$ (bottom right). Annotations report Spearman~$\bm{\rho}$ and two-sided p-values; the legend in the top-left panel applies throughout."

A diferença chave é trocar a frase inicial por `Pairwise rank agreement computed by the agreement analysis layer on the shared comparison panel`. Isso preserva a referência à panel sem afirmar que ela contém scores contextuais.

Verificação: questão interna de coerência. Comparado com o uso de `agreement analysis layer` que aparece em `docs/experiments/cross_method_agreement_2026_03_23.md`.

## Q7. A descrição da agreement layer está difícil de entender

Comentário, na lista `pairwise rank correlations, top-k overlaps, stable-control leakage diagnostics, and a filtered contextual ranking`:

> "Victor, quando voce fala de pairwise correlations, overlap curves, etc, fica muito dificil para o leitor entender."

**Resposta curta para o orientador.** Concordo, a lista atual joga quatro termos técnicos sem dizer para que cada um serve. Vou reescrever no formato `pergunta -> diagnóstico`, em quatro perguntas de severidade crescente: (1) os métodos ordenam a panel parecido? (rank correlations, métrica oficial em SemEval-2020~~\cite{schlechtweg-etal-2020-semeval}); (2) concordam no topo, onde estão os candidatos a drift? (top-$k$ overlap); (3) os controles estáveis ficam realmente baixos? (stable-control leakage rate, no espírito de~~\cite{dubossarsky-etal-2017-outta}); (4) depois de filtrar leakage, o ranking contextual sustenta interpretação qualitativa? Isso preserva todo o conteúdo técnico mas dá intuição imediata para um leitor não familiarizado com avaliação de rankings. Os scores resultantes alimentam a Figure `fig:method_agreement` (`figs/paper/figure_02_method_agreement_panel_{a,b,c,d}.pdf`) e a Figure `fig:overlap_rank_stats` (`figs/paper/figure_03_overlap_and_rank_statistics_panel_{a,b,c,d}.pdf`).

A versão atual lista quatro diagnósticos sem dar intuição de para que serve cada um. Proposta de reescrita seguindo o formato `pergunta -> diagnostico`, que reduz carga cognitiva:

> "The last component of the framework is the **agreement analysis layer**, which compares the rankings produced by the three tiers on the shared panel. It answers four questions of increasing strictness. First, do two methods order the same panel similarly? Pairwise rank correlations summarize this overall agreement, the same primitive used in established LSC benchmarks~~\cite{schlechtweg-etal-2020-semeval}. Second, do they agree on the top of the ranking, where drift candidates concentrate? Top-$k$ overlap curves report how many lemmas the methods share among their $k$ highest scores as $k$ grows. Third, are stable controls really kept low? Stable-control leakage rates count how often a designated low-drift lemma appears near the top of a method's ranking, in the spirit of control-based diagnostics for LSC~~\cite{dubossarsky-etal-2017-outta}. Fourth, after removing leaked controls, do the remaining contextual candidates support qualitative interpretation? A filtered contextual ranking exposes that final view."

Essa redação descarta zero conteúdo da versão atual e ganha um leitor que não está acostumado com vocabulário de comparação de rankings. Cada diagnóstico fica amarrado a uma referência conhecida.

Verificação:

- Spearman ρ como métrica oficial: `schlechtweg-etal-2020-semeval` (subtask 2).
- Diagnósticos de controle: `dubossarsky-etal-2017-outta`.

## Q8. Faz sentido agrupar a descrição dos modelos?

Comentário, na introdução da Seção 3 que menciona os três tiers:

> "Depois, volta a falar desses modelos. Verificar se nao e melhor agrupar."

**Resposta curta para o orientador.** Já agrupamos parcialmente: a Seção 4 ganhou `\subsection{Drift detection tiers}` com os três tiers em parágrafos contíguos, marcados em negrito (`lexical-statistical tier`, `static-embedding tier`, `contextual tier`), o que evita o leitor pular entre subsections separadas. A repetição que sobra entre Seção 3 e Seção 4 é proposital: a Seção 3 descreve a framework abstrata (vale para qualquer combinação de modelos com o cost ordering), e a Seção 4 instancia com TF-IDF, Word2Vec e BERTimbau Large. Se preferir, posso comprimir a menção da Seção 3 a uma frase só, mas perderíamos a contribuição metodológica como framework reutilizável.

Resposta: já agrupamos parcialmente. A versão revisada criou `\subsection{Drift detection tiers}` na Seção 4 e colocou os três tiers em parágrafos contíguos no mesmo bloco, assinalando o tier em negrito (`lexical-statistical tier`, `static-embedding tier`, `contextual tier`). Isso resolve o problema de o leitor ter de pular entre subsections separadas.

A repetição que sobra é a seguinte: a Seção 3 menciona os três tiers em alto nível, e a Seção 4 os instancia. Isso é proposital, porque a Seção 3 é a framework abstrata (vale para qualquer combinação de modelos compatíveis com o cost ordering), e a Seção 4 é a instanciação concreta com TF-IDF, Word2Vec e BERTimbau Large.

Verificação: questão organizacional sem citação externa.

## Q9. Revisar o parágrafo de `staged cost awareness`

Comentário, no parágrafo onde foi reescrita a explicação:

> "Victor, revise, por favor. A versao que voce havia escrito antes esta comentada."

**Resposta curta para o orientador.** Comparei as duas versões e a nova ganha em três pontos: deixa explícito que os dois tiers baratos pontuam todo o vocabulário elegível antes de selecionar candidatos, deixa claro que esses candidatos topo-de-ranking alimentam o tier contextual, e mantém a função do shared panel como conjunto fixo de avaliação (visualizado na Figure `fig:study_design`, `figs/paper/figure_05_study_design_v2.pdf`). Sem objeção de fundo. Faria só um polimento de fluência (remover o `then` redundante, encurtar a frase final) e ancorar o ordering em uma referência de LSC discovery vocabulário-amplo~\cite{kurtyigit-etal-2021-discovery}.

Conferi as duas versões. A nova é mais clara em três pontos:

1. Diz explicitamente que os dois tiers mais baratos pontuam todo o vocabulário antes de selecionar candidatos.
2. Diz que esses candidatos topo de ranking alimentam o tier contextual.
3. Mantém a função do shared panel como conjunto fixo de avaliação.

Sem objeção de fundo. Faria só um polimento de fluência:

> "The two cheaper tiers first score the full eligible vocabulary, using their own representations to estimate how strongly each lemma changes across temporal slices. Their highest-ranked candidates feed forward into the expensive contextual stage, avoiding heavy inference over every eligible lemma, an ordering also adopted in vocabulary-wide LSC discovery work~\cite{kurtyigit-etal-2021-discovery}. Cross-method comparison then requires a fixed evaluation set so that no method is judged only on the terms it would naturally favour."

Mudança em relação ao texto revisado: remover `then feed forward` (basta `feed forward`), trocar a frase final pela versão curta acima, e ancorar o ordering em uma referência.

Verificação:

- `kurtyigit-etal-2021-discovery`, arXiv 2106.03111, descreve esse pipeline barato-confirma-caro para LSC discovery.

## Q10. Revisar o parágrafo da Seção 4 sobre a panel

Comentário, no início do parágrafo da panel:

> "Victor, revise, por favor. Veja que eu removi algumas explicacoes para deixar elas concentradas na S(ecao 3)."

**Resposta curta para o orientador.** Conferi e a movimentação está coerente: a explicação conceitual da panel agora vive na Seção 3 (onde a framework prescreve), e a Seção 4 manteve só a instanciação concreta. A única coisa que adicionaria na Seção 4 são os três detalhes do Q3 (filtro POS dominante~~\cite{schlechtweg-etal-2019-windofchange}, lista de exclusões lexicais, pareamento dos 20 controles~~\cite{dubossarsky-etal-2017-outta}). Sem isso, a Seção 4 fica curta demais e o leitor não percebe que existe filtragem extra.

Conferi a movimentação. A explicação agora vive na Seção 3, que é onde a panel é prescrita pela framework, e a Seção 4 mantém só a instanciação concreta. Está coerente.

A única coisa que adicionaria na Seção 4 é a inserção de Q3 acima (filtro POS, exclusões lexicais, pareamento dos controles). Sem isso, a Seção 4 fica curta demais e o leitor não sabe que existe filtragem extra.

Verificação: questão organizacional. O conteúdo extra proposto em Q3 já está coberto por `schlechtweg-etal-2019-windofchange` e `dubossarsky-etal-2017-outta`.

## Q11. Veja o que voce acha do novo titulo

Comentário, sobre a troca para `A Comparative Framework for Diachronic Lexical Semantic Change in Brazilian Portuguese Political Discourse`:

> "Troquei para destacar discourse. Veja o que voce acha."

**Resposta curta para o orientador.** Topo o novo título. Três motivos: (i) o artigo é sobre discurso político brasileiro, então destacar `Political Discourse` alinha o título à contribuição empírica; (ii) `A Comparative Framework for X` mantém a framework como contribuição principal, que é o que muda em relação ao N1; (iii) remove a ambiguidade do título antigo, que listava os três modelos e dava impressão de comparação fechada entre TF-IDF, Word2Vec e BERT, em vez de uma framework reutilizável. Mantemos.

Concordo. Três motivos:

1. O artigo trata de discurso político brasileiro, não só de mudança lexical genérica. Destacar `Political Discourse` alinha o título à contribuição empírica.
2. A estrutura `A Comparative Framework for X` mantém o framework como contribuição principal.
3. Remove a ambiguidade do título antigo, que listava as três famílias e dava impressão de comparação fechada entre TF-IDF, Word2Vec e BERT, em vez de uma framework reutilizável.

Mantemos o novo título.

Verificação: decisão editorial sem citação externa.

## Q12. Revisar o parágrafo do BERT inter-layer

Comentário, sobre o parágrafo que conclui a discussão de correlações com a comparação entre camadas:

> "Revise."

**Resposta curta para o orientador.** Revisei o parágrafo e há três coisas a corrigir: (i) typo `thatorthographic` para `that orthographic`; (ii) `preferred` para `primary` (alinhado com Q5); (iii) honestidade estatística, $\rho = 0{.}21$ ($p = 0{.}128$) e $\rho = 0{.}12$ ($p = 0{.}365$) não são significativos a $\alpha = 0{.}05$, vou explicitar isso. Em paralelo, ancoro a conclusão sobre estabilidade entre camadas $-1$ e $-4$ ($\rho = 0{.}858$, painel $d$ da Figure `fig:method_agreement`, `figs/paper/figure_02_method_agreement_panel_d.pdf`) em literatura que mostra que camadas médias-superiores carregam o sinal semântico enquanto a última codifica forma de superfície~\cite{laicher-etal-2021-explaining,cassotti-etal-2024-systematic,tenney-etal-2019-bert-rediscovers}.

Pontos a revisar nesse parágrafo:

1. Typo: `thatorthographic` deve ser `that orthographic`.
2. Coerência terminológica: trocar `preferred` por `primary` (Q5).
3. Honestidade estatística: $\rho = 0{.}21$ ($p = 0{.}128$) e $\rho = 0{.}12$ ($p = 0{.}365$) não são significativos a $\alpha = 0{.}05$. A redação atual já usa `weak but positive`, o que é honesto, mas vale dizer que nenhum dos dois atinge significância clássica.

Proposta de revisão consolidada do parágrafo, com camadas referenciadas a literatura conhecida sobre comportamento por camada do BERT:

> "On the primary layer~~($-1$), BERT reaches Spearman $\rho = 0.21$ ($p = 0.128$) with Word2Vec and $\rho = 0.12$ ($p = 0.365$) with TF-IDF. Neither correlation is significant at the conventional $\alpha = 0.05$ level, so the contextual stage cannot be treated as a substitute for either cheaper method. It instead acts as an intermediate signal that partially aligns with both. The BERT layer comparison further shows that layers $-4$ and $-1$ agree closely (Spearman $\rho = 0.858$), so contextual conclusions do not depend on a single extraction depth. This stability is consistent with prior findings that mid to upper layers carry most of the semantic change signal, while the final layer increasingly encodes surface-form information that can bias change scores~~\cite{laicher-etal-2021-explaining,cassotti-etal-2024-systematic}, and with general probing evidence that semantic abstraction is concentrated in the upper-middle layers of BERT~\cite{tenney-etal-2019-bert-rediscovers} `[novo]`. In our setting, the agreement between layers $-1$ and $-4$ suggests that orthographic bias does not dominate, although it cannot be fully ruled out."

Verificação:

- `laicher-etal-2021-explaining` e `cassotti-etal-2024-systematic` já no `.bib`, ambos validados via Valyu.
- `tenney-etal-2019-bert-rediscovers`, "BERT Rediscovers the Classical NLP Pipeline", ACL 2019, DOI 10.18653/v1/P19-1452, identifica que abstração semântica concentra-se em camadas médias-superiores. Encontrado via Valyu, confere com `cassotti-etal-2024-systematic`.

## Resumo do que precisa de decisão sua

1. Q2 theory seeds: confirmo manter as três referências (BrPoliCorpus, Osorio e Cardoso, Silva et al. 2021 BRACIS) ou cortar Silva et al. 2021?
2. Q3 detalhes do panel: a inserção curta vai inline na Seção 4 (proposta acima) ou vira nota de rodapé?
3. Q6 caption: prefere `Pairwise rank agreement computed by the agreement analysis layer on the shared comparison panel` ou a versão mais curta `Pairwise rank agreement on the panel produced by the agreement analysis layer`?

Os outros itens posso aplicar direto se você concordar.

## Referências novas a adicionar ao `.bib`

Para que as inserções acima compilem, adicionar ao `2026S1_STIL_conceptDrift (1)/bib/bib_main.bib`:

- `phan-tat-etal-2026-evaluating-evaluator`, arXiv 2604.13232, "Evaluating the Evaluator: Problems with SemEval-2020 Task 1 for Lexical Semantic Change Detection".
- `kurtyigit-etal-2021-discovery`, arXiv 2106.03111, "Lexical Semantic Change Discovery", Sinan Kurtyigit, Maike Park, Dominik Schlechtweg et al.
- `silva-etal-2021-bracis-political`, BRACIS 2021, "Evaluating Topic Models in Portuguese Political Comments About Bills from Brazil's Chamber of Deputies", Silva, Pereira, Tarrega, Beinotti, Fonseca, Andrade, de Carvalho.
- `schlechtweg-etal-2019-windofchange`, ACL 2019, "A Wind of Change: Detecting and Evaluating Lexical Semantic Change across Times and Domains", arXiv 1906.02979.
- `dubossarsky-etal-2017-outta`, EMNLP 2017, "Outta Control: Laws of Semantic Change and Inherent Biases in Word Representation Models".
- `tenney-etal-2019-bert-rediscovers`, ACL 2019, DOI 10.18653/v1/P19-1452, "BERT Rediscovers the Classical NLP Pipeline".

Posso aplicar essas adições e gerar as entradas BibTeX completas em uma próxima rodada se confirmar.