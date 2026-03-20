I am continuing work for my new experiment and future article with `Articles/N2` as the main workspace. You can also inspect other folders such as `Experiments/` and other `Articles/` folders when useful for past experiments, prior drafts, or methodological context.

Context:
- This folder is for a new STIL paper direction, separate from a previously submitted financial-disclosures article.
- The main results of that previous article must not be reused here.
- My advisor wants a Portuguese-focused conference paper.
- This project builds on earlier semantic-evolution experiments with `Roda Viva`, and `Roda Viva` remains an important complementary corpus and methodological starting point.
- You are allowed to inspect past experiments and prior article folders for context when helpful, but keep `Articles/N2` as the main place for new work.

Current plan:
- main corpus: `RawDatasets/BrPoliCorpus-Dataset/exports/floor`
- complementary corpus: `RawDatasets/Roda-Viva-Dataset/exports/V0-2/csv`
- main method: Word2Vec Skip-Gram 300d trained per time slice and aligned with Orthogonal Procrustes
- confirmatory method: `rufimelo/bert-large-portuguese-cased-sts`
- main time granularity: yearly
- first robustness check: semester

Suggestions for these local skills in the new chat:
- `uv-package-manager`- when creating project 
- `architecture-design` - project structure
- `python-code-style` - code 
- `citation-management` whenever researching citations, references, related papers, or BibTeX (need to use mcp valyu (and mcp exa as secondary) ALWAYS when verifying sources,etc...)
- `codebase-search` - analyzing code.
- `ml-paper-writing` - little help when writting article, but we are not submitting it to the journals there, we are submitting to STIL
- `stop-slop` - remove ai writting patterns in article.

Implementation preferences:
- use `uv` for environment and dependency management
- use `hydra` for configuration and experiment organization
- keep a clean experiment-oriented project structure with good modular organization
- do not overengineer the first version, but keep it extensible for later experiments
- produce good visualizations for outputs so semantic variation and model behavior are easy to understand
- make the visualizations varied and genuinely useful, not just minimal default plots
- include high-quality logging for the ML project, both for current runs and for inspecting past runs later
- keep runs, logs, metrics, artifacts, and outputs well organized on disk
- use checkpoints whenever running models or expensive steps, so progress is not lost if a run is interrupted
- avoid keeping critical outputs only in memory; persist intermediate results and artifacts to disk
- make each script or pipeline step detect whether required outputs already exist and reuse them when appropriate
- support resumable, restart-safe experimentation and follow good ML experimentation best practices throughout
- whenever researching citations or references, use the `citation-management` skill
- for citation and paper search, use MCP `valyu` first and MCP `exa` as a secondary source if needed

Please first read:
- `README.md`
- `docs/chat_handoff.md`
- `docs/project_overview.md`
- `docs/research_readiness_datasets.md`
- `docs/word_selection_protocol.md`
- `docs/semantic_change_literature_guide.md`
- `docs/embedding_strategy_nilc_word2vec.md`

Important constraints:
- do not pool `BrPoliCorpus` and `Roda Viva` into one raw timeline without controlling for genre
- treat `BrPoliCorpus floor` as the main experiment

Then help me continue from the current state in `N2`, using the docs and datasets already organized there.
