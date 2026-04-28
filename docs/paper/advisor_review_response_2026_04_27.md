# Resposta aos comentários do Prof. Renato

Local: `docs/paper/advisor_review_response_2026_04_27.md`

Base de evidências usada nas respostas:

- diff atual de `2026S1_STIL_conceptDrift (1)/main.tex`
- run frozen `ba65fe5b9cce` documentado em `docs/results/frozen_results_snapshot_2026_03_24.md`
- protocolo de seleção em `docs/research/word_selection_protocol.md`
- panel em `docs/experiments/comparison_panel_2026_03_22.md` e `docs/experiments/candidate_panel_filter_2026_03_21.md`
- agreement layer em `docs/experiments/cross_method_agreement_2026_03_23.md`
- guia de literatura em `docs/research/semantic_change_literature_guide.md`

A ordem segue mais ou menos o sentido de leitura do PDF, agrupando comentários relacionados.

## 1. Título: destacar `discourse`

Comentário (linha 34 a 35):

> "Troquei para destacar discourse. Veja o que você acha."

Versão atual:
`A Comparative Framework for Diachronic Lexical Semantic Change in Brazilian Portuguese Political Discourse`

Concordo com a mudança. Três motivos práticos:

1. O artigo deixa claro desde o abstract que a análise não é só de mudança lexical, é de mudança lexical em discurso político brasileiro. Colocar `Political Discourse` em posição de destaque alinha o título com a contribuição empírica.
2. A estrutura `A Comparative Framework for X` mantém a moldura de framework, que é a parte metodológica que o trabalho propõe.
3. Remove a ambiguidade do título antigo, que listava as três famílias de método e dava a impressão de comparação fechada entre TF-IDF, Word2Vec e BERT, e não de uma framework reutilizável.

Não vejo razão para reverter. Mantemos esse título.

## 2. Reorganização da Figura 1 (study design) e da Seção 3

Comentário (linha 168 e adjacentes):

- Figura `fig:study_design` foi movida para o início da Seção 3.
- Caption ajustado para `Staged comparative framework for lexical semantic change detection...`.

Está coerente com a reescrita da seção. A figura agora aparece logo após o parágrafo introdutório da Seção 3, antes da descrição dos três tiers, o que ajuda o leitor a olhar o diagrama enquanto lê o texto.

Ponto técnico: a versão revisada inclui `\includegraphics[...]{figs/paper/figure_05_study_design_v2.pdf}`, mas em `2026S1_STIL_conceptDrift (1)/figs/paper/` só existe `figure_05_study_design.pdf`. Tenho duas opções, e a escolha depende do prof:

- renomear/copiar o arquivo atual para `figure_05_study_design_v2.pdf`
- ou voltar o `\includegraphics` para o nome existente

Proponho gerar uma `v2` de fato com pequenos ajustes visuais, já que a caption mudou.

## 3. Reescrita do parágrafo de `staged cost awareness`

Comentário (linha 208):

> "Victor, revise, por favor. A versão que você havia escrito antes está comentada."

Conferi a versão antiga (comentada com `%`) e a nova. A nova versão é mais clara em três pontos:

1. Diz explicitamente que os dois tiers mais baratos pontuam todo o vocabulário antes de selecionar candidatos.
2. Diz que esses candidatos topo de ranking alimentam o tier contextual, evitando rodar BERT no vocabulário inteiro.
3. Mantém a função do shared panel como conjunto fixo de avaliação.

Sem objeção. Faria só um pequeno polimento de fluência:

> "The two cheaper tiers first score the full eligible vocabulary, using their own representations to estimate how strongly each lemma changes across temporal slices. Their highest-ranked candidates feed forward into the expensive contextual stage, avoiding heavy inference over every eligible lemma."

A diferença é trocar `then feed forward` por `feed forward`, e cortar `in turn requires` por algo mais direto. Posso aplicar esse polimento se você concordar.

## 4. Descrição da agreement layer está densa para o leitor

Comentário (linha 222):

> "Victor, quando você fala de pairwise correlations, overlap curves, etc, fica muito difícil para o le(itor)..."

Esse comentário é justo. O parágrafo com `pairwise rank correlations`, `top-k overlap curves`, `stable-control leakage rates` e `filtered contextual ranking` tem quatro coisas em sequência sem nenhuma intuição.

Proposta de reescrita para a Seção 3, que explica `o que faz e por quê` antes de listar:

> "The last component of the framework is the **agreement analysis layer**, which compares the rankings produced by the three tiers on the shared panel. It answers four questions in increasing order of strictness. First, do two methods order the same panel similarly? Pairwise rank correlations summarize this overall agreement. Second, do they agree on the top of the ranking, where drift candidates concentrate? Top-k overlap curves measure how many lemmas the methods place among their k highest scores as k grows. Third, are stable controls really kept low? Stable-control leakage rates count how often a designated low-drift lemma appears near the top of a method's ranking. Fourth, after removing leaked controls, do the remaining contextual candidates support qualitative interpretation? A filtered contextual ranking exposes that final view."

