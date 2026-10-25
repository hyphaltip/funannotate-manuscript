# funannotate-manuscript

Benchmarks, experiments and validation behind the funannotate manuscript: how the training data for Augustus and the other
predictors are chosen (PASA models, BUSCO models, fallbacks), how PASA 2.6 compares with the earlier PASA in the funannotate
1.9 pipeline, and the parameter and gating experiments that set the defaults. Moved out of the funannotate repository so that
the tool repository holds code and its unit tests only.

## Contents

| Path | What it is |
|---|---|
| `assessment_pasa2.6_fun1.9/` | The assessment: `README.md` (results and open items), `data/` (result tables), `figures/` (plots and `make_figures.py`), `scripts/` (experiments B, C and D, EVM refit, gate sweeps, `predict_scorer.py`, and the analysis scripts) |
| `benchmark/slurm/` | Slurm batch scripts for the PASA, Trinity, EVM and training benchmarks, and `benchmark_env.sh` |
| `benchmark/tests/` | Manual benchmark drivers and output checks (`benchmark_*.sh`, `benchmark_*.py`) |
| `benchmark/plans/` | Notes for running the benchmarks (quick start, Slurm, Trinity Rust) |

The unit tests for the training-source and Augustus gates stay in funannotate (`tests/test_training_source_decision.py`,
`tests/test_augustus_parameters.py`), and so does the methods draft `docs/training_data_selection_methods.md`.

## Running notes

The scripts were run on the UCR HPCC (Slurm partition `stajichlab`, Apptainer images of funannotate) and contain absolute paths
under `/bigdata/stajichlab/...`; they are a record of what was run, not portable workflows. Experiment inputs are listed in
`assessment_pasa2.6_fun1.9/data/` (genome sets, scores); large outputs stay on the cluster.

## History

The files were extracted from nextgenusfs/funannotate with `git filter-repo`, so their commit history is kept. Paths changed:
`docs/assessment_pasa2.6_fun1.9/` is now `assessment_pasa2.6_fun1.9/`, the `benchmark_*` scripts at the repository root are in
`benchmark/slurm/`, `tests/benchmark_*` is `benchmark/tests/`, and `plans/BENCHMARK_*.md` is `benchmark/plans/`.

License: BSD 2-Clause, as funannotate.
