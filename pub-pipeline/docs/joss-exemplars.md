# JOSS R Package Paper Exemplars

## Summary Table

| Package | Domain | DOI | Words | Sections | Notes | Year |
|---------|--------|-----|-------|----------|------------|------|
| univariateML | MLE density estimation | 10.21105/joss.01863 | ~450 | Summary, References | concise, under current minimum | 2019 |
| survPen | Hazard modelling | 10.21105/joss.01434 | ~900 | Background, Summary, Ack, Refs | good domain-first structure | 2019 |
| BayesMFSurv | Bayesian survival | 10.21105/joss.02164 | ~1200 | Summary, Motivation, Package, Availability, Refs | misclassified failures | 2020 |
| aorsf | Random survival forest | 10.21105/joss.04705 | ~1200 | Summary, SoN, Related, Background, Methods, Benchmarks, Ack, Refs | modern structure | 2022 |
| Overlapping | Distribution overlap | 10.21105/joss.01023 | ~700 | Summary, Examples, Refs | simple/focused | 2018 |
| survxai | Survival model explanations | 10.21105/joss.00961 | ~600 | Summary, Refs | ML focus | 2018 |
| performance | Statistical model testing | 10.21105/joss.03139 | ~1000 | Summary, SoN, Refs | easystats suite | 2021 |

**Note**: Pre-2024 papers did not require State of the Field, Software Design, Research Impact Statement, or AI Usage Disclosure (these are newer JOSS requirements). Current submissions MUST include all required sections.

---

## Most Relevant Exemplar: univariateML

**Why relevant**: MLE for univariate distributions, R package, statistical focus.

**GitHub**: https://github.com/JonasMoss/univariateML

### Full paper.md

```yaml
title: 'univariateML: An R package for maximum likelihood estimation of univariate densities'
tags:
  - R
  - statistics
  - maximum likelihood
  - density estimation
authors:
  - name: Jonas Moss
    orcid: 0000-0002-6876-6964
    affiliation: 1
affiliations:
 - name: University of Oslo
   index: 1
date: 25 November 2019
bibliography: paper.bib
```

**Structure**: Single `# Summary` section (~450 words) covering:
- What the package does (MLE for 20+ densities)
- Code example with plot (Egypt mortality data)
- Model selection example (AIC comparison)
- Use cases (exploratory analysis, copulas, density estimation)
- Implementation details (analytic formulas, Newton-Raphson)
- Comparison to alternatives (stats4::mle, Rfast)

**Patterns to note**:
- Very concise — under JOSS minimum by today's standards
- Code examples inline in the paper
- Direct comparison to competing packages
- Single author, single affiliation
- **Would need additional sections under 2025+ requirements**

---

## Exemplar: survPen (hazard modelling)

**Why relevant**: Hazard-based modelling, survival analysis domain, penalized splines.

**GitHub**: https://github.com/fauvernierma/survPen

**Structure**:
1. `# Background` — Survival analysis context, excess mortality, net survival
2. `# Summary` — What survPen does, comparison to alternatives, features list
3. `# Acknowledgements`
4. `# References`

**Patterns to note**:
- Opens with domain context (Background), not just package description
- Lists 5 bullet-point features
- Names competing packages explicitly (rstpm2, bamlss, R2BayesX) and explains why survPen is better
- Mentions 3 real ongoing projects using the package
- ~900 words total
- Available on both GitHub and CRAN

---

## Exemplar: aorsf (modern structure)

**Why relevant**: Published 2022, has Statement of Need section, closest to current JOSS format.

**GitHub**: https://github.com/bcjaeger/aorsf

**Structure**:
1. `# Summary` — What aorsf does, target audience
2. `# Statement of need` — Purpose and target users (analysts + researchers)
3. `## Related software` — Direct comparison table of competing packages
4. `# Background` — Random forests, oblique vs axis-based, censoring
5. `# Newton Raphson scoring` — Mathematical detail with equation
6. `# Variable importance` — Technical contribution
7. `# Benchmarking` — Performance claims with citation
8. `# Acknowledgements` — Funding sources
9. `# References`

**Patterns to note**:
- Separates Summary from Statement of Need (good modern practice)
- Includes mathematical equations (LaTeX in Markdown)
- Uses `\begin{figure}...\end{figure}` for complex figures
- Explicit "Related software" subsection naming 5+ packages
- Two distinct target audiences identified
- ~1200 words

---

## Exemplar: BayesMFSurv (survival + misclassification)

**Why relevant**: Bayesian survival models, misclassified failure events.

**GitHub**: https://github.com/Nicolas-Schmidt/BayesMFSurv

**Structure**:
1. `# Summary` — Problem context, motivation, what the package does
2. `# Motivation, Description, Applications` — Extended justification and comparison
3. `# BayesMFSurv R Package` — Function-by-function description
4. `# Availability` — Installation instructions
5. `# References`

**Patterns to note**:
- Heavy on domain motivation (misclassified failure events explained thoroughly)
- Lists each function with description (4 functions)
- Names 8+ competing packages with citations
- Cross-disciplinary examples (political science, cancer, ancient civilizations)
- ~1200 words
- Uses `remotes::install_github()` for installation

---

## Patterns and Anti-Patterns

### Common Structural Choices
- **Opening**: Domain problem first, then package solution
- **Comparison section**: Every paper names specific competing packages
- **Code examples**: Most include inline R code in the paper
- **References**: 15-30 citations typical (mix of methodology and software)
- **Length**: 600-1200 words for pre-2024 papers; target 750-1750 now

### What Works Well
1. **Concrete use cases**: survPen lists 3 real projects; aorsf cites benchmarks
2. **Direct competitor comparison**: "Package X does Y but not Z; we do Z"
3. **Mathematical precision**: aorsf includes the Newton-Raphson update equation
4. **Dual audience**: aorsf explicitly targets both analysts and researchers
5. **Feature bullet lists**: survPen's 5-bullet feature list is scannable

### Anti-Patterns to Avoid
1. **Too short**: univariateML's ~450 words would not pass current requirements
2. **Missing sections**: Pre-2024 papers lack State of Field, Software Design, Research Impact
3. **Vague competitors**: "Some packages exist" without naming them
4. **No examples**: Papers without code snippets feel abstract
5. **Installation-only availability**: Should be on CRAN, not just GitHub

### Tags Commonly Used for R Statistics Packages
```yaml
tags:
  - R
  - survival analysis / statistics / reliability
  - maximum likelihood / Bayesian
  - hazard function / failure rate
  - [domain-specific tag]
```