Essa estrutura segue um padrão `pergunta -> diagnóstico`, que é mais legível do que listar quatro substantivos em sequência. Posso aplicar.

## 5. Agrupar a descrição dos modelos

Comentário (linha 235):

> "Depois, volta a falar desses modelos. Verificar se não é melhor agrupar."

Esse comentário está conectado a 4. A versão revisada de fato já agrupou os três tiers em uma única `\subsection{Drift detection tiers}` na Seção 4, e cada parágrafo identifica claramente o tier. Acho que o agrupamento já está ok agora.

A única redundância que sobra é o parágrafo introdutório da Seção 3 que descreve os tiers em alto nível, e depois a Seção 4 que os instancia. Isso é proposital: a Seção 3 é a framework abstrata, a Seção 4 é a instanciação concreta. Acho que vale manter, mas tomar cuidado para não repetir frases idênticas. Vou fazer um passe de checagem.

## 6. Cite os trabalhos das theory seeds

Comentário (imagens 13 e 14):

> "Quais trabalhos são esses? Cite."

Sobre `theory seeds drawn from prior work on Brazilian political vocabulary`. A redação atual cita as cinco palavras (`democracia`, `corrupcao`, `reforma`, `economia`, `liberdade`) mas não dá uma referência.

Olhando `docs/research/word_selection_protocol.md`, a justificativa real foi:

- termos centrais e recorrentes no léxico político brasileiro
- termos com alta probabilidade de mudança de framing ao longo de 2000 a 2023
- termos que aparecem com frequência em estudos de discurso parlamentar e em listas como BrPoliCorpus

Para citar com honestidade, sugiro duas saídas:

1. Honesta e mínima: declarar que as seeds foram escolhidas a partir de inspeção manual do vocabulário político brasileiro recorrente em corpora como BrPoliCorpus, citando o próprio paper do BrPoliCorpus (`lima-lopes-2025-brpolicorpus`) e, possivelmente, o levantamento de recursos diacrônicos portugueses (`osorio-cardoso-2025-historical`). Isso reflete a verdade do processo.
2. Mais robusta: adicionar uma ou duas referências de trabalhos sobre vocabulário político brasileiro. Candidatos que valem busca:
  - estudos de análise de discurso parlamentar publicados na Câmara
  - trabalhos sobre reforma da previdência, corrupção e democracia em corpora políticos brasileiros recentes
  - eventualmente, glossários de ciência política aplicada ao Brasil

Na minha opinião a saída 1 é mais honesta. Posso enxergar a saída 2 valendo só para `corrupcao` e `reforma`, em que existe literatura consolidada. Para `democracia`, `economia` e `liberdade` qualquer citação vai parecer forçada.

Sugestão de redação:

> "...and 5~~theory seeds (\textit{democracia}, \textit{corrupcao}, \textit{reforma}, \textit{economia}, \textit{liberdade}). These seeds were selected by manual inspection of frequent terms in Brazilian parliamentary vocabulary and in prior surveys of Portuguese diachronic resources~~\cite{osorio-cardoso-2025-historical, lima-lopes-2025-brpolicorpus}, as anchor points whose stability or drift over the 2000 to 2023 period is interpretable in itself."

## 7. Por que 15 + 15 + 20 + 5

Comentário (imagem 13):

> "Qual a explicacao para a escolha desses numeros?"

Resposta com base em `docs/experiments/comparison_panel_2026_03_22.md` e `docs/experiments/candidate_panel_filter_2026_03_21.md`.

A composição 15 + 15 + 20 + 5 não é arbitrária, mas também não é resultado de tuning. Foi um compromisso prático, e vale registrar isso no texto. As razões reais foram:

- **15 candidatos por baseline (Word2Vec, TF-IDF):** suficiente para cobrir a parte de cima de cada ranking sem inflar custo do BERT, que mede até 64 ocorrências por lemma por slice. Com 15 + 15 + 20 + 5 chegamos a 55 lemmas, e isso já produziu cerca de 82,5 mil ocorrências amostradas e 313 MB de embeddings por camada. Acima de 30 candidatos por baseline o custo BERT começa a inviabilizar reprodução em CPU. Isso vem do snapshot frozen.
- **20 controles estáveis:** balanço entre dois conjuntos de baixa drift (10 do W2V, 10 do TF-IDF). Esse pareamento permite que `stable-control leakage` seja medido com base em duas fontes independentes, em vez de só uma. Um número menor produziria estimativas instáveis de leakage.
- **5 theory seeds:** número pequeno para evitar contaminar os controles ou enviesar a avaliação. Essas cinco entram para inspeção qualitativa, não para teste estatístico.

