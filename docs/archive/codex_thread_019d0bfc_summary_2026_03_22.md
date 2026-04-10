# Codex thread summary: N2 comparative drift work

Session id: `019d0bfc-036b-7493-8fef-9e94970e7674`

Deeplink: `codex://threads/019d0bfc-036b-7493-8fef-9e94970e7674`

## Where the raw history lives

Codex stores rollout logs as JSONL under your home directory:

- Canonical: `/Users/victor/.codex/sessions/2026/03/20/rollout-2026-03-20T13-02-38-019d0bfc-036b-7493-8fef-9e94970e7674.jsonl`

A full copy of that log was written next to the thesis workspace for offline reference:

- `/Users/victor/Dropbox/USP/ResearchThesis/codex-thread-019d0bfc-036b-7493-8fef-9e94970e7674.txt`

That file is JSONL (one JSON object per line). Event kinds include `session_meta`, `turn_context`, `event_msg`, `response_item`, and `compacted`. User prompts and final turn summaries appear under `event_msg` with `payload.type` of `user_message` and `task_complete`.

## Session metadata (from log)

```json
{
  "id": "019d0bfc-036b-7493-8fef-9e94970e7674",
  "timestamp": "2026-03-20T16:02:38.582Z",
  "cwd": "/Users/victor/Dropbox/USP/ResearchThesis",
  "originator": "Codex Desktop",
  "cli_version": "0.116.0-alpha.10",
  "source": "vscode",
  "model_provider": "openai",
  "dynamic_tools": [
    {
      "name": "read_thread_terminal",
      "description": "Read the current app terminal output for this desktop thread. Use it when you need shell output or the current prompt before deciding the next step. This tool takes no arguments.",
      "inputSchema": {
        "type": "object",
        "properties": {},
        "additionalProperties": false
      },
      "deferLoading": false
    }
  ]
}
```

Working directory for the session: `/Users/victor/Dropbox/USP/ResearchThesis` (matches your N2 worktree).

## What this thread accomplished (high level)

This Codex conversation is the main execution thread for pivoting `Articles/N2` from a rushed Word2Vec quicklook toward an advisor aligned comparative drift paper in Brazilian Portuguese political text. The arc, as reflected in repo docs updated during the thread, includes:

1. **Pipeline audit** for comparability: documented gaps between the old single method framing and a multi method design (`docs/pipeline_audit_2026_03_20.md`, `docs/comparative_drift_methodology_2026_03_20.md`).
2. **Execution planning** (`docs/next_steps_execution_plan_2026_03_20.md`) and several long running **Word2Vec yearly baseline** attempts, cancellations, and performance tuning (workers, prep throughput).
3. **Frozen clean baseline** at `run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce`, with integrity notes about a later run id `8e15dc2372c5` (see `docs/progress_status_2026_03_20.md`, `docs/word2vec_baseline_freeze_2026_03_21.md`).
4. **Runtime and structure cleanup**: lazy BERT imports, config validation, prepared text versioning (`docs/runtime_config_cleanup_2026_03_21.md`, `docs/prepared_artifact_layout_2026_03_21.md`).
5. **PTPARL-V note** for a possible future corpus, without replacing BrPoliCorpus as primary (`docs/ptparl_v_vote_label_note.md`).
6. **Stronger candidate panel** so drift lists are not dominated by junk lemmas (`docs/candidate_panel_filter_2026_03_21.md`).
7. **TF-IDF drift stage** and artifacts on top of the frozen baseline (`docs/tfidf_drift_baseline_2026_03_22.md`).
8. **Shared comparison_panel** across methods (`docs/comparison_panel_2026_03_22.md`).
9. **BERT confirmatory path** refactored to consume the shared panel; device tuning when CPU beat MPS for your setup.

For the live handoff list of files to read next, use `docs/chat_handoff.md` and `docs/comparative_pipeline_readiness_2026_03_21.md`.

## Turn by turn (user prompts and Codex outcomes)

Below, each **User** block is the full prompt from the log. **Outcome** is the `last_agent_message` from `task_complete` when present. Aborts and rollbacks are called out explicitly.

### Turn 1 (2026-03-20T16:08:17.061Z)

**User**

```
[$codebase-search](/Users/victor/.agents/skills/codebase-search/SKILL.md) [$code-review-excellence](/Users/victor/.agents/skills/code-review-excellence/SKILL.md) 

I am continuing work in `/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2`.

Please first read these files for context:
- `/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/project_overview.md`
- `/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/chat_handoff.md`
- `/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/progress_status_2026_03_20.md`
- `/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/advisor_feedback_2026_03_20.md`
- `/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/exploratory_drift_comparison_plan.md`
- `/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/research_readiness_datasets.md`
- `/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/embedding_strategy_nilc_word2vec.md`
- `/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/word_selection_protocol.md`

Short context:
- Initial goal: build a Portuguese semantic-change / concept-drift paper for STIL using `BrPoliCorpus floor` as the main corpus and `Roda Viva` as a complementary corpus.
- Initial main method: yearly `Word2Vec Skip-Gram 300d` trained per slice and aligned with Orthogonal Procrustes, with `rufimelo/bert-large-portuguese-cased-sts` as confirmatory analysis.
- Important: we are not using the pretrained `nilc-nlp/word2vec-skip-gram-300d` vectors directly as the experiment output. We are using the NILC setup as the Portuguese reference recipe, while training our own slice-specific Word2Vec models on the corpus.
- We implemented a Hydra + `uv` experiment package and got a preliminary Word2Vec quicklook run.
- That quick run was useful, but it was rushed and not the final clean run. It helped us see some interpretable candidates, but the evidence was still weak as a standalone semantic-change paper because we do not have labels / ground truth.
- After advisor feedback, the project is pivoting into an exploratory comparative paper about drift techniques in Portuguese political discourse, especially comparing cheaper and heavier methods and analyzing correlation / disagreement between them.

Important experiment context:
- There is one completed preliminary quicklook run here:
  `/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ae5022228b99/quicklook/yearly_2003_2023_r1`
- There are later incomplete rerun directories here:
  `/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/4f821f885e1d`
  `/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/c5437a2643c5`

Current paper direction:
- Compare multiple drift techniques on the same Portuguese political corpus.
- At minimum: `TF-IDF`, `Word2Vec`, and `BERT`.
- Possibly include symbolic / lexical indicators such as `NILC-Metrix` as a support layer.
- Main question is no longer “prove semantic change,” but rather “how much do drift signals agree across methods, what kinds of terms does each method surface, and when is a cheaper method enough?”

What I want you to do:
1. Read the docs above and inspect the current N2 pipeline/codebase.
2. Check whether the current pipeline is actually in good shape for this new comparative direction.
3. Tell me what is reusable, what is too tied to the old framing, and what should be changed next.
4. Verify whether the current default pipeline is truly set up for the full clean Word2Vec run or whether important parts still reflect the earlier quick experimental path.
5. Recommend the next concrete implementation steps, with attention to experiment design, artifact organization, comparability across methods, and paper usefulness.

Please keep `Articles/N2` as the main workspace, but you may inspect other folders like `Experiments/` and other `Articles/` folders when helpful for prior methodology context.

We at the end will need better visualizaiton and script to compare embeddings, models in different categories like speed, dimensions, quality, size, best use case, source,etc.. (think or research in articles with mcp valyu or exa), only accept as a real articles if you use [$citation-management](/Users/victor/.agents/skills/citation-management/SKILL.md) and search primarly with valyu mcp and exa as secondary. Techniques, validations, statistical validations,experimentaitons, ,etc.... all need to be based in real examples so create md file aswell with citations and explain how and where we are doing anything we do in article.


Add, change, update tests for new implementations as needed. Add only good and necessary tests.

We are in branch for this feature, create commits as you go for good seperation and version control if we need to rollback, but NEVER push into remote. ONLY commits.


Use any skills or mcp needed:
[$architecture-design](/Users/victor/.codex/skills/architecture-design/SKILL.md) [$python-performance-optimization](/Users/victor/.agents/skills/python-performance-optimization/SKILL.md) [$python-code-style](/Users/victor/.agents/skills/python-code-style/SKILL.md) [$uv-package-manager](/Users/victor/.codex/skills/uv-package-manager/SKILL.md) 
/
```

**Outcome (Codex)**

The pipeline is reusable, but it is not yet comparison-ready. I wrote the audit in [pipeline_audit_2026_03_20.md](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/pipeline_audit_2026_03_20.md) and the article-facing implementation note with citations in [comparative_drift_methodology_2026_03_20.md](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/comparative_drift_methodology_2026_03_20.md).

What is solid and reusable: the shared corpus prep, Hydra artifact/config wiring, and the full Word2Vec arm. The strongest reusable modules are [loaders.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/data/loaders.py), [text.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/preprocessing/text.py), [train.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/word2vec/train.py), [align.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/word2vec/align.py), and [score.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/word2vec/score.py). What is still tied to the old framing: the default task graph in [config.yaml](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/conf/config.yaml) and [run_yearly_core.yaml](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/conf/task/run_yearly_core.yaml), the contextual stage in [confirmatory.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/contextual/confirmatory.py), and the reporting/readiness logic in [plots.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/reporting/plots.py) and [evaluation.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/reporting/evaluation.py). There is still no TF-IDF arm, no shared comparison panel, and no cross-method agreement stage.

The default code path does support a clean full Word2Vec run in principle, but the preserved artifacts do not show a completed clean baseline. The current repo mostly preserves logs and partial outputs from the quicklook/incomplete reruns, not one finished inspectable package with aligned scores, reports, and manifests. So the right answer is: code yes, preserved baseline no. I also found one paper-facing mismatch: the code is currently configured for `rufimelo/bert-large-portuguese-cased-sts`, while older notes discuss `BERTimbau`; the paper should not cite those as if they were the same model.

The next concrete steps I recommend are:
1. Produce one preserved clean Word2Vec baseline run before expanding the method set.
2. Implement a first-class `tfidf_drift` stage as the cheap baseline.
3. Add a method-neutral `comparison_panel.parquet` that merges top terms from each method, stable controls, and theory seeds.
4. Convert the current BERT path into a peer contextual stage that reads from the shared panel instead of Word2Vec `candidate_sets.json`.
5. Add a `compare_methods` stage for Spearman, Kendall, top-k overlap, Jaccard, disagreement packets, and runtime/cost summaries.
6. Replace the current single-method readiness report with a comparison-readiness report.

I also made one small pipeline hardening change: stage manifests now record runtime metadata in [runner.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/runner.py) and [artifacts.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/utils/artifacts.py), with test coverage updated in [test_integration_toy_pipeline.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/tests/test_integration_toy_pipeline.py). I ran `uv run pytest tests/test_integration_toy_pipeline.py tests/test_resumability.py tests/test_run_evaluation.py` and `uv run ruff check ...`; both passed.

Local commits only, no push:
- `ba5d3f9` `docs(audit): add comparative pipeline review`
- `9c93616` `feat(pipeline): record stage runtime metadata`
- `e900a46` `docs(methods): add comparative drift implementation note`

---

### Turn 2 (2026-03-20T16:59:01.763Z)

**User**

```
Go ahead and create md with the concrete next steps as plans. Then go ahead and run  clean Word2Vec baseline run before expanding the method set. Make sure its all correct, in first 5min of run (fix any problems that arises), then if its good, just give me tail command to check as we wait, and i will let you know when done
```

**Outcome (Codex)**

The plan doc is in [next_steps_execution_plan_2026_03_20.md](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/next_steps_execution_plan_2026_03_20.md).

The clean baseline run is now active and stable. In the first five minutes I caught and fixed the only startup issue: Hydra needed `+force=true` instead of `force=true`. After that, the run started cleanly, wrote the resolved config, and processed corpus-prep batches continuously with no dependency, spaCy, parquet, or dataset-parsing errors.

Current run/log path:
`/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/c5437a2643c5/logs/run_yearly_core.log`

Use this to watch it:

```bash
tail -n 50 -f /Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/c5437a2643c5/logs/run_yearly_core.log
```

When it finishes, let me know and I’ll verify the manifests/artifacts and freeze the clean baseline path in the docs.

---

### Turn 3 (2026-03-20T21:13:11.939Z)

**User**

```
Check how its going, and how long has it been, and how long left
```

**Outcome (Codex)**

Current status looks healthy.

- The current clean run started at `2026-03-20 14:00:39`.
- It has been running for about `4h 15m`.
- Corpus preparation is finished. That stage ended around `18:00:14`.
- It is now in `train_word2vec`, on `replicate 0`, training slice `2003`.
- Latest live progress I saw was `2026-03-20 18:15:37`, with slice `2003` at `EPOCH 0` and about `64%` through that epoch.
- Completed slice models so far in this clean run:
  - `2000` replicate `0`
  - `2001` replicate `0`
  - `2002` replicate `0`

Rough ETA:
- I’d estimate about `6h 45m` to `7h 15m` left.
- Reason: the expensive preparation stage is already done, but Word2Vec still has most of the work left:
  - `21` slices remaining in `replicate 0`
  - then full `replicate 1`
  - then full `replicate 2`
  - then alignment, scoring, and reporting

One note to keep an eye on:
- the log shows recurring lines like `Exception ignored in: 'gensim.models.word2vec_inner.our_dot_float'`
- so far they have not interrupted training; models are still saving correctly and progress is continuing

If you want to check it yourself right now, keep using:

```bash
tail -n 50 -f /Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/c5437a2643c5/logs/run_yearly_core.log
```

---

### Turn 4 (2026-03-20T21:17:22.622Z)

**User**

```
why is this so slow? if i rent a runpod, will it go faster?
```

**Aborted**

- Timestamp: `2026-03-20T21:17:24.552Z`
- Reason: `interrupted`
- Turn id: `019d0d1c-293b-70e2-be5f-b6517d0f1cf5`

### Turn 5 (2026-03-20T21:17:38.594Z)

**User**

```
why is this so slow? if i rent a runpod, will it go faster?

Did you optimize performance for run?
```

**Outcome (Codex)**

No, this run was not optimized for speed before launch.

The two biggest reasons are visible in the code:

- The model config is hard-coded to `workers: 1` in [word2vec_skipgram_300d.yaml](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/conf/model/word2vec_skipgram_300d.yaml), so Word2Vec is only using one training worker even though this machine has `8` CPU cores.
- The training iterator in [train.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/word2vec/train.py) re-reads every prepared parquet shard for every slice and every replicate, then filters to the current slice on the fly. That means a lot of repeated disk I/O on top of the actual training.

So the slowness is mostly:
- expected workload size: `24` yearly slices, `3` replicates, `10` epochs, `300d`
- plus avoidable config/code overhead: single-worker training and repeated shard scans

About Runpod:
- For this exact pipeline, a GPU-focused Runpod will not help much. This training path is `gensim` Word2Vec, which is CPU-bound here, not GPU-bound.
- A CPU-heavier remote box with fast local SSD could help, but only after we stop leaving performance on the table locally. If we keep `workers=1`, even a bigger machine will be underused.

So the honest answer is:
- `Will Runpod go faster?`
  - `GPU Runpod:` probably not by much for this exact code path
  - `CPU-rich machine:` yes, but mainly if we also raise workers and reduce repeated I/O
- `Did I optimize this run?`
  - No. I optimized for getting the clean baseline started correctly, not for minimum wall-clock time.

The highest-value fixes before the next serious run are:
1. Raise `model.workers` from `1` to something like `6` or `8`.
2. Stop re-reading all shard files for every slice; materialize or cache slice-specific training text once.
3. Keep `replicates=3` and `epochs=10` only if we still want that exact baseline design after the speed fixes.

At this point, because the current run still has many hours left, it may be worth stopping and restarting with the worker fix first. If you want, I can make the minimal performance changes and relaunch cleanly.

---

### Turn 6 (2026-03-20T21:24:46.444Z)

**User**

```
[$find-skills](/Users/victor/.agents/skills/find-skills/SKILL.md) search for skills in skills.sh that are popular that would be could for our project
```

**Outcome (Codex)**

I searched `skills.sh` with the `find-skills` workflow. For this project, the strongest external options are in visualization and research support; benchmarking results were much weaker.

Best fits for N2:

