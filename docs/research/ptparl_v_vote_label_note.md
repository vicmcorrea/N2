# PTPARL-V Vote Label Note

This note records the status of the locally organized `PTPARL-V` dataset and an important caveat about its vote labels.

## Local Dataset Status

The published `PTPARL-V` bundle has been downloaded and organized under:

- `/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/RawDatasets/PTPARL-V`

Canonical layers now exist in the same style as the other N2 datasets:

- metadata: `/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/RawDatasets/PTPARL-V/exports/Metadata/initiatives`
- source PDFs: `/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/RawDatasets/PTPARL-V/exports/Source/pdf_minutes`
- raw CSVs: `/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/RawDatasets/PTPARL-V/exports/V0-raw/csv`
- processed CSVs: `/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/RawDatasets/PTPARL-V/exports/V0-1/csv`
- inventory: `/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/RawDatasets/PTPARL-V/inventory`

Current inventory summary:

- intervention rows: `10,068`
- words: `11,964,303`
- characters: `73,809,995`
- year coverage: `1995` to `2022`

## Where The Vote Information Is

Initiative-level vote summaries are present in:

- `/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/RawDatasets/PTPARL-V/exports/V0-1/csv/initiatives.csv`

Relevant columns include:

- `vot_results`
- `vot_in_favour`
- `vot_against`
- `vot_abstention`

Per-intervention assigned vote labels are present in:

- `/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/RawDatasets/PTPARL-V/exports/V0-1/csv/out_with_text_processed.csv`
- `/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/RawDatasets/PTPARL-V/exports/V0-1/csv/interventions.csv`
- `/Users/victor/Dropbox/USP/ResearchThesis/Articles/N2/RawDatasets/PTPARL-V/exports/V0-1/csv/parliamentary_minutes.csv`

The main per-intervention label column is:

- `vote`

Typical values are:

- `vot_in_favour`
- `vot_against`
- `vot_abstention`

## Important Caveat

These labels are usable supervision signals, but they should not be described too strongly.

The released data appears to assign each intervention-level `vote` label by matching:

- the speaker's parliamentary group: `dep_parl_group`
- against the initiative-level vote lists: `vot_in_favour`, `vot_against`, `vot_abstention`

So, in practice, this is best treated as:

- a `derived political-position label` attached to each intervention

and not automatically as:

- a separately verified individual nominal vote cast by that exact deputy for that exact intervention

## Additional Caveat From Local Inspection

The local exported tables are noisier than a simple one-to-one party vote mapping.

There is also a specific identifier issue that can create false conflicts during analysis.

In the released tables, `ini_num + ini_leg` is not always a unique initiative key. The same `ini_num` can reappear within the same legislature across different sessions with:

- different `ini_type`
- different `ini_session`
- different `ini_title`
- different vote breakdowns

So if rows are grouped only by:

- `ini_num + ini_leg`

then the same deputy can appear to have conflicting labels even when the rows belong to different initiatives.

Safer initiative keys are:

- `ini_num + ini_leg + ini_type`

and, when useful for checking:

- `ini_session`
- `ini_title`
- `pub_date`

Important observations from the current local `V0-1` export:

- `ini_leg + ini_num` is not a unique initiative key by itself
- `ini_leg + ini_num + ini_type` is a safer initiative key
- the same deputy can appear multiple times for the same initiative key
- some initiative-party groups contain more than one assigned vote label
- some initiative-deputy groups also contain more than one assigned vote label

So the safest interpretation is not:

- `one clean vote label per intervention with no ambiguity`

but rather:

- `a useful but noisy derived political supervision layer that requires deduplication or aggregation before evaluation`

## Recommended Interpretation For N2

Safe phrasing:

- `PTPARL-V provides initiative-level vote outcomes and derived political-position labels for interventions.`
- `The intervention-level label is useful as an external supervision signal, but it should be interpreted cautiously because the released export may contain repeated rows and conflicting assigned labels for some initiative-party or initiative-deputy combinations.`

Avoid stronger phrasing unless independently verified from official nominal roll-call data:

- `each intervention has a ground-truth individual deputy vote`
- `the dataset contains direct deputy-level roll-call labels for every intervention`

## Practical Consequence

For N2, `PTPARL-V` is still useful for:

- external political supervision
- contrastive validation across parties and vote positions
- testing whether drift signals align with legislative conflict structure

But if a later experiment needs strict deputy-level roll-call validation, it would be better to combine this dataset with official vote records from Parliament rather than relying only on the released intervention label.

Even for N2, the dataset should first be converted into a cleaner evaluation table with an explicit analysis unit, for example:

- initiative-party aggregated labels, dropping conflicted cases
- or initiative-deputy majority labels, dropping conflicted cases
- and only using interventions with valid processed text

## What This Improves Relative To BrPoliCorpus

Compared with `BrPoliCorpus`, `PTPARL-V` gives N2 a better evaluation setting, but not a full replacement corpus.

With `BrPoliCorpus` alone, the project mainly supports:

- exploratory drift detection
- qualitative interpretation
- historical plausibility checks

With `PTPARL-V`, we also gain an external political signal linked to interventions:

- party-aligned vote labels
- initiative-level vote outcomes

That means we can test whether drift measures track politically meaningful structure, for example:

- whether high-drift terms separate `vot_in_favour` vs `vot_against` interventions
- whether different methods correlate differently with vote alignment
- whether some methods capture polarization or framing differences better than others

## Important Limit Of This Validation

The vote labels do not directly prove that a word changed meaning.

They help answer questions like:

- `does this drift signal align with political positioning?`
- `does this method capture politically meaningful lexical variation?`

They do not by themselves answer:

- `did this word truly undergo semantic change in the strict linguistic sense?`

So the safest interpretation is:

- `PTPARL-V provides better grounds for evaluating the political relevance and external usefulness of drift signals`

but not:

- `PTPARL-V provides a gold-standard ground truth for semantic drift`

## Recommended N2 Framing

A strong way to use the corpora together is:

- `BrPoliCorpus` as the broad exploratory Portuguese political-discourse corpus
- `PTPARL-V` as the validation-oriented corpus with noisy external political labels

In that setup, the paper can defend claims such as:

- some drift techniques align more strongly with legislative conflict and party positioning
- some methods may be cheaper yet capture similar politically relevant movement
- agreement or disagreement across methods is itself informative

This is a substantially stronger validation story than using `BrPoliCorpus` alone.

## Current Recommendation

For N2, the best current plan is:

- keep `BrPoliCorpus` as the main exploratory corpus
- continue the full Word2Vec / TF-IDF / BERT comparison there
- treat `PTPARL-V` as a separate validation-oriented corpus
- build a cleaned supervision table before using it in evaluation

So `PTPARL-V` should be framed as:

- a strong secondary validation resource

and not as:

- a simple drop-in replacement for the main corpus