Sugestão de redação para a Seção 4 ou para uma nota de rodapé:

> "Panel sizes were fixed in advance as practical defaults rather than tuned. Fifteen candidates per cheaper baseline give enough coverage of each method's top region while keeping the contextual stage tractable on CPU, since each lemma triggers up to 64 sampled context windows per slice. Twenty stable controls were drawn equally from the two cheaper methods (ten each) so that leakage diagnostics rely on two independent low-drift sources. Five theory seeds were kept small to avoid biasing the controls or overwhelming the qualitative inspection."

## 8. Detalhe metodológico adicional para a panel

Comentário (imagem 15):

> "Ha algum detalhe metodologico sobre essa parte. Se sim, complemente, por favor."

Sim, há detalhes que estão em `docs/experiments/candidate_panel_filter_2026_03_21.md` e que vale a pena incluir. Os mais relevantes:

1. **Filtro de POS dominante:** drift candidates e stable controls são restringidos a `NOUN` ou `ADJ` por POS dominante agregada de `prepared/tokens/content`. Isso elimina resíduo verbal antes de qualquer exclusão lexical.
2. **Exclusões lexicais explícitas:** `src/stil_semantic_change/selection/lexicons.py` mantém uma lista de exclusões de palavras procedurais (`art.`, `sessao`), discurso genérico (`acaso`, `novidade`) e adjetivos avaliativos amplos (`interessante`).
3. **Controles intersecção:** os 10 controles vindos do W2V são os 10 lemmas com menor drift no W2V que passam o filtro. Os 10 do TF-IDF seguem o mesmo critério dentro do TF-IDF. Isso preserva a independência entre as duas fontes de controles.

Posso adicionar um parágrafo curto na Seção 4 indicando o filtro POS e a exclusão lexical, citando `src/stil_semantic_change/selection/lexicons.py` no apêndice ou em um artefato de reprodução.

## 9. Como interpretar a Figura `method_agreement`

Comentário (imagens 16 e 17, linhas 388):

> "Explique como interpretar o grafico."

A reescrita do parágrafo da Seção 5 já encaminha isso, mas vale ser mais explícito. Proposta:

> "Each panel of Figure~~\ref{fig:method_agreement} is a scatter plot of the 55 lemmas in the shared panel under two methods. The x-axis is the rank of each lemma under one method, the y-axis is the rank under the other. Lemmas placed on a roughly diagonal trend indicate agreement between the two methods, lemmas on an anti-diagonal trend indicate disagreement, and lemmas scattered without pattern indicate weak association. Annotated Spearman~~$\rho$ and two-sided p-values quantify the overall trend per panel. The Word2Vec vs.\ TF-IDF panel (top right) shows a clear anti-diagonal pattern, BERT vs.\ Word2Vec and BERT vs.\ TF-IDF (top left, bottom left) show weak positive trends, and BERT layer~~$-4$ vs.\ layer~~$-1$ (bottom right) shows a strong diagonal."

Isso responde diretamente ao pedido.

## 10. Caption da Figura `method_agreement` está incorreta

Comentário (imagem 20, linhas 404 a 408):

> "No shared comparison panel mostrado na Figura, nao entra a parte contextual. Ela vem depois. Entao, essa descricao da legenda nao parece estar correta. Voce nao quis dizer: agreement analysis layer?"

Comentário correto. O shared comparison panel é a tabela de 55 lemmas, e contém só os candidatos vindos dos dois tiers baratos mais controles e seeds. O que entra na figura `method_agreement` são scores produzidos pela agreement analysis layer, que inclui o tier contextual.

Proposta de caption corrigida:

> "Pairwise rank agreement on the shared panel as computed by the agreement analysis layer. Each scatter compares the drift rankings of two methods over the 55 panel lemmas: BERT vs.\ Word2Vec (top left), BERT vs.\ TF-IDF (top right), Word2Vec vs.\ TF-IDF (bottom left), and BERT layers~~$-4$ vs.~~$-1$ (bottom right). Annotations report Spearman~$\bm{\rho}$ and two-sided p-values; legend in the top-left panel applies throughout."

A mudança principal é trocar `Pairwise rank agreement on the shared comparison panel across BERT vs. Word2Vec...` por `Pairwise rank agreement on the shared panel as computed by the agreement analysis layer`.

## 11. `preferred` versus `primary` para a layer BERT

Comentário (imagem 19):

> "Porque voce usou o termo preferred para essa layer ao longo da secao? Nao seria melhor usar primary?"

Eu havia usado `preferred` para sinalizar que a escolha da camada $-1$ é uma preferência metodológica. Mas pensando bem, o prof tem razão. `Primary` é mais comum em machine learning e fica mais claro que essa é a camada principal de análise.

