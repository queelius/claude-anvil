---
name: experiment
description: >-
  This skill should be used when the user asks to "design an experiment",
  "plan my experiments", "set up a benchmark", "how should I test my
  thesis", "design a computational study", or needs to plan experiments
  for a research paper. Covers hypothesis formulation, variable
  identification, methodology selection, and success criteria definition.
  Produces a structured experiment plan with reproducibility in mind.
---

# Experiment Design

Help the researcher design rigorous experiments or computational studies. Good experiments are hypothesis-driven, reproducible, and have clear success criteria before they are run.

## Step 1: Read Context

Read `.papermill.md` (Read tool) for:
- **Thesis**: The claim the experiments should support or test.
- **Existing experiments**: Any previously registered experiments.
- **Format and tools**: What languages/tools are in the repo (R, Python, C++, etc.).

If `.papermill.md` does not exist, ask the user what claim the experiments should test. Experiment design can proceed without the state file — suggest running `/papermill:init` afterward to register experiments persistently.

Scan the repository for existing code (Glob tool) in `research/`, `code/`, `scripts/`, `experiments/`, or `analysis/` directories.

## Step 2: Identify What Needs Testing

Ask the user: "What specific claim or aspect of your thesis do these experiments need to support?"

Different contribution types need different experimental approaches:

| Contribution | Experimental approach |
|-------------|----------------------|
| Theorem/proof | Numerical validation of theoretical predictions |
| Algorithm | Runtime/accuracy benchmarks against baselines |
| Statistical method | Monte Carlo simulations with known ground truth |
| Empirical finding | Controlled experiments with statistical tests |
| Framework/model | Case studies demonstrating applicability |

## Step 3: Design the Experiment

For each experiment, specify:

### Hypothesis
State the expected outcome in falsifiable terms. "We expect X to be Y under conditions Z" -- not "we want to show our method works."

### Variables
- **Independent variables**: What you manipulate (parameters, dataset size, algorithm choice).
- **Dependent variables**: What you measure (accuracy, runtime, error rate).
- **Control variables**: What you hold constant (hardware, random seeds, data preprocessing).

### Methodology
- Data generation or collection procedure
- Algorithm/method configuration
- Number of replications or samples
- Statistical tests to apply (t-test, bootstrap CI, etc.)
- Baseline comparisons

### Success Criteria
Define **before running** what constitutes support for the hypothesis. This prevents post-hoc rationalization.

### Reproducibility
- Random seed strategy
- Hardware/software environment
- Data availability
- Script that runs the full experiment end-to-end

## Step 4: Address Common Pitfalls

Check for and warn about:

- **Cherry-picking**: Are you testing one configuration or sweeping parameters fairly?
- **Multiple comparisons**: If running many tests, apply correction (Bonferroni, FDR).
- **Overfitting to test data**: Is there a held-out validation set?
- **Computational budget**: Is this feasible given available hardware and time?
- **Missing baselines**: Every method needs comparison to something. Even "no method" is a baseline.

## Step 5: Register the Experiment

If `.papermill.md` exists, update it (Edit tool) by adding to the `experiments` list. If it does not exist, skip registration and suggest running `/papermill:init` to persist the experiment.

```yaml
experiments:
  - name: "descriptive-name"
    type: "simulation | benchmark | case-study | ablation"
    hypothesis: "Expected outcome in one sentence"
    status: "planned | running | completed | failed"
    script: "path/to/script.R"
    last_run: null
```

Append a timestamped note documenting the experiment design.

## Step 6: Suggest Next Steps

Based on the experiment type, suggest the most relevant next step:

- If this is a Monte Carlo study → "Use `/papermill:simulation` for detailed simulation design — it covers sample sizes, convergence diagnostics, and result presentation."
- If the experiment involves proving a theoretical prediction → "Consider `/papermill:proof` to verify the theory before running experiments."
- If results will need statistical analysis → "Implement the script, run it, then use `/papermill:review` once the results are written up."
- For all experiments → "Start with a small pilot run to debug before the full experiment."