- `inferen-sh/skills@data-visualization`  
  Install: `npx skills add inferen-sh/skills@data-visualization`  
  Link: [skills.sh/inferen-sh/skills/data-visualization](https://skills.sh/inferen-sh/skills/data-visualization)  
  Why it fits: best general-purpose charting/visualization result by popularity (`5.8K installs`), useful for method-comparison figures, drift dashboards, overlap plots, and paper-ready visual summaries.

- `anthropics/knowledge-work-plugins@data-visualization`  
  Install: `npx skills add anthropics/knowledge-work-plugins@data-visualization`  
  Link: [skills.sh/anthropics/knowledge-work-plugins/data-visualization](https://skills.sh/anthropics/knowledge-work-plugins/data-visualization)  
  Why it fits: also popular (`2.5K installs`), likely better for analysis-to-figure workflows than flashy frontend work.

- `davila7/claude-code-templates@scientific-visualization`  
  Install: `npx skills add davila7/claude-code-templates@scientific-visualization`  
  Link: [skills.sh/davila7/claude-code-templates/scientific-visualization](https://skills.sh/davila7/claude-code-templates/scientific-visualization)  
  Why it fits: directly aligned with research plots and scientific presentation, even if less popular (`531 installs`).

- `shubhamsaboo/awesome-llm-apps@academic-researcher`  
  Install: `npx skills add shubhamsaboo/awesome-llm-apps@academic-researcher`  
  Link: [skills.sh/shubhamsaboo/awesome-llm-apps/academic-researcher](https://skills.sh/shubhamsaboo/awesome-llm-apps/academic-researcher)  
  Why it fits: useful for literature synthesis and research structuring (`2.2K installs`), though we already have good local research skills.

Worth considering, but lower priority:

- `jamditis/claude-skills-journalism@academic-writing`  
  Install: `npx skills add jamditis/claude-skills-journalism@academic-writing`  
  Link: [skills.sh/jamditis/claude-skills-journalism/academic-writing](https://skills.sh/jamditis/claude-skills-journalism/academic-writing)  
  Why it fits: could help polish paper prose, but we already have strong local writing/LaTeX skills.

Probably not worth adding for this project:

- Benchmarking results on `skills.sh` were weak and low-install.
  Best hit was `dotnet/skills@microbenchmarking`, which is not a good fit for this Python/NLP pipeline.
- Python performance search mostly returned versions of a skill we already effectively have locally.
  The top hit was `wshobson/agents@python-performance-optimization` with `11.6K installs`, but we already have [python-performance-optimization](/Users/victor/.agents/skills/python-performance-optimization/SKILL.md).

My recommendation:
- Install one visualization skill first:
  - `inferen-sh/skills@data-visualization`
  - or `davila7/claude-code-templates@scientific-visualization`
- Skip benchmarking/perf installs for now.
- Skip academic-writing installs unless you want extra paper-polish workflow beyond the local skills we already have.

If you want, I can install the top 1-2 recommended ones for you now.

---

### Turn 7 (2026-03-20T21:32:32.790Z)

**User**

```
Dont install anything.

Cancel this current run(delete all results), and optimize pipeline, Use 6 worker, and then optimize the rest of paraments aswell, this is word2vec, no need for super things here (because we will still run bert and tf-idf later). So please optimize wherever possible.

Also use any skills or mcp needed. 

[$python-performance-optimization](/Users/victor/.agents/skills/python-performance-optimization/SKILL.md) [$python-code-style](/Users/victor/.agents/skills/python-code-style/SKILL.md) [$architecture-design](/Users/victor/.codex/skills/architecture-design/SKILL.md) [$codebase-search](/Users/victor/.agents/skills/codebase-search/SKILL.md) [$code-review-excellence](/Users/victor/.agents/skills/code-review-excellence/SKILL.md)
```

**Outcome (Codex)**

The old run artifacts were removed, including the canceled experiment directory and its resolved config. I optimized the baseline in commit `dcd8942` by adding a per-slice prepared corpus cache, so training no longer rescans every parquet shard for every year/replicate, and by tuning the default Word2Vec baseline to `workers=6`, `negative=5`, `epochs=5`, and `replicates=2` while keeping `300d`.

I verified the new path with tests and lint: `4 passed in 11.66s`, and `ruff check` passed. The new clean baseline run is active under [run_yearly_core.log](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/fcd496682944/logs/run_yearly_core.log). I watched the first 5 minutes of startup: corpus prep advanced continuously through batch 29 with no errors, the new `prepared/slice_sentences/` cache is being written, and the resolved config confirms the tuned settings.

Use this to monitor it while it runs:

```bash
tail -n 50 -f /Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/fcd496682944/logs/run_yearly_core.log
```

When it finishes, tell me and I’ll verify the final artifacts and freeze this as the clean Word2Vec baseline.

---

### Turn 8 (2026-03-20T21:53:40.532Z)

**User**

```
how long will this version be?
```

**Outcome (Codex)**

As of **March 20, 2026, 18:54 BRT**, this run is still in `prepare_corpus`.

Right now the estimate is:

- `97 / 1826` prep batches done, about **5.3%**
- elapsed so far: about **16.8 minutes**
- current prep speed: about **10.4 seconds per batch**
- projected prep time alone: about **5.3 hours total**
- prep time remaining: about **4.9 to 5.1 hours**

Then we still need:

- Word2Vec training for **24 slices x 2 replicates = 48 models**
- alignment
- scoring
- report generation

So my current best estimate for the **full optimized run** is:

- **about 6 to 8 hours total**
- **about 5 to 7 hours left from now**

Important detail: the new `6 workers` setting only speeds up the **Word2Vec training** stage. The run is currently slow because the bottleneck right now is still **CSV reading + spaCy preprocessing**, not Word2Vec itself.

If you want, next I can optimize the preprocessing stage too, which is where the biggest remaining time savings are.

---

### Turn 9 (2026-03-21T00:42:38.348Z)

**User**

```
I canceled yout run, can you start again pelase
```

**Aborted**

- Timestamp: `2026-03-21T00:42:47.809Z`
- Reason: `interrupted`
- Turn id: `019d0dd8-1589-72c1-ab69-9bf6799b2973`

**Thread rolled back**

- Timestamp: `2026-03-21T00:43:24.412Z`
- Payload: `{"type": "thread_rolled_back", "num_turns": 1}`

### Turn 10 (2026-03-21T00:43:24.565Z)

**User**

```
I canceled yout run. Please optimize everything possible (thats not unreasonable, and considered standard). After that start it again and give me tail command
```

**Outcome (Codex)**

I optimized the standard low-risk path end to end and restarted the baseline.

Main changes now in the branch:
- `dcd8942` `perf(word2vec): cache slice corpora and tune baseline defaults`
- `861d783` `perf(preprocess): parallelize spaCy and reduce prep overhead`
- `3441b02` `perf(artifacts): trim prepared shard payloads`

What changed in practice:
- Word2Vec trains from per-slice sentence files instead of rescanning all parquet shards
- Word2Vec defaults are lighter but still reasonable for the comparative paper: `300d`, `workers=6`, `negative=5`, `epochs=5`, `replicates=2`
- CSV ingest uses larger chunks
- spaCy preprocessing now runs with `n_process=6` and larger batch size
- prepared docs/tokens only keep fields the later pipeline actually uses

The fresh run is active and startup looks clean. Current log is [run_yearly_core.log](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/logs/run_yearly_core.log).

Use this to watch it:

```bash
tail -n 50 -f /Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/logs/run_yearly_core.log
```

When it finishes, tell me and I’ll verify the full artifact set.

---

### Turn 11 (2026-03-21T00:56:22.106Z)

**User**

```
check logs and based on current runs, ee how long it will take
```

**Outcome (Codex)**

As of **March 20, 2026, 21:57 BRT**, the run is still in `prepare_corpus`.

From the current log:

- completed prep batches: `10 / 490`
- elapsed prep time: about **5.4 minutes**
- current prep speed: about **36.0 seconds per batch**
- projected prep remaining: about **17,280 seconds**, which is **4.8 hours**
- projected prep total: about **4.9 hours**

So the best estimate right now is:

- `prepare_corpus`: **about 4 hours 45 minutes to 5 hours left**
- full pipeline including Word2Vec + alignment + scoring + reports: **about 5.5 to 7 hours left**

Why the range is still wide:
- we have a solid estimate for prep now
- we do **not** yet have live timing for the new Word2Vec stage on this exact run
- but Word2Vec should be noticeably cheaper than before because it now uses:
  - per-slice cached corpora
  - `workers=6`
  - `epochs=5`
  - `negative=5`
  - `replicates=2`

If you want, I can check again once prep gets closer to completion or once the first few Word2Vec slice models finish, and then I can give a much tighter ETA.

---

### Turn 12 (2026-03-21T08:44:47.815Z)

**User**

```
did i finish? hasunt updated in 2 hrs:

2026-03-21 03:56:04 | INFO | gensim.utils | Word2Vec lifecycle event {'update': False, 'trim_rule': 'None', 'datetime': '2026-03-21T03:56:04.479242', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'build_vocab'}
2026-03-21 03:56:04 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training model with 6 workers on 17907 vocabulary and 300 features, using sg=1 hs=0 sample=0.001 negative=5 window=5 shrink_windows=True', 'datetime': '2026-03-21T03:56:04.479410', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 03:56:05 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 18.35% examples, 597454 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:06 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 37.60% examples, 619127 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:07 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 90.09% examples, 632979 words/s, in_qsize 10, out_qsize 1
2026-03-21 03:56:08 | INFO | gensim.models.word2vec | EPOCH 0: training on 2521155 raw words (2333689 effective words) took 3.7s, 636938 effective words/s
2026-03-21 03:56:09 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 18.07% examples, 613117 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:10 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 36.19% examples, 626272 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:11 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 88.98% examples, 641492 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:56:11 | INFO | gensim.models.word2vec | EPOCH 1: training on 2521155 raw words (2333359 effective words) took 3.6s, 646834 effective words/s
2026-03-21 03:56:12 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 18.07% examples, 616746 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:13 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 36.42% examples, 622664 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:14 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 88.35% examples, 630081 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:56:15 | INFO | gensim.models.word2vec | EPOCH 2: training on 2521155 raw words (2333640 effective words) took 3.7s, 638168 effective words/s
2026-03-21 03:56:16 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 18.07% examples, 600339 words/s, in_qsize 10, out_qsize 1
2026-03-21 03:56:17 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 36.72% examples, 629745 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:18 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 89.52% examples, 641650 words/s, in_qsize 11, out_qsize 1
2026-03-21 03:56:19 | INFO | gensim.models.word2vec | EPOCH 3: training on 2521155 raw words (2333575 effective words) took 3.6s, 643054 effective words/s
2026-03-21 03:56:20 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 17.22% examples, 591254 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:21 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 35.50% examples, 616871 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:22 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 86.96% examples, 622713 words/s, in_qsize 11, out_qsize 1
2026-03-21 03:56:22 | INFO | gensim.models.word2vec | EPOCH 4: training on 2521155 raw words (2333670 effective words) took 3.7s, 631122 effective words/s
2026-03-21 03:56:22 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training on 12605775 raw words (11667933 effective words) took 18.3s, 639036 effective words/s', 'datetime': '2026-03-21T03:56:22.738283', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 03:56:22 | INFO | gensim.utils | Word2Vec lifecycle event {'params': 'Word2Vec<vocab=17907, vector_size=300, alpha=0.025>', 'datetime': '2026-03-21T03:56:22.738341', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'created'}
2026-03-21 03:56:22 | INFO | gensim.utils | Word2Vec lifecycle event {'fname_or_handle': '/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2011/word2vec.model', 'separately': 'None', 'sep_limit': 10485760, 'ignore': frozenset(), 'datetime': '2026-03-21T03:56:22.739253', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'saving'}
2026-03-21 03:56:22 | INFO | gensim.utils | not storing attribute cum_table
2026-03-21 03:56:22 | INFO | gensim.utils | saved /Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2011/word2vec.model
2026-03-21 03:56:23 | INFO | stil_semantic_change.word2vec.train | Trained Word2Vec for slice 2011 replicate 1 with 17907 words
2026-03-21 03:56:23 | INFO | gensim.models.word2vec | collecting all words and their counts
2026-03-21 03:56:23 | INFO | gensim.models.word2vec | PROGRESS: at sentence #0, processed 0 words, keeping 0 word types
2026-03-21 03:56:23 | INFO | gensim.models.word2vec | PROGRESS: at sentence #10000, processed 1714698 words, keeping 39146 word types
2026-03-21 03:56:23 | INFO | gensim.models.word2vec | collected 47530 word types from a corpus of 2623384 raw words and 15161 sentences
2026-03-21 03:56:23 | INFO | gensim.models.word2vec | Creating a fresh vocabulary
2026-03-21 03:56:23 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'effective_min_count=5 retains 17189 unique words (36.16% of original 47530, drops 30341)', 'datetime': '2026-03-21T03:56:23.972171', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:56:23 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'effective_min_count=5 leaves 2573191 word corpus (98.09% of original 2623384, drops 50193)', 'datetime': '2026-03-21T03:56:23.972318', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:56:24 | INFO | gensim.models.word2vec | deleting the raw counts dictionary of 47530 items
2026-03-21 03:56:24 | INFO | gensim.models.word2vec | sample=0.001 downsamples 20 most-common words
2026-03-21 03:56:24 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'downsampling leaves estimated 2455435.9617432603 word corpus (95.4%% of prior 2573191)', 'datetime': '2026-03-21T03:56:24.003049', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:56:24 | INFO | gensim.models.word2vec | estimated required memory for 17189 words and 300 dimensions: 49848100 bytes
2026-03-21 03:56:24 | INFO | gensim.models.word2vec | resetting layer weights
2026-03-21 03:56:24 | INFO | gensim.utils | Word2Vec lifecycle event {'update': False, 'trim_rule': 'None', 'datetime': '2026-03-21T03:56:24.082286', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'build_vocab'}
2026-03-21 03:56:24 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training model with 6 workers on 17189 vocabulary and 300 features, using sg=1 hs=0 sample=0.001 negative=5 window=5 shrink_windows=True', 'datetime': '2026-03-21T03:56:24.082450', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 03:56:25 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 25.90% examples, 613150 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:26 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 51.13% examples, 622105 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:27 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 78.49% examples, 632217 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:27 | INFO | gensim.models.word2vec | EPOCH 0: training on 2623384 raw words (2455053 effective words) took 3.9s, 634009 effective words/s
2026-03-21 03:56:28 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 25.61% examples, 599999 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:56:29 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 51.06% examples, 617733 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:30 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 78.86% examples, 631839 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:31 | INFO | gensim.models.word2vec | EPOCH 1: training on 2623384 raw words (2455562 effective words) took 3.8s, 641769 effective words/s
2026-03-21 03:56:32 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 26.54% examples, 636793 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:56:33 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 53.78% examples, 656223 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:34 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 81.38% examples, 655032 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:35 | INFO | gensim.models.word2vec | EPOCH 2: training on 2623384 raw words (2455806 effective words) took 3.7s, 661831 effective words/s
2026-03-21 03:56:36 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 25.90% examples, 615459 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:37 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 53.02% examples, 643022 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:38 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 80.76% examples, 648454 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:39 | INFO | gensim.models.word2vec | EPOCH 3: training on 2623384 raw words (2455103 effective words) took 3.8s, 648820 effective words/s
2026-03-21 03:56:40 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 26.25% examples, 620863 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:41 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 53.43% examples, 644505 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:42 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 81.38% examples, 651169 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:56:43 | INFO | gensim.models.word2vec | EPOCH 4: training on 2623384 raw words (2456026 effective words) took 3.7s, 656740 effective words/s
2026-03-21 03:56:43 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training on 13116920 raw words (12277550 effective words) took 18.9s, 648349 effective words/s', 'datetime': '2026-03-21T03:56:43.019304', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 03:56:43 | INFO | gensim.utils | Word2Vec lifecycle event {'params': 'Word2Vec<vocab=17189, vector_size=300, alpha=0.025>', 'datetime': '2026-03-21T03:56:43.019361', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'created'}
2026-03-21 03:56:43 | INFO | gensim.utils | Word2Vec lifecycle event {'fname_or_handle': '/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2012/word2vec.model', 'separately': 'None', 'sep_limit': 10485760, 'ignore': frozenset(), 'datetime': '2026-03-21T03:56:43.020422', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'saving'}
2026-03-21 03:56:43 | INFO | gensim.utils | not storing attribute cum_table
2026-03-21 03:56:43 | INFO | gensim.utils | saved /Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2012/word2vec.model
2026-03-21 03:56:43 | INFO | stil_semantic_change.word2vec.train | Trained Word2Vec for slice 2012 replicate 1 with 17189 words
2026-03-21 03:56:43 | INFO | gensim.models.word2vec | collecting all words and their counts
2026-03-21 03:56:43 | INFO | gensim.models.word2vec | PROGRESS: at sentence #0, processed 0 words, keeping 0 word types
2026-03-21 03:56:43 | INFO | gensim.models.word2vec | PROGRESS: at sentence #10000, processed 1500734 words, keeping 37206 word types
2026-03-21 03:56:44 | INFO | gensim.models.word2vec | PROGRESS: at sentence #20000, processed 3070880 words, keeping 51112 word types
2026-03-21 03:56:44 | INFO | gensim.models.word2vec | collected 58114 word types from a corpus of 4123806 raw words and 26307 sentences
2026-03-21 03:56:44 | INFO | gensim.models.word2vec | Creating a fresh vocabulary
2026-03-21 03:56:44 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'effective_min_count=5 retains 21353 unique words (36.74% of original 58114, drops 36761)', 'datetime': '2026-03-21T03:56:44.496015', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:56:44 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'effective_min_count=5 leaves 4063603 word corpus (98.54% of original 4123806, drops 60203)', 'datetime': '2026-03-21T03:56:44.496164', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:56:44 | INFO | gensim.models.word2vec | deleting the raw counts dictionary of 58114 items
2026-03-21 03:56:44 | INFO | gensim.models.word2vec | sample=0.001 downsamples 25 most-common words
2026-03-21 03:56:44 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'downsampling leaves estimated 3842181.3379345573 word corpus (94.6%% of prior 4063603)', 'datetime': '2026-03-21T03:56:44.535932', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:56:44 | INFO | gensim.models.word2vec | estimated required memory for 21353 words and 300 dimensions: 61923700 bytes
2026-03-21 03:56:44 | INFO | gensim.models.word2vec | resetting layer weights
2026-03-21 03:56:44 | INFO | gensim.utils | Word2Vec lifecycle event {'update': False, 'trim_rule': 'None', 'datetime': '2026-03-21T03:56:44.633362', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'build_vocab'}
2026-03-21 03:56:44 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training model with 6 workers on 21353 vocabulary and 300 features, using sg=1 hs=0 sample=0.001 negative=5 window=5 shrink_windows=True', 'datetime': '2026-03-21T03:56:44.633534', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 03:56:45 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 16.71% examples, 595362 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:46 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 33.72% examples, 605863 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:47 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 50.96% examples, 612250 words/s, in_qsize 11, out_qsize 1
2026-03-21 03:56:48 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 67.21% examples, 618885 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:49 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 82.97% examples, 621293 words/s, in_qsize 10, out_qsize 1
2026-03-21 03:56:50 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 98.73% examples, 622555 words/s, in_qsize 6, out_qsize 0
2026-03-21 03:56:50 | INFO | gensim.models.word2vec | EPOCH 0: training on 4123806 raw words (3842105 effective words) took 6.2s, 623534 effective words/s
2026-03-21 03:56:51 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 16.03% examples, 578122 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:52 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 33.40% examples, 610201 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:53 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 50.97% examples, 618579 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:56:54 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 67.50% examples, 628057 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:56:55 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 82.68% examples, 624583 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:56:56 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 98.04% examples, 622345 words/s, in_qsize 9, out_qsize 0
2026-03-21 03:56:56 | INFO | gensim.models.word2vec | EPOCH 1: training on 4123806 raw words (3841640 effective words) took 6.1s, 625422 effective words/s
2026-03-21 03:56:57 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 16.35% examples, 589584 words/s, in_qsize 11, out_qsize 1
2026-03-21 03:56:58 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 33.40% examples, 613945 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:56:59 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 50.67% examples, 616401 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:00 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 66.40% examples, 617555 words/s, in_qsize 11, out_qsize 2
2026-03-21 03:57:01 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 82.38% examples, 621417 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:57:02 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 97.54% examples, 619712 words/s, in_qsize 10, out_qsize 1
2026-03-21 03:57:03 | INFO | gensim.models.word2vec | EPOCH 2: training on 4123806 raw words (3841890 effective words) took 6.2s, 624345 effective words/s
2026-03-21 03:57:04 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 16.03% examples, 579267 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:05 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 33.14% examples, 610236 words/s, in_qsize 11, out_qsize 1
2026-03-21 03:57:06 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 50.67% examples, 618579 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:07 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 66.96% examples, 623777 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:08 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 82.91% examples, 627938 words/s, in_qsize 10, out_qsize 1
2026-03-21 03:57:09 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 99.54% examples, 631287 words/s, in_qsize 2, out_qsize 1
2026-03-21 03:57:09 | INFO | gensim.models.word2vec | EPOCH 3: training on 4123806 raw words (3841725 effective words) took 6.1s, 633416 effective words/s
2026-03-21 03:57:10 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 16.96% examples, 608171 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:11 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 33.40% examples, 609937 words/s, in_qsize 10, out_qsize 1
2026-03-21 03:57:12 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 51.26% examples, 620352 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:13 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 66.96% examples, 619699 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:14 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 83.26% examples, 623167 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:15 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 99.78% examples, 628387 words/s, in_qsize 1, out_qsize 1
2026-03-21 03:57:15 | INFO | gensim.models.word2vec | EPOCH 4: training on 4123806 raw words (3842022 effective words) took 6.1s, 629513 effective words/s
2026-03-21 03:57:15 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training on 20619030 raw words (19209382 effective words) took 30.6s, 627143 effective words/s', 'datetime': '2026-03-21T03:57:15.263848', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 03:57:15 | INFO | gensim.utils | Word2Vec lifecycle event {'params': 'Word2Vec<vocab=21353, vector_size=300, alpha=0.025>', 'datetime': '2026-03-21T03:57:15.263909', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'created'}
2026-03-21 03:57:15 | INFO | gensim.utils | Word2Vec lifecycle event {'fname_or_handle': '/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2013/word2vec.model', 'separately': 'None', 'sep_limit': 10485760, 'ignore': frozenset(), 'datetime': '2026-03-21T03:57:15.264813', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'saving'}
2026-03-21 03:57:15 | INFO | gensim.utils | not storing attribute cum_table
2026-03-21 03:57:15 | INFO | gensim.utils | saved /Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2013/word2vec.model
2026-03-21 03:57:16 | INFO | stil_semantic_change.word2vec.train | Trained Word2Vec for slice 2013 replicate 1 with 21353 words
2026-03-21 03:57:16 | INFO | gensim.models.word2vec | collecting all words and their counts
2026-03-21 03:57:16 | INFO | gensim.models.word2vec | PROGRESS: at sentence #0, processed 0 words, keeping 0 word types
2026-03-21 03:57:16 | INFO | gensim.models.word2vec | PROGRESS: at sentence #10000, processed 1570384 words, keeping 39279 word types
2026-03-21 03:57:16 | INFO | gensim.models.word2vec | collected 49520 word types from a corpus of 2639168 raw words and 16556 sentences
2026-03-21 03:57:16 | INFO | gensim.models.word2vec | Creating a fresh vocabulary
2026-03-21 03:57:16 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'effective_min_count=5 retains 17639 unique words (35.62% of original 49520, drops 31881)', 'datetime': '2026-03-21T03:57:16.619438', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:57:16 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'effective_min_count=5 leaves 2586805 word corpus (98.02% of original 2639168, drops 52363)', 'datetime': '2026-03-21T03:57:16.619584', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:57:16 | INFO | gensim.models.word2vec | deleting the raw counts dictionary of 49520 items
2026-03-21 03:57:16 | INFO | gensim.models.word2vec | sample=0.001 downsamples 24 most-common words
2026-03-21 03:57:16 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'downsampling leaves estimated 2445838.683950619 word corpus (94.6%% of prior 2586805)', 'datetime': '2026-03-21T03:57:16.653398', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:57:16 | INFO | gensim.models.word2vec | estimated required memory for 17639 words and 300 dimensions: 51153100 bytes
2026-03-21 03:57:16 | INFO | gensim.models.word2vec | resetting layer weights
2026-03-21 03:57:16 | INFO | gensim.utils | Word2Vec lifecycle event {'update': False, 'trim_rule': 'None', 'datetime': '2026-03-21T03:57:16.731435', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'build_vocab'}
2026-03-21 03:57:16 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training model with 6 workers on 17639 vocabulary and 300 features, using sg=1 hs=0 sample=0.001 negative=5 window=5 shrink_windows=True', 'datetime': '2026-03-21T03:57:16.731610', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 03:57:17 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 23.12% examples, 578278 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:18 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 50.20% examples, 602218 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:19 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 77.25% examples, 615947 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:20 | INFO | gensim.models.word2vec | EPOCH 0: training on 2639168 raw words (2436444 effective words) took 3.9s, 619946 effective words/s
2026-03-21 03:57:21 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 24.53% examples, 610532 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:22 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 53.43% examples, 635669 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:23 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 79.69% examples, 637576 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:24 | INFO | gensim.models.word2vec | EPOCH 1: training on 2639168 raw words (2436361 effective words) took 3.8s, 637976 effective words/s
2026-03-21 03:57:25 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 24.53% examples, 607896 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:57:26 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 52.52% examples, 627221 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:57:27 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 79.69% examples, 638742 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:28 | INFO | gensim.models.word2vec | EPOCH 2: training on 2639168 raw words (2436449 effective words) took 3.8s, 643064 effective words/s
2026-03-21 03:57:29 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 24.97% examples, 620086 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:57:30 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 53.43% examples, 638639 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:57:31 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 80.03% examples, 642424 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:57:32 | INFO | gensim.models.word2vec | EPOCH 3: training on 2639168 raw words (2436438 effective words) took 3.8s, 648806 effective words/s
2026-03-21 03:57:33 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 24.53% examples, 611530 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:34 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 52.98% examples, 633547 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:35 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 80.03% examples, 638200 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:35 | INFO | gensim.models.word2vec | EPOCH 4: training on 2639168 raw words (2436484 effective words) took 3.8s, 644688 effective words/s
2026-03-21 03:57:35 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training on 13195840 raw words (12182176 effective words) took 19.1s, 638587 effective words/s', 'datetime': '2026-03-21T03:57:35.808594', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 03:57:35 | INFO | gensim.utils | Word2Vec lifecycle event {'params': 'Word2Vec<vocab=17639, vector_size=300, alpha=0.025>', 'datetime': '2026-03-21T03:57:35.808654', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'created'}
2026-03-21 03:57:35 | INFO | gensim.utils | Word2Vec lifecycle event {'fname_or_handle': '/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2014/word2vec.model', 'separately': 'None', 'sep_limit': 10485760, 'ignore': frozenset(), 'datetime': '2026-03-21T03:57:35.809863', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'saving'}
2026-03-21 03:57:35 | INFO | gensim.utils | not storing attribute cum_table
2026-03-21 03:57:35 | INFO | gensim.utils | saved /Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2014/word2vec.model
2026-03-21 03:57:36 | INFO | stil_semantic_change.word2vec.train | Trained Word2Vec for slice 2014 replicate 1 with 17639 words
2026-03-21 03:57:36 | INFO | gensim.models.word2vec | collecting all words and their counts
2026-03-21 03:57:36 | INFO | gensim.models.word2vec | PROGRESS: at sentence #0, processed 0 words, keeping 0 word types
2026-03-21 03:57:36 | INFO | gensim.models.word2vec | PROGRESS: at sentence #10000, processed 1356702 words, keeping 34600 word types
2026-03-21 03:57:36 | INFO | gensim.models.word2vec | PROGRESS: at sentence #20000, processed 2685656 words, keeping 46669 word types
2026-03-21 03:57:37 | INFO | gensim.models.word2vec | collected 53046 word types from a corpus of 3593898 raw words and 26868 sentences
2026-03-21 03:57:37 | INFO | gensim.models.word2vec | Creating a fresh vocabulary
2026-03-21 03:57:37 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'effective_min_count=5 retains 19463 unique words (36.69% of original 53046, drops 33583)', 'datetime': '2026-03-21T03:57:37.179305', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:57:37 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'effective_min_count=5 leaves 3538671 word corpus (98.46% of original 3593898, drops 55227)', 'datetime': '2026-03-21T03:57:37.179453', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:57:37 | INFO | gensim.models.word2vec | deleting the raw counts dictionary of 53046 items
2026-03-21 03:57:37 | INFO | gensim.models.word2vec | sample=0.001 downsamples 25 most-common words
2026-03-21 03:57:37 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'downsampling leaves estimated 3332409.1919969153 word corpus (94.2%% of prior 3538671)', 'datetime': '2026-03-21T03:57:37.213781', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:57:37 | INFO | gensim.models.word2vec | estimated required memory for 19463 words and 300 dimensions: 56442700 bytes
2026-03-21 03:57:37 | INFO | gensim.models.word2vec | resetting layer weights
2026-03-21 03:57:37 | INFO | gensim.utils | Word2Vec lifecycle event {'update': False, 'trim_rule': 'None', 'datetime': '2026-03-21T03:57:37.310667', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'build_vocab'}
2026-03-21 03:57:37 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training model with 6 workers on 19463 vocabulary and 300 features, using sg=1 hs=0 sample=0.001 negative=5 window=5 shrink_windows=True', 'datetime': '2026-03-21T03:57:37.311268', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 03:57:38 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 17.52% examples, 606082 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:57:39 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 37.17% examples, 623657 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:57:40 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 56.36% examples, 631184 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:41 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 77.24% examples, 638728 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:42 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 97.56% examples, 642264 words/s, in_qsize 10, out_qsize 0
2026-03-21 03:57:42 | INFO | gensim.models.word2vec | EPOCH 0: training on 3593898 raw words (3323729 effective words) took 5.2s, 643505 effective words/s
2026-03-21 03:57:43 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 17.41% examples, 595003 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:44 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 37.87% examples, 631029 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:45 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 57.20% examples, 635789 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:46 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 77.24% examples, 632535 words/s, in_qsize 11, out_qsize 1
2026-03-21 03:57:47 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 95.87% examples, 625590 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:57:47 | INFO | gensim.models.word2vec | EPOCH 1: training on 3593898 raw words (3324088 effective words) took 5.3s, 628933 effective words/s
2026-03-21 03:57:48 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 17.21% examples, 595885 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:49 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 37.17% examples, 626048 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:50 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 56.64% examples, 636168 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:57:51 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 77.26% examples, 639573 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:52 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 97.71% examples, 641990 words/s, in_qsize 10, out_qsize 0
2026-03-21 03:57:52 | INFO | gensim.models.word2vec | EPOCH 2: training on 3593898 raw words (3324024 effective words) took 5.2s, 642936 effective words/s
2026-03-21 03:57:53 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 17.78% examples, 612624 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:54 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 37.17% examples, 625249 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:55 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 56.64% examples, 633639 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:57:56 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 77.26% examples, 637133 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:57:57 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 97.71% examples, 640649 words/s, in_qsize 10, out_qsize 0
2026-03-21 03:57:58 | INFO | gensim.models.word2vec | EPOCH 3: training on 3593898 raw words (3323894 effective words) took 5.2s, 645167 effective words/s
2026-03-21 03:57:59 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 18.12% examples, 613643 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:00 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 38.10% examples, 634966 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:01 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 57.82% examples, 635953 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:02 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 78.71% examples, 640293 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:03 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 98.17% examples, 639641 words/s, in_qsize 8, out_qsize 0
2026-03-21 03:58:03 | INFO | gensim.models.word2vec | EPOCH 4: training on 3593898 raw words (3324598 effective words) took 5.2s, 642812 effective words/s
2026-03-21 03:58:03 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training on 17969490 raw words (16620333 effective words) took 25.9s, 640518 effective words/s', 'datetime': '2026-03-21T03:58:03.259918', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 03:58:03 | INFO | gensim.utils | Word2Vec lifecycle event {'params': 'Word2Vec<vocab=19463, vector_size=300, alpha=0.025>', 'datetime': '2026-03-21T03:58:03.259987', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'created'}
2026-03-21 03:58:03 | INFO | gensim.utils | Word2Vec lifecycle event {'fname_or_handle': '/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2015/word2vec.model', 'separately': 'None', 'sep_limit': 10485760, 'ignore': frozenset(), 'datetime': '2026-03-21T03:58:03.260878', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'saving'}
2026-03-21 03:58:03 | INFO | gensim.utils | not storing attribute cum_table
2026-03-21 03:58:03 | INFO | gensim.utils | saved /Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2015/word2vec.model
2026-03-21 03:58:04 | INFO | stil_semantic_change.word2vec.train | Trained Word2Vec for slice 2015 replicate 1 with 19463 words
2026-03-21 03:58:04 | INFO | gensim.models.word2vec | collecting all words and their counts
2026-03-21 03:58:04 | INFO | gensim.models.word2vec | PROGRESS: at sentence #0, processed 0 words, keeping 0 word types
2026-03-21 03:58:04 | INFO | gensim.models.word2vec | PROGRESS: at sentence #10000, processed 1347052 words, keeping 36025 word types
2026-03-21 03:58:04 | INFO | gensim.models.word2vec | PROGRESS: at sentence #20000, processed 2693683 words, keeping 48397 word types
2026-03-21 03:58:04 | INFO | gensim.models.word2vec | collected 50379 word types from a corpus of 2961377 raw words and 22042 sentences
2026-03-21 03:58:04 | INFO | gensim.models.word2vec | Creating a fresh vocabulary
2026-03-21 03:58:04 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'effective_min_count=5 retains 18244 unique words (36.21% of original 50379, drops 32135)', 'datetime': '2026-03-21T03:58:04.617463', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:58:04 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'effective_min_count=5 leaves 2908755 word corpus (98.22% of original 2961377, drops 52622)', 'datetime': '2026-03-21T03:58:04.617603', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:58:04 | INFO | gensim.models.word2vec | deleting the raw counts dictionary of 50379 items
2026-03-21 03:58:04 | INFO | gensim.models.word2vec | sample=0.001 downsamples 26 most-common words
2026-03-21 03:58:04 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'downsampling leaves estimated 2730842.1653731083 word corpus (93.9%% of prior 2908755)', 'datetime': '2026-03-21T03:58:04.651413', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:58:04 | INFO | gensim.models.word2vec | estimated required memory for 18244 words and 300 dimensions: 52907600 bytes
2026-03-21 03:58:04 | INFO | gensim.models.word2vec | resetting layer weights
2026-03-21 03:58:04 | INFO | gensim.utils | Word2Vec lifecycle event {'update': False, 'trim_rule': 'None', 'datetime': '2026-03-21T03:58:04.732997', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'build_vocab'}
2026-03-21 03:58:04 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training model with 6 workers on 18244 vocabulary and 300 features, using sg=1 hs=0 sample=0.001 negative=5 window=5 shrink_windows=True', 'datetime': '2026-03-21T03:58:04.733148', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 03:58:05 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 23.41% examples, 587368 words/s, in_qsize 10, out_qsize 1
2026-03-21 03:58:06 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 46.43% examples, 609134 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:58:07 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 70.86% examples, 622690 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:08 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 95.21% examples, 627246 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:58:09 | INFO | gensim.models.word2vec | EPOCH 0: training on 2961377 raw words (2725375 effective words) took 4.3s, 633665 effective words/s
2026-03-21 03:58:10 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 23.41% examples, 607161 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:11 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 46.89% examples, 633057 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:58:12 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 70.86% examples, 634302 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:13 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 94.24% examples, 633564 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:13 | INFO | gensim.models.word2vec | EPOCH 1: training on 2961377 raw words (2725780 effective words) took 4.3s, 639468 effective words/s
2026-03-21 03:58:14 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 23.41% examples, 610921 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:15 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 46.89% examples, 631465 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:16 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 70.86% examples, 633772 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:17 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 94.98% examples, 635181 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:17 | INFO | gensim.models.word2vec | EPOCH 2: training on 2961377 raw words (2724876 effective words) took 4.2s, 642712 effective words/s
2026-03-21 03:58:18 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 23.41% examples, 606461 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:19 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 46.89% examples, 631476 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:58:20 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 70.86% examples, 630263 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:58:21 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 95.81% examples, 639610 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:21 | INFO | gensim.models.word2vec | EPOCH 3: training on 2961377 raw words (2725141 effective words) took 4.2s, 642931 effective words/s
2026-03-21 03:58:22 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 23.57% examples, 618188 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:23 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 47.84% examples, 640854 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:24 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 71.34% examples, 637738 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:25 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 94.69% examples, 636525 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:58:26 | INFO | gensim.models.word2vec | EPOCH 4: training on 2961377 raw words (2725172 effective words) took 4.3s, 640199 effective words/s
2026-03-21 03:58:26 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training on 14806885 raw words (13626344 effective words) took 21.3s, 639664 effective words/s', 'datetime': '2026-03-21T03:58:26.035757', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 03:58:26 | INFO | gensim.utils | Word2Vec lifecycle event {'params': 'Word2Vec<vocab=18244, vector_size=300, alpha=0.025>', 'datetime': '2026-03-21T03:58:26.035821', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'created'}
2026-03-21 03:58:26 | INFO | gensim.utils | Word2Vec lifecycle event {'fname_or_handle': '/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2016/word2vec.model', 'separately': 'None', 'sep_limit': 10485760, 'ignore': frozenset(), 'datetime': '2026-03-21T03:58:26.036903', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'saving'}
2026-03-21 03:58:26 | INFO | gensim.utils | not storing attribute cum_table
2026-03-21 03:58:26 | INFO | gensim.utils | saved /Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2016/word2vec.model
2026-03-21 03:58:26 | INFO | stil_semantic_change.word2vec.train | Trained Word2Vec for slice 2016 replicate 1 with 18244 words
2026-03-21 03:58:26 | INFO | gensim.models.word2vec | collecting all words and their counts
2026-03-21 03:58:26 | INFO | gensim.models.word2vec | PROGRESS: at sentence #0, processed 0 words, keeping 0 word types
2026-03-21 03:58:26 | INFO | gensim.models.word2vec | PROGRESS: at sentence #10000, processed 1262703 words, keeping 33861 word types
2026-03-21 03:58:27 | INFO | gensim.models.word2vec | PROGRESS: at sentence #20000, processed 2376836 words, keeping 45026 word types
2026-03-21 03:58:27 | INFO | gensim.models.word2vec | collected 49957 word types from a corpus of 3067001 raw words and 26414 sentences
2026-03-21 03:58:27 | INFO | gensim.models.word2vec | Creating a fresh vocabulary
2026-03-21 03:58:27 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'effective_min_count=5 retains 18039 unique words (36.11% of original 49957, drops 31918)', 'datetime': '2026-03-21T03:58:27.366435', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:58:27 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'effective_min_count=5 leaves 3014607 word corpus (98.29% of original 3067001, drops 52394)', 'datetime': '2026-03-21T03:58:27.366588', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:58:27 | INFO | gensim.models.word2vec | deleting the raw counts dictionary of 49957 items
2026-03-21 03:58:27 | INFO | gensim.models.word2vec | sample=0.001 downsamples 25 most-common words
2026-03-21 03:58:27 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'downsampling leaves estimated 2818587.1496930313 word corpus (93.5%% of prior 3014607)', 'datetime': '2026-03-21T03:58:27.401705', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:58:27 | INFO | gensim.models.word2vec | estimated required memory for 18039 words and 300 dimensions: 52313100 bytes
2026-03-21 03:58:27 | INFO | gensim.models.word2vec | resetting layer weights
2026-03-21 03:58:27 | INFO | gensim.utils | Word2Vec lifecycle event {'update': False, 'trim_rule': 'None', 'datetime': '2026-03-21T03:58:27.487654', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'build_vocab'}
2026-03-21 03:58:27 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training model with 6 workers on 18039 vocabulary and 300 features, using sg=1 hs=0 sample=0.001 negative=5 window=5 shrink_windows=True', 'datetime': '2026-03-21T03:58:27.487833', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 03:58:28 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 20.37% examples, 595883 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:29 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 40.64% examples, 622123 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:30 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 64.67% examples, 627652 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:58:31 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 89.73% examples, 631747 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:58:31 | INFO | gensim.models.word2vec | EPOCH 0: training on 3067001 raw words (2818880 effective words) took 4.4s, 637501 effective words/s
2026-03-21 03:58:32 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 20.05% examples, 604064 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:58:33 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 39.90% examples, 615801 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:34 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 63.88% examples, 625729 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:35 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 88.77% examples, 630486 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:36 | INFO | gensim.models.word2vec | EPOCH 1: training on 3067001 raw words (2818919 effective words) took 4.4s, 636610 effective words/s
2026-03-21 03:58:37 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 20.68% examples, 622232 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:38 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 41.39% examples, 639614 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:39 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 67.26% examples, 651281 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:40 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 91.88% examples, 651926 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:40 | INFO | gensim.models.word2vec | EPOCH 2: training on 3067001 raw words (2819062 effective words) took 4.3s, 654527 effective words/s
2026-03-21 03:58:41 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 20.68% examples, 619892 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:42 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 41.39% examples, 634269 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:43 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 67.64% examples, 644211 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:44 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 92.07% examples, 647912 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:58:44 | INFO | gensim.models.word2vec | EPOCH 3: training on 3067001 raw words (2819027 effective words) took 4.3s, 650623 effective words/s
2026-03-21 03:58:45 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 20.68% examples, 622882 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:46 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 41.72% examples, 640237 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:48 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 67.64% examples, 648742 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:58:49 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 91.88% examples, 648007 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:49 | INFO | gensim.models.word2vec | EPOCH 4: training on 3067001 raw words (2817960 effective words) took 4.3s, 652578 effective words/s
2026-03-21 03:58:49 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training on 15335005 raw words (14093848 effective words) took 21.8s, 646167 effective words/s', 'datetime': '2026-03-21T03:58:49.299554', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 03:58:49 | INFO | gensim.utils | Word2Vec lifecycle event {'params': 'Word2Vec<vocab=18039, vector_size=300, alpha=0.025>', 'datetime': '2026-03-21T03:58:49.299620', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'created'}
2026-03-21 03:58:49 | INFO | gensim.utils | Word2Vec lifecycle event {'fname_or_handle': '/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2017/word2vec.model', 'separately': 'None', 'sep_limit': 10485760, 'ignore': frozenset(), 'datetime': '2026-03-21T03:58:49.300548', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'saving'}
2026-03-21 03:58:49 | INFO | gensim.utils | not storing attribute cum_table
2026-03-21 03:58:49 | INFO | gensim.utils | saved /Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2017/word2vec.model
2026-03-21 03:58:50 | INFO | stil_semantic_change.word2vec.train | Trained Word2Vec for slice 2017 replicate 1 with 18039 words
2026-03-21 03:58:50 | INFO | gensim.models.word2vec | collecting all words and their counts
2026-03-21 03:58:50 | INFO | gensim.models.word2vec | PROGRESS: at sentence #0, processed 0 words, keeping 0 word types
2026-03-21 03:58:50 | INFO | gensim.models.word2vec | PROGRESS: at sentence #10000, processed 1177191 words, keeping 33277 word types
2026-03-21 03:58:50 | INFO | gensim.models.word2vec | collected 39747 word types from a corpus of 1779893 raw words and 15131 sentences
2026-03-21 03:58:50 | INFO | gensim.models.word2vec | Creating a fresh vocabulary
2026-03-21 03:58:50 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'effective_min_count=5 retains 14106 unique words (35.49% of original 39747, drops 25641)', 'datetime': '2026-03-21T03:58:50.366035', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:58:50 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'effective_min_count=5 leaves 1737602 word corpus (97.62% of original 1779893, drops 42291)', 'datetime': '2026-03-21T03:58:50.366193', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:58:50 | INFO | gensim.models.word2vec | deleting the raw counts dictionary of 39747 items
2026-03-21 03:58:50 | INFO | gensim.models.word2vec | sample=0.001 downsamples 30 most-common words
2026-03-21 03:58:50 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'downsampling leaves estimated 1633376.80292133 word corpus (94.0%% of prior 1737602)', 'datetime': '2026-03-21T03:58:50.391437', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:58:50 | INFO | gensim.models.word2vec | estimated required memory for 14106 words and 300 dimensions: 40907400 bytes
2026-03-21 03:58:50 | INFO | gensim.models.word2vec | resetting layer weights
2026-03-21 03:58:50 | INFO | gensim.utils | Word2Vec lifecycle event {'update': False, 'trim_rule': 'None', 'datetime': '2026-03-21T03:58:50.456155', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'build_vocab'}
2026-03-21 03:58:50 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training model with 6 workers on 14106 vocabulary and 300 features, using sg=1 hs=0 sample=0.001 negative=5 window=5 shrink_windows=True', 'datetime': '2026-03-21T03:58:50.456334', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 03:58:51 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 37.39% examples, 602343 words/s, in_qsize 10, out_qsize 1
2026-03-21 03:58:52 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 75.28% examples, 616443 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:53 | INFO | gensim.models.word2vec | EPOCH 0: training on 1779893 raw words (1633625 effective words) took 2.6s, 628970 effective words/s
2026-03-21 03:58:54 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 37.99% examples, 604457 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:55 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 77.93% examples, 646626 words/s, in_qsize 11, out_qsize 1
2026-03-21 03:58:55 | INFO | gensim.models.word2vec | EPOCH 1: training on 1779893 raw words (1633144 effective words) took 2.5s, 655883 effective words/s
2026-03-21 03:58:56 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 40.33% examples, 638681 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:57 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 77.93% examples, 646286 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:58:58 | INFO | gensim.models.word2vec | EPOCH 2: training on 1779893 raw words (1633421 effective words) took 2.5s, 661094 effective words/s
2026-03-21 03:58:59 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 41.08% examples, 641343 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:00 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 80.09% examples, 659747 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:00 | INFO | gensim.models.word2vec | EPOCH 3: training on 1779893 raw words (1633734 effective words) took 2.5s, 666245 effective words/s
2026-03-21 03:59:01 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 40.33% examples, 641421 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:02 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 78.53% examples, 654213 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:02 | INFO | gensim.models.word2vec | EPOCH 4: training on 1779893 raw words (1633295 effective words) took 2.5s, 661341 effective words/s
2026-03-21 03:59:02 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training on 8899465 raw words (8167219 effective words) took 12.5s, 654057 effective words/s', 'datetime': '2026-03-21T03:59:02.943522', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 03:59:02 | INFO | gensim.utils | Word2Vec lifecycle event {'params': 'Word2Vec<vocab=14106, vector_size=300, alpha=0.025>', 'datetime': '2026-03-21T03:59:02.943581', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'created'}
2026-03-21 03:59:02 | INFO | gensim.utils | Word2Vec lifecycle event {'fname_or_handle': '/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2018/word2vec.model', 'separately': 'None', 'sep_limit': 10485760, 'ignore': frozenset(), 'datetime': '2026-03-21T03:59:02.944646', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'saving'}
2026-03-21 03:59:02 | INFO | gensim.utils | not storing attribute cum_table
2026-03-21 03:59:02 | INFO | gensim.utils | saved /Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2018/word2vec.model
2026-03-21 03:59:03 | INFO | stil_semantic_change.word2vec.train | Trained Word2Vec for slice 2018 replicate 1 with 14106 words
2026-03-21 03:59:03 | INFO | gensim.models.word2vec | collecting all words and their counts
2026-03-21 03:59:03 | INFO | gensim.models.word2vec | PROGRESS: at sentence #0, processed 0 words, keeping 0 word types
2026-03-21 03:59:03 | INFO | gensim.models.word2vec | PROGRESS: at sentence #10000, processed 1150200 words, keeping 32312 word types
2026-03-21 03:59:03 | INFO | gensim.models.word2vec | collected 37290 word types from a corpus of 1626937 raw words and 14402 sentences
2026-03-21 03:59:03 | INFO | gensim.models.word2vec | Creating a fresh vocabulary
2026-03-21 03:59:03 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'effective_min_count=5 retains 13219 unique words (35.45% of original 37290, drops 24071)', 'datetime': '2026-03-21T03:59:03.809124', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:59:03 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'effective_min_count=5 leaves 1587046 word corpus (97.55% of original 1626937, drops 39891)', 'datetime': '2026-03-21T03:59:03.809213', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:59:03 | INFO | gensim.models.word2vec | deleting the raw counts dictionary of 37290 items
2026-03-21 03:59:03 | INFO | gensim.models.word2vec | sample=0.001 downsamples 31 most-common words
2026-03-21 03:59:03 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'downsampling leaves estimated 1493703.8417424448 word corpus (94.1%% of prior 1587046)', 'datetime': '2026-03-21T03:59:03.832638', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:59:03 | INFO | gensim.models.word2vec | estimated required memory for 13219 words and 300 dimensions: 38335100 bytes
2026-03-21 03:59:03 | INFO | gensim.models.word2vec | resetting layer weights
2026-03-21 03:59:03 | INFO | gensim.utils | Word2Vec lifecycle event {'update': False, 'trim_rule': 'None', 'datetime': '2026-03-21T03:59:03.893976', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'build_vocab'}
2026-03-21 03:59:03 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training model with 6 workers on 13219 vocabulary and 300 features, using sg=1 hs=0 sample=0.001 negative=5 window=5 shrink_windows=True', 'datetime': '2026-03-21T03:59:03.894141', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 03:59:04 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 39.81% examples, 620179 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:05 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 85.47% examples, 635954 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:06 | INFO | gensim.models.word2vec | EPOCH 0: training on 1626937 raw words (1493856 effective words) took 2.3s, 648707 effective words/s
2026-03-21 03:59:07 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 39.81% examples, 621987 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:08 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 85.47% examples, 639651 words/s, in_qsize 11, out_qsize 1
2026-03-21 03:59:08 | INFO | gensim.models.word2vec | EPOCH 1: training on 1626937 raw words (1493519 effective words) took 2.3s, 648768 effective words/s
2026-03-21 03:59:09 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 40.42% examples, 619272 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:59:10 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 88.45% examples, 656548 words/s, in_qsize 10, out_qsize 0
2026-03-21 03:59:10 | INFO | gensim.models.word2vec | EPOCH 2: training on 1626937 raw words (1493712 effective words) took 2.3s, 661182 effective words/s
2026-03-21 03:59:11 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 39.81% examples, 620979 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:59:12 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 85.47% examples, 639000 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:13 | INFO | gensim.models.word2vec | EPOCH 3: training on 1626937 raw words (1494047 effective words) took 2.3s, 648876 effective words/s
2026-03-21 03:59:14 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 40.42% examples, 628600 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:15 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 86.72% examples, 645780 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:15 | INFO | gensim.models.word2vec | EPOCH 4: training on 1626937 raw words (1493393 effective words) took 2.3s, 651214 effective words/s
2026-03-21 03:59:15 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training on 8134685 raw words (7468527 effective words) took 11.5s, 651480 effective words/s', 'datetime': '2026-03-21T03:59:15.358235', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 03:59:15 | INFO | gensim.utils | Word2Vec lifecycle event {'params': 'Word2Vec<vocab=13219, vector_size=300, alpha=0.025>', 'datetime': '2026-03-21T03:59:15.358298', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'created'}
2026-03-21 03:59:15 | INFO | gensim.utils | Word2Vec lifecycle event {'fname_or_handle': '/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2019/word2vec.model', 'separately': 'None', 'sep_limit': 10485760, 'ignore': frozenset(), 'datetime': '2026-03-21T03:59:15.359539', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'saving'}
2026-03-21 03:59:15 | INFO | gensim.utils | not storing attribute cum_table
2026-03-21 03:59:15 | INFO | gensim.utils | saved /Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2019/word2vec.model
2026-03-21 03:59:15 | INFO | stil_semantic_change.word2vec.train | Trained Word2Vec for slice 2019 replicate 1 with 13219 words
2026-03-21 03:59:15 | INFO | gensim.models.word2vec | collecting all words and their counts
2026-03-21 03:59:15 | INFO | gensim.models.word2vec | PROGRESS: at sentence #0, processed 0 words, keeping 0 word types
2026-03-21 03:59:16 | INFO | gensim.models.word2vec | PROGRESS: at sentence #10000, processed 1013496 words, keeping 27106 word types
2026-03-21 03:59:16 | INFO | gensim.models.word2vec | collected 31096 word types from a corpus of 1427931 raw words and 14397 sentences
2026-03-21 03:59:16 | INFO | gensim.models.word2vec | Creating a fresh vocabulary
2026-03-21 03:59:16 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'effective_min_count=5 retains 11286 unique words (36.29% of original 31096, drops 19810)', 'datetime': '2026-03-21T03:59:16.161855', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:59:16 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'effective_min_count=5 leaves 1394977 word corpus (97.69% of original 1427931, drops 32954)', 'datetime': '2026-03-21T03:59:16.163941', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:59:16 | INFO | gensim.models.word2vec | deleting the raw counts dictionary of 31096 items
2026-03-21 03:59:16 | INFO | gensim.models.word2vec | sample=0.001 downsamples 40 most-common words
2026-03-21 03:59:16 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'downsampling leaves estimated 1286129.4757752568 word corpus (92.2%% of prior 1394977)', 'datetime': '2026-03-21T03:59:16.185218', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:59:16 | INFO | gensim.models.word2vec | estimated required memory for 11286 words and 300 dimensions: 32729400 bytes
2026-03-21 03:59:16 | INFO | gensim.models.word2vec | resetting layer weights
2026-03-21 03:59:16 | INFO | gensim.utils | Word2Vec lifecycle event {'update': False, 'trim_rule': 'None', 'datetime': '2026-03-21T03:59:16.239721', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'build_vocab'}
2026-03-21 03:59:16 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training model with 6 workers on 11286 vocabulary and 300 features, using sg=1 hs=0 sample=0.001 negative=5 window=5 shrink_windows=True', 'datetime': '2026-03-21T03:59:16.239868', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 03:59:17 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 46.80% examples, 628042 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:18 | INFO | gensim.models.word2vec | EPOCH 0: training on 1427931 raw words (1285668 effective words) took 2.0s, 650986 effective words/s
2026-03-21 03:59:19 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 46.80% examples, 632657 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:20 | INFO | gensim.models.word2vec | EPOCH 1: training on 1427931 raw words (1285901 effective words) took 2.0s, 653029 effective words/s
2026-03-21 03:59:21 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 47.56% examples, 647694 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:22 | INFO | gensim.models.word2vec | EPOCH 2: training on 1427931 raw words (1285933 effective words) took 1.9s, 670425 effective words/s
2026-03-21 03:59:23 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 48.40% examples, 651104 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:24 | INFO | gensim.models.word2vec | EPOCH 3: training on 1427931 raw words (1286178 effective words) took 1.9s, 666979 effective words/s
2026-03-21 03:59:25 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 46.80% examples, 625755 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:26 | INFO | gensim.models.word2vec | EPOCH 4: training on 1427931 raw words (1286073 effective words) took 2.0s, 648289 effective words/s
2026-03-21 03:59:26 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training on 7139655 raw words (6429753 effective words) took 9.8s, 657536 effective words/s', 'datetime': '2026-03-21T03:59:26.018566', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 03:59:26 | INFO | gensim.utils | Word2Vec lifecycle event {'params': 'Word2Vec<vocab=11286, vector_size=300, alpha=0.025>', 'datetime': '2026-03-21T03:59:26.018622', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'created'}
2026-03-21 03:59:26 | INFO | gensim.utils | Word2Vec lifecycle event {'fname_or_handle': '/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2020/word2vec.model', 'separately': 'None', 'sep_limit': 10485760, 'ignore': frozenset(), 'datetime': '2026-03-21T03:59:26.019358', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'saving'}
2026-03-21 03:59:26 | INFO | gensim.utils | not storing attribute cum_table
2026-03-21 03:59:26 | INFO | gensim.utils | saved /Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2020/word2vec.model
2026-03-21 03:59:26 | INFO | stil_semantic_change.word2vec.train | Trained Word2Vec for slice 2020 replicate 1 with 11286 words
2026-03-21 03:59:26 | INFO | gensim.models.word2vec | collecting all words and their counts
2026-03-21 03:59:26 | INFO | gensim.models.word2vec | PROGRESS: at sentence #0, processed 0 words, keeping 0 word types
2026-03-21 03:59:26 | INFO | gensim.models.word2vec | PROGRESS: at sentence #10000, processed 968696 words, keeping 26405 word types
2026-03-21 03:59:26 | INFO | gensim.models.word2vec | PROGRESS: at sentence #20000, processed 2008573 words, keeping 36700 word types
2026-03-21 03:59:26 | INFO | gensim.models.word2vec | collected 37279 word types from a corpus of 2083724 raw words and 20715 sentences
2026-03-21 03:59:26 | INFO | gensim.models.word2vec | Creating a fresh vocabulary
2026-03-21 03:59:26 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'effective_min_count=5 retains 13882 unique words (37.24% of original 37279, drops 23397)', 'datetime': '2026-03-21T03:59:26.879469', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:59:26 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'effective_min_count=5 leaves 2045090 word corpus (98.15% of original 2083724, drops 38634)', 'datetime': '2026-03-21T03:59:26.879611', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:59:26 | INFO | gensim.models.word2vec | deleting the raw counts dictionary of 37279 items
2026-03-21 03:59:26 | INFO | gensim.models.word2vec | sample=0.001 downsamples 36 most-common words
2026-03-21 03:59:26 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'downsampling leaves estimated 1905108.5361227742 word corpus (93.2%% of prior 2045090)', 'datetime': '2026-03-21T03:59:26.905839', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:59:26 | INFO | gensim.models.word2vec | estimated required memory for 13882 words and 300 dimensions: 40257800 bytes
2026-03-21 03:59:26 | INFO | gensim.models.word2vec | resetting layer weights
2026-03-21 03:59:26 | INFO | gensim.utils | Word2Vec lifecycle event {'update': False, 'trim_rule': 'None', 'datetime': '2026-03-21T03:59:26.967463', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'build_vocab'}
2026-03-21 03:59:26 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training model with 6 workers on 13882 vocabulary and 300 features, using sg=1 hs=0 sample=0.001 negative=5 window=5 shrink_windows=True', 'datetime': '2026-03-21T03:59:26.967676', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 03:59:27 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 32.31% examples, 592950 words/s, in_qsize 11, out_qsize 1
2026-03-21 03:59:28 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 67.57% examples, 618931 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:29 | INFO | gensim.models.word2vec | EPOCH 0: training on 2083724 raw words (1905380 effective words) took 3.0s, 633241 effective words/s
2026-03-21 03:59:30 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 33.81% examples, 614275 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:59:32 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 69.75% examples, 635035 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:32 | INFO | gensim.models.word2vec | EPOCH 1: training on 2083724 raw words (1904999 effective words) took 2.9s, 646014 effective words/s
2026-03-21 03:59:33 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 33.86% examples, 617567 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:34 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 70.26% examples, 647123 words/s, in_qsize 12, out_qsize 0
2026-03-21 03:59:35 | INFO | gensim.models.word2vec | EPOCH 2: training on 2083724 raw words (1904923 effective words) took 2.9s, 652174 effective words/s
2026-03-21 03:59:36 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 34.30% examples, 622492 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:37 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 70.23% examples, 639618 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:38 | INFO | gensim.models.word2vec | EPOCH 3: training on 2083724 raw words (1904979 effective words) took 2.9s, 652647 effective words/s
2026-03-21 03:59:39 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 33.81% examples, 607999 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:40 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 70.26% examples, 639545 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:41 | INFO | gensim.models.word2vec | EPOCH 4: training on 2083724 raw words (1904805 effective words) took 2.9s, 655735 effective words/s
2026-03-21 03:59:41 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training on 10418620 raw words (9525086 effective words) took 14.7s, 647689 effective words/s', 'datetime': '2026-03-21T03:59:41.674220', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 03:59:41 | INFO | gensim.utils | Word2Vec lifecycle event {'params': 'Word2Vec<vocab=13882, vector_size=300, alpha=0.025>', 'datetime': '2026-03-21T03:59:41.674282', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'created'}
2026-03-21 03:59:41 | INFO | gensim.utils | Word2Vec lifecycle event {'fname_or_handle': '/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2021/word2vec.model', 'separately': 'None', 'sep_limit': 10485760, 'ignore': frozenset(), 'datetime': '2026-03-21T03:59:41.675099', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'saving'}
2026-03-21 03:59:41 | INFO | gensim.utils | not storing attribute cum_table
2026-03-21 03:59:41 | INFO | gensim.utils | saved /Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2021/word2vec.model
2026-03-21 03:59:42 | INFO | stil_semantic_change.word2vec.train | Trained Word2Vec for slice 2021 replicate 1 with 13882 words
2026-03-21 03:59:42 | INFO | gensim.models.word2vec | collecting all words and their counts
2026-03-21 03:59:42 | INFO | gensim.models.word2vec | PROGRESS: at sentence #0, processed 0 words, keeping 0 word types
2026-03-21 03:59:42 | INFO | gensim.models.word2vec | PROGRESS: at sentence #10000, processed 1032373 words, keeping 28503 word types
2026-03-21 03:59:42 | INFO | gensim.models.word2vec | collected 33169 word types from a corpus of 1454684 raw words and 13611 sentences
2026-03-21 03:59:42 | INFO | gensim.models.word2vec | Creating a fresh vocabulary
2026-03-21 03:59:42 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'effective_min_count=5 retains 12094 unique words (36.46% of original 33169, drops 21075)', 'datetime': '2026-03-21T03:59:42.497403', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:59:42 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'effective_min_count=5 leaves 1419845 word corpus (97.61% of original 1454684, drops 34839)', 'datetime': '2026-03-21T03:59:42.497543', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:59:42 | INFO | gensim.models.word2vec | deleting the raw counts dictionary of 33169 items
2026-03-21 03:59:42 | INFO | gensim.models.word2vec | sample=0.001 downsamples 34 most-common words
2026-03-21 03:59:42 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'downsampling leaves estimated 1330136.2696726313 word corpus (93.7%% of prior 1419845)', 'datetime': '2026-03-21T03:59:42.521155', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:59:42 | INFO | gensim.models.word2vec | estimated required memory for 12094 words and 300 dimensions: 35072600 bytes
2026-03-21 03:59:42 | INFO | gensim.models.word2vec | resetting layer weights
2026-03-21 03:59:42 | INFO | gensim.utils | Word2Vec lifecycle event {'update': False, 'trim_rule': 'None', 'datetime': '2026-03-21T03:59:42.578809', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'build_vocab'}
2026-03-21 03:59:42 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training model with 6 workers on 12094 vocabulary and 300 features, using sg=1 hs=0 sample=0.001 negative=5 window=5 shrink_windows=True', 'datetime': '2026-03-21T03:59:42.578936', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 03:59:43 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 48.15% examples, 615818 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:44 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 96.50% examples, 636403 words/s, in_qsize 5, out_qsize 2
2026-03-21 03:59:44 | INFO | gensim.models.word2vec | EPOCH 0: training on 1454684 raw words (1329896 effective words) took 2.1s, 644306 effective words/s
2026-03-21 03:59:45 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 48.17% examples, 604498 words/s, in_qsize 10, out_qsize 1
2026-03-21 03:59:46 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 98.30% examples, 643203 words/s, in_qsize 3, out_qsize 1
2026-03-21 03:59:46 | INFO | gensim.models.word2vec | EPOCH 1: training on 1454684 raw words (1330160 effective words) took 2.1s, 640182 effective words/s
2026-03-21 03:59:47 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 49.57% examples, 610042 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:48 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 99.01% examples, 637677 words/s, in_qsize 2, out_qsize 1
2026-03-21 03:59:48 | INFO | gensim.models.word2vec | EPOCH 2: training on 1454684 raw words (1329792 effective words) took 2.1s, 638837 effective words/s
2026-03-21 03:59:49 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 49.67% examples, 622773 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:50 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 97.73% examples, 639438 words/s, in_qsize 4, out_qsize 1
2026-03-21 03:59:50 | INFO | gensim.models.word2vec | EPOCH 3: training on 1454684 raw words (1329980 effective words) took 2.1s, 644435 effective words/s
2026-03-21 03:59:51 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 48.86% examples, 620905 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:52 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 97.73% examples, 643636 words/s, in_qsize 4, out_qsize 1
2026-03-21 03:59:52 | INFO | gensim.models.word2vec | EPOCH 4: training on 1454684 raw words (1329968 effective words) took 2.0s, 649196 effective words/s
2026-03-21 03:59:52 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training on 7273420 raw words (6649796 effective words) took 10.3s, 643139 effective words/s', 'datetime': '2026-03-21T03:59:52.918676', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 03:59:52 | INFO | gensim.utils | Word2Vec lifecycle event {'params': 'Word2Vec<vocab=12094, vector_size=300, alpha=0.025>', 'datetime': '2026-03-21T03:59:52.918736', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'created'}
2026-03-21 03:59:52 | INFO | gensim.utils | Word2Vec lifecycle event {'fname_or_handle': '/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2022/word2vec.model', 'separately': 'None', 'sep_limit': 10485760, 'ignore': frozenset(), 'datetime': '2026-03-21T03:59:52.919640', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'saving'}
2026-03-21 03:59:52 | INFO | gensim.utils | not storing attribute cum_table
2026-03-21 03:59:52 | INFO | gensim.utils | saved /Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2022/word2vec.model
2026-03-21 03:59:53 | INFO | stil_semantic_change.word2vec.train | Trained Word2Vec for slice 2022 replicate 1 with 12094 words
2026-03-21 03:59:53 | INFO | gensim.models.word2vec | collecting all words and their counts
2026-03-21 03:59:53 | INFO | gensim.models.word2vec | PROGRESS: at sentence #0, processed 0 words, keeping 0 word types
2026-03-21 03:59:53 | INFO | gensim.models.word2vec | PROGRESS: at sentence #10000, processed 1135529 words, keeping 30862 word types
2026-03-21 03:59:53 | INFO | gensim.models.word2vec | collected 36737 word types from a corpus of 1747796 raw words and 15700 sentences
2026-03-21 03:59:53 | INFO | gensim.models.word2vec | Creating a fresh vocabulary
2026-03-21 03:59:53 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'effective_min_count=5 retains 13552 unique words (36.89% of original 36737, drops 23185)', 'datetime': '2026-03-21T03:59:53.742827', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:59:53 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'effective_min_count=5 leaves 1709182 word corpus (97.79% of original 1747796, drops 38614)', 'datetime': '2026-03-21T03:59:53.742944', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:59:53 | INFO | gensim.models.word2vec | deleting the raw counts dictionary of 36737 items
2026-03-21 03:59:53 | INFO | gensim.models.word2vec | sample=0.001 downsamples 30 most-common words
2026-03-21 03:59:53 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'downsampling leaves estimated 1598809.063491883 word corpus (93.5%% of prior 1709182)', 'datetime': '2026-03-21T03:59:53.771743', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'prepare_vocab'}
2026-03-21 03:59:53 | INFO | gensim.models.word2vec | estimated required memory for 13552 words and 300 dimensions: 39300800 bytes
2026-03-21 03:59:53 | INFO | gensim.models.word2vec | resetting layer weights
2026-03-21 03:59:53 | INFO | gensim.utils | Word2Vec lifecycle event {'update': False, 'trim_rule': 'None', 'datetime': '2026-03-21T03:59:53.830566', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'build_vocab'}
2026-03-21 03:59:53 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training model with 6 workers on 13552 vocabulary and 300 features, using sg=1 hs=0 sample=0.001 negative=5 window=5 shrink_windows=True', 'datetime': '2026-03-21T03:59:53.830730', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 03:59:54 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 37.57% examples, 615224 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:55 | INFO | gensim.models.word2vec | EPOCH 0 - PROGRESS: at 80.31% examples, 633082 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:56 | INFO | gensim.models.word2vec | EPOCH 0: training on 1747796 raw words (1599197 effective words) took 2.5s, 648954 effective words/s
2026-03-21 03:59:57 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 37.01% examples, 603729 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:58 | INFO | gensim.models.word2vec | EPOCH 1 - PROGRESS: at 79.17% examples, 624858 words/s, in_qsize 11, out_qsize 0
2026-03-21 03:59:58 | INFO | gensim.models.word2vec | EPOCH 1: training on 1747796 raw words (1598535 effective words) took 2.5s, 635960 effective words/s
2026-03-21 03:59:59 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 37.57% examples, 619559 words/s, in_qsize 11, out_qsize 0
2026-03-21 04:00:00 | INFO | gensim.models.word2vec | EPOCH 2 - PROGRESS: at 80.31% examples, 635428 words/s, in_qsize 11, out_qsize 0
2026-03-21 04:00:01 | INFO | gensim.models.word2vec | EPOCH 2: training on 1747796 raw words (1598477 effective words) took 2.4s, 653066 effective words/s
2026-03-21 04:00:02 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 38.08% examples, 633106 words/s, in_qsize 12, out_qsize 0
2026-03-21 04:00:03 | INFO | gensim.models.word2vec | EPOCH 3 - PROGRESS: at 79.80% examples, 643209 words/s, in_qsize 11, out_qsize 0
2026-03-21 04:00:03 | INFO | gensim.models.word2vec | EPOCH 3: training on 1747796 raw words (1599105 effective words) took 2.5s, 647216 effective words/s
2026-03-21 04:00:04 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 37.57% examples, 606398 words/s, in_qsize 11, out_qsize 2
2026-03-21 04:00:05 | INFO | gensim.models.word2vec | EPOCH 4 - PROGRESS: at 80.89% examples, 640010 words/s, in_qsize 11, out_qsize 0
2026-03-21 04:00:06 | INFO | gensim.models.word2vec | EPOCH 4: training on 1747796 raw words (1598822 effective words) took 2.5s, 648007 effective words/s
2026-03-21 04:00:06 | INFO | gensim.utils | Word2Vec lifecycle event {'msg': 'training on 8738980 raw words (7994136 effective words) took 12.4s, 646384 effective words/s', 'datetime': '2026-03-21T04:00:06.198361', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'train'}
2026-03-21 04:00:06 | INFO | gensim.utils | Word2Vec lifecycle event {'params': 'Word2Vec<vocab=13552, vector_size=300, alpha=0.025>', 'datetime': '2026-03-21T04:00:06.198422', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'created'}
2026-03-21 04:00:06 | INFO | gensim.utils | Word2Vec lifecycle event {'fname_or_handle': '/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2023/word2vec.model', 'separately': 'None', 'sep_limit': 10485760, 'ignore': frozenset(), 'datetime': '2026-03-21T04:00:06.199122', 'gensim': '4.4.0', 'python': '3.12.12 | packaged by conda-forge | (main, Oct 22 2025, 23:34:53) [Clang 19.1.7 ]', 'platform': 'macOS-15.7.4-arm64-arm-64bit', 'event': 'saving'}
2026-03-21 04:00:06 | INFO | gensim.utils | not storing attribute cum_table
2026-03-21 04:00:06 | INFO | gensim.utils | saved /Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/models/replicate_1/2023/word2vec.model
2026-03-21 04:00:06 | INFO | stil_semantic_change.word2vec.train | Trained Word2Vec for slice 2023 replicate 1 with 13552 words
```

**Outcome (Codex)**

Yes, it finished.

What happened:
- The last noisy log line you saw was still inside `train_word2vec`.
- The process is no longer running.
- All downstream stage manifests exist: training, alignment, scoring, and reporting.

Exact completion times for this run on **March 21, 2026**:
- `train_word2vec` finished at **04:00:06 BRT**
- `align_embeddings` finished at **04:00:44 BRT**
- `score_candidates` finished at **04:05:51 BRT**
- `report_candidates` finished at **04:05:55 BRT**

So the full pipeline completed at **04:05:55 BRT on March 21, 2026**.

Why it looked stuck:
- the log got very verbose during Word2Vec
- the later stages are much quieter, so after the last training lines there wasn’t much new to show

Main output folder:
[2cf8a857028c](\/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c)

Quick summary file:
[analysis_summary.md](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c/reports/analysis_summary.md)

It produced:
- 24 slices
- 428,366 documents
- 63,071,705 cleaned tokens
- 3,225 eligible lemmas scored

If you want, I can now do the post-run audit: check artifact integrity, flag anything suspicious in the top candidates, and freeze this as the clean Word2Vec baseline.

---

### Turn 13 (2026-03-21T08:48:42.876Z)

**User**

```
yes go ahead
```

**Outcome (Codex)**

The baseline is now audited and frozen in [clean_word2vec_baseline_audit_2026_03_21.md](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/clean_word2vec_baseline_audit_2026_03_21.md). I also committed that note as `c81b0b1` with `docs(baseline): freeze clean word2vec audit`.

Bottom line: this run is clean mechanically and complete as a Word2Vec baseline. It finished at **2026-03-21 04:05:55 BRT**, all stage manifests are present, and the full artifact package exists under [/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/2cf8a857028c).

The main caveat is semantic quality, not pipeline integrity. The top drift list is dominated by rhetorical/procedural items like `dir`, `dito`, `repito`, `digo`, and malformed lemmas like `digar`; neighbor lists also show artifacts like `repitar` and `começarer`. I also confirmed a small accounting edge case: 5 “eligible” lemmas were never scored because they contain spaces, like `tratar se` and `tornar se`, so they survive lemma stats but do not behave like single Word2Vec tokens.

So the right interpretation is: keep this as the clean Word2Vec baseline for the comparative paper, but add lexical cleanup before treating the top-ranked drift items as substantive political concepts. The next concrete fix should be excluding multi-token lemmas and adding a lightweight cleanup/filter layer before we build the TF-IDF and BERT comparison panel.

---

### Turn 14 (2026-03-21T17:21:45.802Z)

**User**

```
Ok should we implement fixes then run again? please analyze code and fix all these errors


[$python-code-style](/Users/victor/.agents/skills/python-code-style/SKILL.md) [$python-performance-optimization](/Users/victor/.agents/skills/python-performance-optimization/SKILL.md)
```

**Outcome (Codex)**

I implemented the fixes and reran the validation loop before restarting the baseline.

What changed:
- fixed the concrete malformed lemma cases we saw in the audit, including `digar`/`repitar`-style errors and pronominal spacing like `tratar se`
- added a generic repair for the `estarer` / `deverer` / `votarer` family using surface-form inference
- added a safer fallback so unresolved malformed infinitives fall back to the surface token instead of staying as garbage lemmas
- hard-excluded whitespace lemmas at scoring time so we can’t get the old eligibility/scoring mismatch again
- kept the lexical exclusion list for obvious procedural noise in the baseline comparison path

Validation:
- `ruff check` passed
- focused regression suites passed, including the new preprocessing and selection tests
- the new run’s first token shard has `0` whitespace lemmas
- the specific old bad forms I spot-checked are gone from `batch_0001`

New commits:
- `375c359` `fix(preprocess): repair lemma normalization artifacts`
- `ea0d88f` `fix(preprocess): suppress residual malformed infinitives`

The fresh baseline run is active here:
[run_yearly_core.log](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/1c11279e1f2d/logs/run_yearly_core.log)

Use this to watch it:

```bash
tail -n 50 -f /Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/1c11279e1f2d/logs/run_yearly_core.log
```

If you want a second terminal check too, this is the experiment root:
`/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/1c11279e1f2d`

When it finishes, tell me and I’ll do the same full post-run audit against the cleaned baseline.

---

### Turn 15 (2026-03-21T17:37:26.976Z)

**User**

```
Make sure we save different version of the processed text, because we might want to use different stages of it for different uses. Make sure its all well organied and structured in project folders

[$architecture-design](/Users/victor/.codex/skills/architecture-design/SKILL.md)
```

**Outcome (Codex)**

I implemented the artifact-structure change and restarted the baseline so it writes the new layout from batch 1 onward.

What changed:
- the prep stage now stores separate representations instead of one overloaded `clean_text`
- raw documents, metadata, retained tokens, and processed text views are split into named folders
- Word2Vec now explicitly trains from `model.text_view=content_lemma`
- BERT and qualitative readers were updated to use the new prepared paths
- I documented the layout in [prepared_artifact_layout_2026_03_21.md](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/prepared_artifact_layout_2026_03_21.md)

New prepared structure under the active run:
- `prepared/docs/metadata/`
- `prepared/docs/raw_text/`
- `prepared/tokens/content/`
- `prepared/text_views/by_doc/`
- `prepared/text_views/by_slice/normalized_surface/`
- `prepared/text_views/by_slice/content_surface/`
- `prepared/text_views/by_slice/content_lemma/`

I verified the first batch on disk:
- all new directories exist
- `by_doc` shards contain `normalized_surface_text`, `content_surface_text`, and `content_lemma_text`
- `tokens/content` now keeps `pos` too
- all three text views are populated for the first 1000 docs

Validation:
- `ruff check` passed
- `13 passed in 41.03s`

Commits:
- `7038660` `refactor(prepared): organize multiple text views`

The new run is active here:
[run_yearly_core.log](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/logs/run_yearly_core.log)

Use this to watch it:

```bash
tail -n 50 -f /Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/logs/run_yearly_core.log
```

When it finishes, I’ll audit both the lexical cleanup and the new prepared-artifact package together.

---

### Turn 16 (2026-03-21T17:52:34.911Z)

**User**

```
is it possible for u to check preliminary results so that we wont know just when its finished that its wrong?
```

**Outcome (Codex)**

Yes. We can catch a lot before the full run finishes.

As of **March 21, 2026, 14:53 BRT**, the run is still in `prepare_corpus`, so we do not have drift rankings yet. But the early preprocessing checks look good:

- `11,884` docs prepared so far
- only slices `2000` and `2001` have appeared yet, which is expected at this stage
- `2,313,785` retained token rows so far
- `0` whitespace lemmas
- none of the old bad forms I checked are present:
  - `digar`
  - `repitar`
  - `estarer`
  - `deverer`
  - `votarer`
  - `verer`
  - `tratar se`
  - `fazer ele`
  - `de esse`
  - `parecr ee`
  - `transformour se`

The one pattern that still shows up in the crude `*arer/*erer/*irer` suffix scan is mostly legitimate lemmas:
- `querer`
- `requerer`
- `bem-querer`

So the early signal is that the preprocessing fixes are holding.

The new structured text views are also being written correctly:
- `prepared/docs/metadata/`
- `prepared/docs/raw_text/`
- `prepared/tokens/content/`
- `prepared/text_views/by_doc/`
- `prepared/text_views/by_slice/normalized_surface/`
- `prepared/text_views/by_slice/content_surface/`
- `prepared/text_views/by_slice/content_lemma/`

And the first prepared docs are populated in all 3 views:
- `normalized_surface_text`
- `content_surface_text`
- `content_lemma_text`

What we still cannot know yet:
- whether Word2Vec top drift terms are now substantively better
- whether rhetorical markers still dominate rankings after scoring
- whether neighbors look cleaner after alignment

The right checkpoints are:
1. during `prepare_corpus`: preprocessing quality and artifact structure
2. after the first few Word2Vec slice models: vocab sanity and nearest neighbors
3. after `score_candidates`: top drift list quality

If you want, I can check again as soon as the first trained models appear, which is the first point where we can inspect actual semantic outputs instead of just prep quality.

---

### Turn 17 (2026-03-21T18:09:25.247Z)

**User**

```
Ok, one new thing is that we maybe might not use this dataset(we will still run it all, because we might do this new dataset seperate).  I got a new dataset that might be easier to validate pegar it has votes of parlament. in rawdataset folder analyze PTPARL-V, and analyze [ptparl_v_vote_label_note.md](Articles/N2/docs/ptparl_v_vote_label_note.md) and see what you think of it
```

**Outcome (Codex)**

I think `PTPARL-V` is promising, but I would not treat it as a simple “better replacement” for `BrPoliCorpus`.

The good news is real. The local files match your note: [ptparl_v_vote_label_note.md](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/ptparl_v_vote_label_note.md), [inventory_overview.md](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/RawDatasets/PTPARL-V/inventory/inventory_overview.md), and the exported tables under [/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/RawDatasets/PTPARL-V/exports/V0-1/csv](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/RawDatasets/PTPARL-V/exports/V0-1/csv) are there. It does give you something `BrPoliCorpus` does not: an external political signal tied to interventions. For the processed export, I found `10,068` total rows, `1995–2022` nominal coverage, and a usable text subset of about `5,713` rows with `text_process_label == 1` and non-null text. The vote labels are reasonably populated and not absurdly imbalanced: about `52.6%` in favour, `31.0%` against, `16.5%` abstention in the usable subset.

The caution is stronger than the current note suggests. Your note is directionally right that the labels should not be oversold as semantic ground truth, and the source code in [init_corpus_meta.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/RawDatasets/PTPARL-V/pt_parliamentary_minutes/init_corpus_meta.py) does support a party-list matching story. But the exported data is messier than a pure party-aligned label. I found:
- `ini_leg + ini_num` is not unique enough; you need at least `ini_leg + ini_num + ini_type`.
- even with that stricter key, there are still many repeated deputy/initiative rows.
- more importantly, there are conflicting vote labels for the same deputy within the same initiative key.
So I would revise the note from “best treated as party-aligned vote label” to “best treated as a noisy derived political-position label that requires deduplication/aggregation rules before validation use.”

My recommendation is:
- Keep `BrPoliCorpus` as the main broad exploratory corpus.
- Treat `PTPARL-V` as a separate validation-oriented corpus, not a drop-in replacement.
- Use it only after building a clean evaluation table with one explicit unit of analysis.
A good safe unit would be:
- initiative-party aggregated label, dropping conflicted cases
- or initiative-deputy majority label, dropping conflicted cases
- and only on rows with `text_process_label == 1`

So yes, I think it can substantially strengthen the paper, but only if we present it as “noisy external political supervision” and clean the supervision layer first. If you want, next I can write a short evaluation plan for `PTPARL-V` and define the exact dedup/aggregation rules before we integrate it into N2.

---

### Turn 18 (2026-03-21T18:14:47.788Z)

**User**

```
Ok,  we will follow ur recommendation, in that docs, write that
```

**Outcome (Codex)**

I updated [ptparl_v_vote_label_note.md](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/ptparl_v_vote_label_note.md) with the stronger recommendation and the new caveats from the local inspection.

The doc now says, in substance:
- `PTPARL-V` is useful, but should be treated as a noisy derived political supervision layer
- it is not a clean deputy-level ground truth
- it should not replace `BrPoliCorpus` as the main exploratory corpus
- it should be used as a secondary validation-oriented corpus after deduplication/aggregation
- the safest next step is a cleaned evaluation table such as initiative-party or initiative-deputy aggregated labels with conflicted cases dropped

If you want, next I can turn that into a concrete `PTPARL-V` integration plan doc with the exact cleaning rules and evaluation protocol.

---

### Turn 19 (2026-03-21T18:35:12.860Z)

**User**

```
I’m adding a short section to the PTPARL-V note about the initiative-key ambiguity and the safe key to use, keeping the rest of the file intact.
```

**Outcome (Codex)**

I updated [ptparl_v_vote_label_note.md](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/ptparl_v_vote_label_note.md) with the initiative-key ambiguity section and corrected the safe key to:

- `ini_leg + ini_num + ini_type`

with `ini_session`, `ini_title`, and `pub_date` kept as useful secondary checks.

I also committed it:
- `704d63f` `docs(ptparl): clarify safe initiative key`

One important detail from the local inspection: `ini_session` helps, but `ini_type` is the stronger disambiguator in this export.

---

### Turn 20 (2026-03-21T18:40:04.414Z)

**User**

```
how long till current one finishes that we started?
```

**Outcome (Codex)**

As of **March 21, 2026, 15:39 BRT**, it’s still in `prepare_corpus`.

Current progress:
- prepared batches: `88`
- recent prep speed: about **37.6 seconds per batch**
- this run previously had about **490 prep batches** total, so a reasonable estimate is:
  - **~402 prep batches left**
  - **~4.2 hours left for prep**

After prep, we still need:
- Word2Vec training
- alignment
- scoring
- reports

Based on the earlier clean baseline on this same pipeline family, those later stages should be much shorter than prep, roughly **20 to 35 minutes total**.

Best estimate right now:
- **~4.5 to 5 hours left**
- likely finish around **March 21, 2026, 20:05 to 20:40 BRT**

Why I trust this estimate more now:
- it’s based on the actual live run speed, not a guess
- the current run is behaving steadily
- early artifact checks look good, so there’s no sign yet that we’ll lose time to a restart

If you want, I can check again once prep gets near the end or as soon as the first Word2Vec models start, and then I can tighten the ETA further.

---

### Turn 21 (2026-03-21T18:52:52.915Z)

**User**

```
Is there any other things in N2 codebase that we could be cleaning,organizing, fixing project strucutre, improving, etc... that we could do while waiting for this to finish?


[$architecture-design](/Users/victor/.codex/skills/architecture-design/SKILL.md) [$uv-package-manager](/Users/victor/.codex/skills/uv-package-manager/SKILL.md) [$codebase-search](/Users/victor/.agents/skills/codebase-search/SKILL.md) [$code-review-excellence](/Users/victor/.agents/skills/code-review-excellence/SKILL.md) [$python-code-style](/Users/victor/.agents/skills/python-code-style/SKILL.md) [$python-performance-optimization](/Users/victor/.agents/skills/python-performance-optimization/SKILL.md)
```

**Outcome (Codex)**

**Findings**
- High: optional BERT dependencies are imported on every pipeline startup, even when we only run preprocessing or Word2Vec. [runner.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/runner.py#L12) imports [contextual/__init__.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/contextual/__init__.py#L1), which immediately imports [confirmatory.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/contextual/confirmatory.py#L10). On this machine, `import stil_semantic_change.runner` took about `4.9s`, while `import stil_semantic_change.word2vec.train` took about `1.27s`; `confirmatory` alone was about `4.29s`. That makes worker/process startup slower than it needs to be and couples the cheap pipeline stages to `torch`/`transformers`.
- Medium: `preserve_accents` is a dead config knob right now. It is declared in [schema.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/utils/config/schema.py#L30), loaded in [loader.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/utils/config/loader.py#L79), and exposed in [default.yaml](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/conf/preprocess/default.yaml#L1), but the preprocessing path never reads it. That is a reproducibility/documentation risk because the config suggests an ablation we cannot actually run.
- Medium: `model.text_view` has no upfront validation, so a typo fails late as a raw `KeyError` inside training. The lookup happens directly in [train.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/word2vec/train.py#L63), while the valid values only live implicitly in [views.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/preprocessing/views.py#L12). Now that text views are a first-class artifact contract, this should fail fast with a clear config error.
- Low: the top-level README is now behind the codebase. [README.md](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/README.md#L28) still gives the old high-level quickstart but does not mention the multi-view prepared layout or `model.text_view`, so someone extending the pipeline will miss the new artifact contract and likely assume the old single-text representation.

**What I’d do next while the run finishes**
- Patch the runner to lazy-import `run_bert_confirmatory` inside the BERT stage, and probably lazy-import plotting too. This is the best payoff-to-risk item.
- Add explicit `text_view` validation during config loading, with the allowed values coming from one shared constant.
- Either implement `preserve_accents` in normalization or remove it from schema/config/tests so the config surface matches reality.
- Refresh the README to point to [prepared_artifact_layout_2026_03_21.md](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/prepared_artifact_layout_2026_03_21.md) and document the new prepared views.

I did not spot another obvious correctness bug in the core preprocessing path during this pass. The first three items above are safe to do in parallel and should not interfere with the active run. If you want, I can start by implementing the lazy-import cleanup plus `text_view` validation now.

---

### Turn 22 (2026-03-21T18:59:58.340Z)

**User**

```
Please go ahead and implement all of this. Also update all docs files. Also add your implementation changes so all can keep that in mind
```

**Outcome (Codex)**

Implemented the cleanup pass and documented it. The main runtime changes are in [runner.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/runner.py), [loader.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/utils/config/loader.py), [text.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/preprocessing/text.py), and [contextual/__init__.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/contextual/__init__.py). We now lazy-load the optional BERT/reporting stages, validate `model.text_view` up front, and make `preprocess.preserve_accents` actually change normalization behavior. I also added regression coverage in [test_config_loader.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/tests/test_config_loader.py) and expanded [test_preprocessing.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/tests/test_preprocessing.py).

I updated the core docs that future chats should rely on: [README.md](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/README.md), [project_overview.md](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/project_overview.md), [chat_handoff.md](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/chat_handoff.md), [progress_status_2026_03_20.md](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/progress_status_2026_03_20.md), and [prepared_artifact_layout_2026_03_21.md](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/prepared_artifact_layout_2026_03_21.md). I also added a dedicated implementation note in [runtime_config_cleanup_2026_03_21.md](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/runtime_config_cleanup_2026_03_21.md) so the new guardrails stay visible.

Verification passed:
- `uv run ruff check src tests README.md docs`
- `uv run pytest tests/test_preprocessing.py tests/test_config_loader.py tests/test_integration_toy_pipeline.py`
- result: `9 passed`

Committed as `016fdd3` with message `refactor(runtime): validate text views and lazy-load optional stages`.

I did not touch the active experiment outputs or restart the running job.

---

### Turn 23 (2026-03-21T19:09:49.010Z)

**User**

```
do you think we should cancel current run and rerun with fixes or no?
```

**Outcome (Codex)**

No, I would not cancel the current run.

These fixes are mostly runtime/config hygiene, not semantic changes for the active experiment:
- lazy-loading BERT/reporting only affects startup/import cost
- `model.text_view` validation only catches bad configs earlier
- `preprocess.preserve_accents` only changes outputs if it is `false`

Your current yearly run is using the normal setup:
- `model.text_view=content_lemma`
- `preprocess.preserve_accents=true`

So the running experiment’s actual corpus/model outputs should be materially the same as they would be under the new code.

My recommendation:
- let the current run finish
- audit its results normally
- use the new code for the next run
- only rerun immediately if you want every paper-facing artifact to be generated from commit `016fdd3` or later for strict provenance

So: finish this one, don’t cancel.

---

### Turn 24 (2026-03-21T19:16:29.860Z)

**User**

```
look at current run and  see progress and eta
```

**Outcome (Codex)**

As of **March 21, 2026, 16:16:43 BRT**, the active run in [ba65fe5b9cce](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce) is still in `prepare_corpus` and has reached **Prepared batch 146** in the log; by my batch parser it has **147 prepared batches** recorded, with the latest at **16:16:26 BRT** in [run_yearly_core.log](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/logs/run_yearly_core.log).

Using the last completed run on the same dataset as reference:
- full prep size was **474 batches**
- current run has about **327 prep batches left**
- recent prep speed is about **33.1 sec/batch** over the last 25 batches
- that implies about **3.0 hours left for prep**

Then the later stages on the previous full run took about:
- Word2Vec training: **983s** or about **16.4 min**
- alignment: **38s**
- scoring: **307s** or about **5.1 min**
- reports: **4s**

So the best current ETA is:
- **about 3.35 to 3.85 hours remaining total**
- likely finish around **March 21, 2026, 19:38 to 20:07 BRT**

If I had to give one single estimate, I’d call it:
- **around 19:50 BRT on March 21, 2026**

The run looks healthy, not stuck. The batch timestamps are still moving steadily.

---

### Turn 25 (2026-03-21T19:21:09.541Z)

**User**

```
What are the steps after run finish? we still need bert and tf-idf correct?
```

**Outcome (Codex)**

Yes. After this run finishes, we still need both `TF-IDF` and `BERT` for the comparative paper.

This current run is just the core `Word2Vec` pipeline:
- `prepare_corpus`
- `train_word2vec`
- `align_embeddings`
- `score_candidates`
- `report_candidates`

It does **not** include:
- `bert_confirmatory`
- any `TF-IDF` baseline

So the sequence after finish should be:

1. Audit this finished `Word2Vec` run.
   - check top drift terms
   - inspect neighbors
   - confirm the cleanup worked semantically, not just mechanically
   - decide whether this is the baseline we freeze

2. Freeze the run if it looks good.
   - document run id
   - record config and caveats
   - keep it as the `Word2Vec` baseline for comparison

3. Implement and run the `TF-IDF` drift baseline.
   - this is still the biggest missing comparison method
   - we need a per-term score table aligned to the same candidate vocabulary

4. Run `BERT` on a filtered comparison panel.
   - not on everything first
   - better on the selected candidate set from the cheaper methods

5. Build the comparison layer.
   - rank correlations
   - top-k overlap
   - agreement/disagreement cases
   - cost/runtime comparison

6. Optionally add the `PTPARL-V` validation table later.
   - separate from the main `BrPoliCorpus` run
   - useful as a noisy external validation layer

So the short answer is: **correct, we still need TF-IDF and BERT after this finishes.**  
If you want, once this run completes I can do the audit immediately and then start the `TF-IDF` implementation next.

---

### Turn 26 (2026-03-21T22:55:32.973Z)

**User**

```
check the eta
```

**Outcome (Codex)**

As of **March 21, 2026, 19:55:49 BRT**, the run is at **Prepared batch 470** in [run_yearly_core.log](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/logs/run_yearly_core.log).

Using the last completed run on this same dataset:
- total prep batches should be **474**
- so only **4 prep batches** are left
- recent speed is about **40.9 sec/batch**

That means:
- **prep likely finishes in about 2 to 3 minutes**
- after that, the remaining stages should take about **22 minutes** total, based on the previous completed run:
  - Word2Vec training: about **16.4 min**
  - alignment: about **0.6 min**
  - scoring: about **5.1 min**
  - reports: essentially immediate

Best estimate now:
- **about 24 to 26 minutes left total**
- likely finish around **March 21, 2026, 20:20 to 20:22 BRT**

So it’s very close now. The run looks healthy.

---

### Turn 27 (2026-03-21T23:17:25.732Z)

**User**

```
check again
```

**Outcome (Codex)**

As of **March 21, 2026, 20:17:43 BRT**, the run has already moved much further:

- `prepare_corpus` is finished
- `train_word2vec` is finished
- `align_embeddings` is finished
- it is now effectively in `score_candidates` / final scoring

I can confirm this from the stage manifests already on disk in:
[/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce)

Current completed timings for this run:
- `prepare_corpus` finished at **20:58:32 UTC / 19:58:32 BRT**
- `train_word2vec` finished at **21:15:26 UTC / 20:15:26 BRT**
- `align_embeddings` finished at **21:16:05 UTC / 20:16:05 BRT**

What is still missing:
- `scores/score_candidates_manifest.json`
- `reports/report_candidates_manifest.json`

So the best ETA now is:
- **about 3 to 5 minutes left**
- likely finish around **March 21, 2026, 20:21 to 20:23 BRT**

Why the log looks quiet right now:
- scoring/reporting are much quieter than Word2Vec training
- the presence of `eligible_vocabulary.parquet` in `scores/` shows scoring has already started

So it is essentially at the finish line.

---

### Turn 28 (2026-03-21T23:23:51.420Z)

**User**

```
ok, check results now
```

**Outcome (Codex)**

**Findings**
- High: the run is complete and mechanically clean, but the top drift list is still dominated by generic rhetorical/evaluative terms rather than clearly substantive political concepts. In [analysis_summary.md](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/reports/analysis_summary.md), the top drift candidates are `acaso`, `novidade`, `separar`, `óbvio`, `impossível`, `dizer-se`, `completo`, `refiro`, `apropriar`, `paralelo`, `propósito`, `bastar`, `admitir`, `incrível`, `exato`. That is better than the old malformed-lemma failure mode, but it still is not a paper-ready substantive drift panel by itself.
- Medium: the cleanup fixes did work. In [scores_aggregated.parquet](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/scores_aggregated.parquet) and [eligible_vocabulary.parquet](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/eligible_vocabulary.parquet), the old bad forms are gone: `digar`, `repitar`, `estarer`, `deverer`, `votarer`, `verer`, `tratar se`, `fazer ele`, `parecr ee`, `transformour se` are all absent, and whitespace lemmas are now `0`.
- Medium: the stable controls improved, but a few are still procedural rather than conceptually “stable content” terms. In [candidate_sets.json](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/candidate_sets.json), `juridicidade`, `orçamentária`, `recurso`, `trabalho`, `público`, `social` look usable, but `sessão`, `art.`, `ocupo`, and `cumprimentá-lo` are still institutional/procedural.
- Low: the theory seeds are present and look usable for comparison, but they are not especially high-drift under this baseline. In [scores_aggregated.parquet](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/scores_aggregated.parquet), `corrupção` and `liberdade` are around `0.24`, `economia` about `0.21`, `democracia` about `0.20`, and `reforma` about `0.17`.

**Bottom Line**

This run finished successfully on **March 21, 2026 at 20:21:27 BRT**. The full artifact package is in [ba65fe5b9cce](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce), and all stage manifests are present:
- [prepare_corpus_manifest.json](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/prepared/prepare_corpus_manifest.json)
- [train_word2vec_manifest.json](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/models/train_word2vec_manifest.json)
- [align_embeddings_manifest.json](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/aligned/align_embeddings_manifest.json)
- [score_candidates_manifest.json](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/score_candidates_manifest.json)
- [report_candidates_manifest.json](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/reports/report_candidates_manifest.json)

My recommendation is:
- freeze this as the cleaned technical `Word2Vec` baseline
- do not treat the raw top drift list as the final substantive candidate panel
- before paper-facing interpretation, add one more lexical/concept filter layer
- then move to `TF-IDF`, and after that run `BERT` on the filtered comparison set

So: this is a good baseline run mechanically, but not yet the final semantic story.

---

### Turn 29 (2026-03-21T23:41:24.119Z)

**User**

```
Ok, go ahead. Freeze this baseline. Then we need to create better filter that is not usueless words like the current top drifts. And we need to make sure of that before we run THE FULL7HRS run we just did. 

So please go ahead and fix this.
```

**Outcome (Codex)**

The cleaned baseline is frozen and the filter is now materially stronger.

I recorded the frozen run in [word2vec_baseline_freeze_2026_03_21.md](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/word2vec_baseline_freeze_2026_03_21.md) for run `ba65fe5b9cce`, and I documented the new panel logic plus the validation preview in [candidate_panel_filter_2026_03_21.md](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/candidate_panel_filter_2026_03_21.md). The code change is committed as `1e5822d` with `fix(selection): harden drift panel filtering`.

What changed in code:
- residual malformed lemma cases are patched in [text.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/preprocessing/text.py)
- candidate selection now uses dominant POS from prepared token shards in [score.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/word2vec/score.py)
- drift/stable panel defaults are centralized in [lexicons.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/selection/lexicons.py)
- config support for that gate is in [schema.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/utils/config/schema.py), [loader.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/utils/config/loader.py), and [default.yaml](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/conf/selection/default.yaml)

I validated the new panel against the frozen `ba65fe5b9cce` outputs without doing another 7-hour rerun. The preview drift panel moved from junk like `acaso`, `novidade`, `refiro`, `puder`, `tiver` to a much cleaner set:
- `intervenção`
- `planalto`
- `renovação`
- `troca`
- `inaceitável`
- `oposto`
- `perigoso`
- `crítico`
- `contradição`
- `excepcional`
- `inédito`
- `exposição`
- `bloqueio`
- `típico`
- `alvo`

Verification passed:
- `uv run ruff check src tests README.md docs`
- `uv run pytest tests/test_preprocessing.py tests/test_selection.py tests/test_config_loader.py tests/test_integration_toy_pipeline.py`

So yes: I think we should use commit `1e5822d` as the codebase for the next long rerun, not the older code.

---

### Turn 30 (2026-03-22T03:55:11.639Z)

**User**

```
Ok,go ahead and rerun for longrun now (because its night and i will leave it on during the night). Watch it for the first 5-10min to make sure its going all good, and make sure it runs all night with no problems(make sure of this). Then give me tail command
```

**Outcome (Codex)**

The long rerun is live and healthy.

Current run:
- experiment id: `8e15dc2372c5`
- pipeline PID: `8873`
- keep-awake PID: `9399`

What I verified:
- restarted it in a properly detached session, so the pipeline is now `PPID 1` rather than hanging off the app
- attached `caffeinate -dimsu -w 8873` so macOS stays awake while the run is active
- watched the clean restart for a bit over 5 minutes
- confirmed steady progress through fresh prep batches after the reset
- confirmed prepared artifacts are being written again

Latest healthy progress I saw:
- `Prepared batch 12` at `2026-03-22 01:11:30`

I can’t honestly guarantee “no problems all night,” but this is the most robust setup available from here: detached process, active logging, automatic stage reset on incomplete rerun, and sleep prevention tied to the run PID.

Tail command:

```bash
tail -n 50 -f /Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/8e15dc2372c5/logs/run_yearly_core.log
```

If this is a laptop, keep it plugged in and don’t close the lid unless you’re using a setup that prevents lid-sleep.

---

### Turn 31 (2026-03-22T14:08:37.215Z)

**User**

```
it finished, please check result and keep going
```

**Outcome (Codex)**

The overnight `Word2Vec` run finished, and I kept going. The important status is: the clean frozen baseline remains [ba65fe5b9cce](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce), and I implemented a first-class `TF-IDF` drift stage on top of it. The new TF-IDF artifacts are in [scores/tfidf_drift](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/tfidf_drift), and the writeup is in [tfidf_drift_baseline_2026_03_22.md](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/tfidf_drift_baseline_2026_03_22.md).

The raw TF-IDF list was too procedural at first, so I added a method-local panel filter on top of the shared selection rules. The cleaned TF-IDF drift panel on the frozen run is now: `crise`, `trabalhador`, `saúde`, `salário`, `emenda`, `eleição`, `previdência`, `provisório`, `preço`, `mínimo`, `político`, `voto`, `real`, `partido`, `destaque`. Full-vocabulary correlation with `Word2Vec` is meaningfully negative on this run, about `-0.386` Spearman, which is actually useful for the comparison paper because it shows the cheap baseline is not just reproducing the aligned-embedding ranking.

One integrity note: after the overnight run completed at `8e15dc2372c5`, I made an aborted forced `tfidf_drift` rerun attempt that briefly re-entered `prepare_corpus` before I killed it. So I do not want to treat [`8e15dc2372c5`](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/8e15dc2372c5) as the immutable prepared-artifact source. I documented that and kept `ba65fe5b9cce` as the safe frozen source. Code and docs are committed in `a0aff5e` (`feat(comparison): add tfidf drift baseline`). Validation passed with `ruff` and `13` tests.

The next best move is to build the shared `comparison_panel` that merges `Word2Vec` candidates, `TF-IDF` candidates, theory seeds, and stable controls, then use that as the common input for BERT and agreement/disagreement analysis.

---

### Turn 32 (2026-03-22T15:50:05.023Z)

**User**

```
Ok, make sure we have the best word2vec and tf-idf for each. Then go ahead and move to building comparison_panel
```

**Outcome (Codex)**

The frozen source of truth is now the clean baseline run [ba65fe5b9cce](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce). I refreshed the `Word2Vec` score artifacts there to use the stricter cleaned panel, kept the clean `TF-IDF` baseline on that same run, and then built the shared comparison panel directly on top of it so provenance stays anchored to one immutable source.

The new shared panel is here: [comparison_panel.parquet](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/comparison_panel/comparison_panel.parquet). It has `55` rows: `15` `Word2Vec` drift terms, `15` `TF-IDF` drift terms, `20` stable controls, and `5` theory seeds. Current overlap is `0`, so this first panel is essentially a clean disagreement panel, which is actually useful before BERT. The drift buckets are now:
- `Word2Vec`: `intervenção`, `planalto`, `renovação`, `troca`, `inaceitável`, `oposto`, `perigoso`, `crítico`, `contradição`, `excepcional`, `inédito`, `exposição`, `bloqueio`, `típico`, `alvo`
- `TF-IDF`: `crise`, `trabalhador`, `saúde`, `salário`, `emenda`, `eleição`, `previdência`, `provisório`, `preço`, `mínimo`, `político`, `voto`, `real`, `partido`, `destaque`

I documented everything in [comparison_panel_2026_03_22.md](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/docs/comparison_panel_2026_03_22.md) and updated the main handoff/status docs and [README.md](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/README.md). The code is committed as `b04aca1` with `feat(comparison): add shared comparison panel`. Verification passed with `uv run ruff check ...` and `uv run pytest tests/test_comparison_panel.py tests/test_selection.py tests/test_tfidf.py`.

The next move is clear now: point contextual BERT at this shared panel instead of a Word2Vec-only candidate set.

---

### Turn 33 (2026-03-22T16:15:56.711Z)

**User**

```
Ok, go ahead
```

**Outcome (Codex)**

BERT is now refactored to use the shared comparison panel by default, and I started the real confirmatory run on the frozen baseline `ba65fe5b9cce`.

What changed:
- contextual BERT now prefers [comparison_panel.parquet](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/comparison_panel/comparison_panel.parquet) instead of the old Word2Vec-only `candidate_sets.json`
- it still falls back to the legacy path if the panel is missing
- the BERT comparison output now carries shared-panel metadata and compares against both cheap methods, not just Word2Vec
- `bert_confirmatory` task now includes the comparison prerequisites in [bert_confirmatory.yaml](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/conf/task/bert_confirmatory.yaml)

Validation passed:
- `uv run ruff check ...`
- `uv run pytest tests/test_confirmatory.py tests/test_comparison_panel.py tests/test_tfidf.py tests/test_selection.py`
- result: `12 passed`

Committed:
- `af3fb08` `refactor(contextual): use shared comparison panel`

Live run status:
- frozen source run: [ba65fe5b9cce](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce)
- output directory: [bert_confirmatory](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/bert_confirmatory)
- active Python worker PID: `28107`

Right now it is still in the quiet startup/sampling part, but it is healthy: the worker is alive and has been running near 100% CPU, so it is doing work rather than sitting idle.

Good monitor commands:

```bash
ps -o pid,ppid,etime,%cpu,%mem,command -p 28107
```

```bash
ls -ltr /Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/bert_confirmatory
```

When it finishes, the key files to inspect will be:
- [scores.parquet](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/bert_confirmatory/scores.parquet)
- [comparison_with_word2vec.parquet](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/bert_confirmatory/comparison_with_word2vec.parquet)
- [summary.json](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/bert_confirmatory/summary.json)

Send me a note when you want me to check the finished BERT outputs, or if you want me to poll this run again later.

---

### Turn 34 (2026-03-22T16:26:01.405Z)

**User**

```
what would be the ETA for this?
```

**Outcome (Codex)**

As of **March 22, 2026, 17:?? BRT** there’s enough signal to give a real estimate.

What I can confirm:
- the BERT run is healthy and active
- it already wrote [sampled_occurrences.parquet](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/bert_confirmatory/sampled_occurrences.parquet)
- it sampled **82,468 occurrences**
- it’s running on **Apple `mps`**, not plain CPU
- the worker is still near **100% CPU**, which is consistent with active preprocessing / embedding work

Best ETA:
- **roughly 45 to 90 minutes total from launch**
- since it has already been running about **6 minutes**, I’d estimate **about 40 to 85 minutes left**
- my single best guess is **around 50 to 65 minutes left**

So I’d expect completion roughly around:
- **March 22, 2026, 18:10 to 18:35 BRT**

Why the range is still wide:
- BERT startup is quiet
- this run has a large sample cap hit almost everywhere (`64` per term per slice)
- the expensive part is embedding `82k` contexts, and that can vary a lot on `mps`

Quick monitor commands:

```bash
ps -o pid,etime,%cpu,%mem,command -p 28107
```

```bash
ls -ltr /Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/bert_confirmatory
```

When `occurrence_embeddings_meta.parquet` appears, the ETA will tighten a lot.

---

### Turn 35 (2026-03-22T16:48:34.388Z)

**User**

```
I've already tested and its faster to run in CPU instead of MPS
```

**Outcome (Codex)**

Yes, I switched it.

Current status as of **2026-03-22 13:51:20 BRT**:
- the old `mps` run was stopped
- the BERT run was restarted on **CPU**
- active worker PID is `35719`
- log file is now:
  [direct_run.log](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/bert_confirmatory/direct_run.log)

Best ETA for the **CPU** run:
- **about 30 to 60 minutes from this restart**
- my best guess is **35 to 45 minutes**
- likely finish around **2026-03-22 14:25 to 14:35 BRT**

Why this estimate changed:
- the earlier ETA was for the slower `mps` path
- you were right to call it out, so I added an explicit `model.bert_device` override and relaunched with `cpu`

Monitor commands:

```bash
tail -n 50 -f /Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/bert_confirmatory/direct_run.log
```

```bash
ps -o pid,etime,%cpu,%mem,command -p 35719
```

---

### Turn 36 (2026-03-22T17:14:13.654Z)

**User**

```
check how its going
```

**Outcome (Codex)**

As of **2026-03-22 14:14:25 BRT**, it’s still running on CPU and looks healthy.

Current status:
- PID: `35719`
- elapsed: **23m 39s**
- CPU: **71.2%**
- memory: **4.1%**
- artifacts so far:
  - [sampled_occurrences.parquet](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/bert_confirmatory/sampled_occurrences.parquet)
  - [direct_run.log](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/bert_confirmatory/direct_run.log)

Interpretation:
- it is past sampling
- it has not yet written the embedding/prototype outputs
- so it is still in the expensive middle part

Updated ETA:
- **about 15 to 35 minutes left**
- best guess: **around 14:35 to 14:50 BRT**

Useful checks:

```bash
ps -o pid,ppid,etime,%cpu,%mem,command -p 35719
```

```bash
ls -ltr /Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/bert_confirmatory
```

When `occurrence_embeddings_meta.parquet` appears, we’ll know it has cleared the longest bottleneck.

---

### Turn 37 (2026-03-22T17:52:15.664Z)

**User**

```
go ahead and check again
```

**Outcome (Codex)**

As of **2026-03-22 14:52:30 BRT**, it is still running and still looks healthy, but my earlier ETA was too optimistic.

Current state:
- PID `35719` is alive
- elapsed: **1h 01m 44s**
- CPU: **97.5%**
- outputs so far:
  - [direct_run.log](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/bert_confirmatory/direct_run.log)
  - [sampled_occurrences.parquet](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/run/outputs/experiments/brpolicorpus_floor_yearly/ba65fe5b9cce/scores/bert_confirmatory/sampled_occurrences.parquet)

Important context:
- it sampled **82,468** occurrences
- the next big files are only written **after** the full embedding pass finishes, so the artifact directory stays quiet for a long time
- that means “only one parquet so far” does **not** mean it is stuck

What I think now:
- it is very likely in the long embedding pass
- a more honest ETA is **another 1 to 3 hours**
- best rough guess: finish around **16:00 to 17:30 BRT on March 22, 2026**

One reason this stage is expensive is here:
[confirmatory.py](/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/src/stil_semantic_change/contextual/confirmatory.py#L354)
It builds contexts occurrence by occurrence, and the embedding outputs are only persisted after the whole pass completes.

So the short answer is: **still running, still healthy, but this is probably a multi-hour CPU job, not a sub-hour one.**

---

## Related repository docs (cross reference)

| Topic | Path |
| --- | --- |
| Handoff index | `Articles/N2/docs/chat_handoff.md` |
| Progress and frozen baseline note | `Articles/N2/docs/progress_status_2026_03_20.md` |
| Pipeline readiness | `Articles/N2/docs/comparative_pipeline_readiness_2026_03_21.md` |
| Word2Vec freeze | `Articles/N2/docs/word2vec_baseline_freeze_2026_03_21.md` |
| Candidate filter | `Articles/N2/docs/candidate_panel_filter_2026_03_21.md` |
| TF-IDF on frozen baseline | `Articles/N2/docs/tfidf_drift_baseline_2026_03_22.md` |
| Comparison panel | `Articles/N2/docs/comparison_panel_2026_03_22.md` |
| Exploratory plan | `Articles/N2/docs/exploratory_drift_comparison_plan.md` |

## Note on research and citations

Several early turns asked for article backed methodology notes and visualization research with citation discipline. Those writeups landed in the dated docs under `Articles/N2/docs/` (for example `comparative_drift_methodology_2026_03_20.md`). This summary does not duplicate every citation; it points you at the docs that were created or updated inside the same thread.