Já existe uma inconsistência no texto atual: na Seção 4 a versão revisada diz `the agreement layer uses layer $-1$ as the primary ranking and layer $-4$ as a robustness check`, enquanto a Seção 5 usa `preferred contextual layer` em alguns trechos.

Vou padronizar para `primary` em todas as ocorrências:

- Seção 4: `the primary ranking and layer $-4$ as a robustness check`. Já está assim.
- Seção 5: trocar `preferred contextual layer`, `preferred BERT layer`, `the preferred contextual ranking` para `primary contextual layer`, `primary BERT layer`, `the primary contextual ranking`.

## 12. Revisar parágrafo BERT inter-layer

Comentário (imagem 18):

> "Revise."

Esse `Revise` cai sobre o parágrafo onde está escrito `thatorthographic bias does not yet dominate` (sem espaço entre `that` e `orthographic`). Outros pontos a corrigir:

1. typo: `thatorthographic` deve ser `that orthographic`
2. coerência com 11: trocar `preferred` por `primary`
3. fluência: a frase `weak but positive associations with both methods` é forte; a evidência empírica é $\rho = 0{.}21$ ($p = 0{.}128$) e $\rho = 0{.}12$ ($p = 0{.}365$), nenhum dos dois significativo a $\alpha = 0{.}05$. A redação `weak but positive` ainda é honesta, mas vale acrescentar que essas correlações não atingem significância estatística clássica.

Proposta de revisão concentrada no parágrafo inter-layer:

> "On the primary layer~~($-1$), BERT reaches Spearman $\rho = 0.21$ ($p = 0.128$) with Word2Vec and $\rho = 0.12$ ($p = 0.365$) with TF-IDF. Neither correlation is significant at the conventional $\alpha = 0.05$ level, so the contextual stage cannot be treated as a substitute for either cheaper method. It instead acts as an intermediate signal that partially aligns with both. The BERT layer comparison further shows that layers $-4$ and $-1$ agree closely (Spearman $\rho = 0.858$), so contextual conclusions do not depend on a single extraction depth. This stability is consistent with prior findings that mid to upper layers carry most of the semantic change signal, while the final layer increasingly encodes surface-form information that can bias change scores~~\cite{laicher-etal-2021-explaining,cassotti-etal-2024-systematic}. In our setting, the agreement between layers $-1$ and $-4$ suggests that orthographic bias does not dominate, although it cannot be fully ruled out."

## 13. Ajustes menores que aproveito o momento para listar

Itens que percebi enquanto lia o diff e que não estão entre os comentários explícitos do prof, mas afetam a coerência:

- O abstract revisado tem `The results shows`, deve ser `The results show`.
- O parágrafo final de Conclusion trocou `30 drift terms` por `all drift terms nominated by the two cheaper methods are exclusive to one baseline`. Está mais elegante, mas vale checar se a banca prefere o número concreto. Eu manteria a versão concreta `30 drift terms`, porque ancora no shared panel.
- Na Seção 5 o resultado `Word2Vec vs. TF-IDF Spearman $\rho = -0.54$ ($p = 2.1 \times 10^{-5}$)` foi mantido, mas a Tabela do `frozen_results_snapshot_2026_03_24.md` registra `0.000021`. Os dois valores são consistentes ($2.1 \times 10^{-5} = 0.000021$). Apenas confirma.
- A Seção `Generative AI Use Disclosure` foi adicionada conforme a nota de submissão. Vale verificar se o formato exigido pela STIL é mais detalhado, do contrário a frase atual cobre o requisito.

## 14. Resumo do que vou aplicar

Sem alteração:

- Aceitar o título.
- Aceitar a relocação da figura de design (`fig:study_design`).
- Aceitar o agrupamento dos tiers em uma subsection única.

Aplicar com pequenas redações (proposta acima):

- Reescrita da agreement analysis layer com formato `pergunta -> diagnostico`.
- Justificativa de 15 + 15 + 20 + 5 como nota explícita.
- Adição de detalhes metodológicos do shared panel: filtro POS dominante e exclusões lexicais.
- Citação das theory seeds com referência ao BrPoliCorpus e à survey de Osorio e Cardoso.
- Caption da Figura `method_agreement` corrigido para `agreement analysis layer`.
- Substituir `preferred` por `primary` em toda a Seção 5.
- Corrigir typo `thatorthographic`.
- Pequeno polimento da frase de `staged cost awareness`.

Itens que precisam de decisão sua:

- Renomear ou regerar `figure_05_study_design_v2.pdf`. Hoje só existe a versão sem `_v2`.
- Confirmar se queremos manter `30 drift terms` no Conclusion ou a redação genérica atual.
- Se preferir incluir uma referência de ciência política para `corrupcao` e `reforma` separadamente das theory seeds.

Posso aplicar todos os itens na seção `Aplicar com pequenas redações` em uma só passada e te passar o diff para revisar.