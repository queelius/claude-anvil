---
name: simulation
description: >-
  This skill should be used when the user asks to "design a Monte Carlo
  simulation", "validate my theoretical result", "set up a simulation
  study", "how many replications do I need", "plan a coverage study",
  or needs to design simulations for verifying theoretical results.
  Covers sample size determination, convergence diagnostics, and result
  presentation. Specialized for statistical methodology papers.
---

# Monte Carlo Simulation Design

Help the researcher design rigorous Monte Carlo simulations to validate theoretical results. Simulations bridge the gap between theory and practice -- they demonstrate that analytical formulas work as predicted and reveal finite-sample behavior.

## Step 1: Read Context

Read `.papermill.md` (Read tool) for:
- **Thesis**: What theoretical result needs validation.
- **Experiments**: Any existing simulation experiments.

If `.papermill.md` does not exist, ask the user which theoretical result needs validation. Simulation design can proceed without the state file — suggest running `/papermill:init` afterward.

Scan the repository for existing simulation code and results (Glob/Read tools).

## Step 2: Identify What to Validate

Ask: "Which theoretical result are you validating with this simulation?"

Common simulation targets in methodology papers:
- **Asymptotic distributions**: Does the CLT approximation hold at finite n?
- **Estimator properties**: Is the MLE unbiased? What is its MSE?
- **Covariance/information matrices**: Does the empirical covariance match the theoretical Fisher information?
- **Confidence interval coverage**: Do 95% CIs actually cover 95% of the time?
- **Power analysis**: Can the test detect a given effect size?
- **Algorithm convergence**: Does the optimizer find the right answer?

## Step 3: Design the Simulation

### Parameters

- **True parameter values**: Choose several configurations spanning easy, moderate, and hard cases.
- **Sample sizes**: Include small (n=20-50), moderate (n=100-500), and large (n=1000+) to show convergence.
- **Number of replications**: Typically R=1,000-10,000. More replications reduce Monte Carlo error but cost time. The Monte Carlo standard error for a proportion p is sqrt(p(1-p)/R).

### Data Generation

Specify exactly how to generate synthetic data:
1. Set random seed for reproducibility.
2. Generate from the known model with known true parameters.
3. Apply the estimation/inference procedure to each replicate.
4. Collect the quantities of interest.

### Metrics

| What to measure | How to summarize |
|----------------|-----------------|
| Bias | Mean(estimate) - true value |
| Variance | Var(estimates) across replicates |
| MSE | Bias^2 + Variance |
| Coverage | Fraction of CIs containing true value |
| Convergence rate | Plot metric vs. n on log scale |

### Memory and Compute

- **Batch processing**: If R * n is large, process in batches to control memory. Accumulate sufficient statistics rather than storing all raw data.
- **Parallelization**: Independent replicates are embarrassingly parallel. Use `parallel` (R), `multiprocessing` (Python), or OpenMP (C++).
- **Progress reporting**: For long simulations, report progress every ~10% of replicates.

## Step 4: Convergence Diagnostics

Before presenting results, verify the simulation itself is reliable:

1. **Monte Carlo standard errors**: Report them alongside point estimates. If MCSE is large relative to the quantity of interest, increase R.
2. **Trace plots**: Plot running averages to verify convergence.
3. **Sensitivity to seed**: Run with 2-3 different seeds. Results should be stable.

## Step 5: Result Presentation

Design the output tables and figures:

### Tables
- Rows: parameter configurations or sample sizes
- Columns: bias, SD, MSE, coverage, or whatever metrics are relevant
- Include Monte Carlo standard errors in parentheses

### Figures
- **Convergence plots**: Metric vs. n (log scale) with theoretical prediction overlaid
- **QQ plots**: Compare empirical distribution of estimator to theoretical asymptotic distribution
- **Box plots**: Distribution of estimates across replicates for each configuration

## Step 6: Common Pitfalls

Warn about:

- **Insufficient replicates**: R=100 is rarely enough. For coverage studies, you need R >= 1,000.
- **Ignoring Monte Carlo error**: Always report MCSE. A coverage of 0.94 with MCSE=0.007 is consistent with 0.95.
- **Conditioning bias**: If you filter out "non-convergent" replicates, the remaining sample is biased. Report the rejection rate.
- **Single parameter configuration**: Results at one parameter value do not generalize. Test across a range.
- **Floating-point issues**: For extreme parameter values, numerical issues can corrupt results. Include sanity checks.

## Step 7: Update State File

If `.papermill.md` exists, register the simulation (Edit tool) under `experiments`. If it does not exist, skip registration and suggest running `/papermill:init`.

The entry uses the standard experiment schema with an optional `config` block for simulation-specific parameters:

```yaml
experiments:
  - name: "simulation-name"
    type: "simulation"
    hypothesis: "Empirical covariance matches theoretical FIM as n grows"
    status: "planned"
    script: "research/simulate_covariance.R"
    last_run: null
    config:  # simulation-specific extension, not in the base experiment schema
      replications: 5000
      sample_sizes: [50, 100, 200, 500, 1000]
      parameter_configs: 3
```

Append a timestamped note documenting the simulation design.

## Step 8: Suggest Next Steps

Based on the simulation status, suggest the most relevant next step:

- **Implement**: "Write the simulation script. Start with a small pilot (R=100) to debug before the full run."
- If the simulation validates a proof → "Once results confirm the theory, integrate both the proof and simulation evidence into the paper. Use `/papermill:proof` if the proof itself needs work."
- If simulation results are surprising or contradict theory → "The simulation suggests the theoretical result may need revisiting. Use `/papermill:proof` to re-examine the proof's assumptions."
- If results are written up → "Use `/papermill:review` to get feedback on the presentation of simulation results."
