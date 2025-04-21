### Methodology for Hierarchical Inference of Cosmological and Feedback Parameters

#### Overview

This methodology outlines a step-by-step approach for inferring cosmological and feedback parameters from the simulated galaxy catalogs, leveraging both galaxy-level and catalog-level summary statistics. The approach is informed by the EDA and is designed to maximize parameter sensitivity, minimize degeneracies, and operate efficiently within computational constraints.

---

#### 1. **Feature Engineering and Preprocessing**

**a. Feature Selection and Transformation**
- Select the following galaxy properties as primary observables: $M_{star}$, $M_t$, $V_{max}$, $M_{BH}$, $SFR$, $Z_{star}$, and $K$-band magnitude.
- For each property, compute the following summary statistics within each catalog:
  - Mean, standard deviation, median, 1st and 99th percentiles.
  - For $M_{star}$, $V_{max}$, and $M_{BH}$, stratify statistics by mass/luminosity bins (e.g., low, intermediate, high).
- Apply logarithmic transformation to all mass, velocity, and size features.
- Standardize all summary statistics (subtract mean, divide by standard deviation across catalogs).

**b. Dimensionality Reduction**
- Perform Principal Component Analysis (PCA) on the standardized summary statistics across all catalogs.
- Retain the first 3–4 principal components, as these capture the majority of variance and are less redundant.

---

#### 2. **Summary Statistic Construction**

**a. Catalog-Level Summary Table**
- For each catalog, construct a feature vector \(\mathbf{s}_i\) containing:
  - The selected summary statistics (means, stds, percentiles) for each property and bin.
  - The retained principal components.
- The final summary vector for catalog \(i\) is \(\mathbf{s}_i \in \mathbb{R}^d\), where \(d\) is the total number of selected statistics and PCs.

**b. Data Matrix**
- Assemble the data matrix \(S = [\mathbf{s}_1, \ldots, \mathbf{s}_N]^T\) for all \(N=1000\) catalogs.
- Construct the parameter matrix \(\Theta = [\boldsymbol{\theta}_1, \ldots, \boldsymbol{\theta}_N]^T\), where \(\boldsymbol{\theta}_i\) contains the 6 parameters for catalog \(i\).

---

#### 3. **Hierarchical Statistical Modeling**

**a. Model Structure**
- Adopt a Bayesian hierarchical model to capture the relationship between summary statistics and parameters, accounting for catalog-to-catalog variation and parameter degeneracies.
- The generative model is:
  \[
  \mathbf{s}_i \sim \mathcal{N}(\boldsymbol{\mu}(\boldsymbol{\theta}_i), \Sigma)
  \]
  where \(\boldsymbol{\mu}(\boldsymbol{\theta}_i)\) is a function mapping parameters to expected summary statistics, and \(\Sigma\) is the covariance of the summary statistics (estimated empirically from the simulations).

**b. Likelihood Construction**
- For each catalog, the likelihood of observing summary statistics \(\mathbf{s}_i\) given parameters \(\boldsymbol{\theta}_i\) is:
  \[
  \mathcal{L}_i = \mathcal{N}(\mathbf{s}_i \mid \boldsymbol{\mu}(\boldsymbol{\theta}_i), \Sigma)
  \]
- The joint likelihood over all catalogs is:
  \[
  \mathcal{L}_{\text{joint}} = \prod_{i=1}^N \mathcal{L}_i
  \]

**c. Emulator for \(\boldsymbol{\mu}(\boldsymbol{\theta})\)**
- Since \(\boldsymbol{\mu}(\boldsymbol{\theta})\) is not analytically known, train a regression emulator (e.g., Gaussian Process Regression, Random Forest, or Neural Network) to map from parameter space to summary statistics using the simulated catalogs.
- Use cross-validation to select the emulator with the best predictive performance and lowest bias.

---

#### 4. **Parameter Inference**

**a. Posterior Sampling**
- For a given set of observed or test summary statistics, infer the posterior distribution of parameters using the trained emulator and the hierarchical likelihood.
- Use Markov Chain Monte Carlo (MCMC) or Hamiltonian Monte Carlo (HMC) for posterior sampling, leveraging efficient libraries (e.g., emcee, PyMC, or Stan).

**b. Marginalization and Uncertainty Quantification**
- Marginalize over nuisance summary statistics and propagate emulator uncertainty into the posterior.
- Quantify parameter degeneracies by examining the joint and marginal posterior distributions.

---

#### 5. **Computational Implementation**

**a. Parallelization**
- All per-catalog summary statistic calculations and emulator training should be parallelized across the 8 available CPUs.
- Precompute and cache all summary statistics and PCA components to minimize repeated computation.

**b. Runtime Optimization**
- Limit the number of summary statistics and principal components to ensure that emulator training and posterior sampling complete within the 10-minute constraint.
- Use batch evaluation and vectorized operations for likelihood and posterior calculations.

**c. Validation**
- Perform posterior predictive checks by simulating new catalogs at inferred parameter values and comparing their summary statistics to the observed/test data.
- Assess emulator accuracy using held-out catalogs.

---

#### 6. **Mathematical Formulation**

- **Summary Statistic Model:**
  \[
  \mathbf{s}_i = f(\boldsymbol{\theta}_i) + \boldsymbol{\epsilon}_i, \quad \boldsymbol{\epsilon}_i \sim \mathcal{N}(0, \Sigma)
  \]
  where \(f\) is the trained emulator.

- **Posterior:**
  \[
  p(\boldsymbol{\theta} \mid \mathbf{s}) \propto \mathcal{N}(\mathbf{s} \mid f(\boldsymbol{\theta}), \Sigma) \; p(\boldsymbol{\theta})
  \]
  where \(p(\boldsymbol{\theta})\) is the prior over parameters (uniform or informed by simulation design).

---

#### 7. **Actionable Steps for Implementation**

1. **Compute and standardize summary statistics and principal components for all catalogs.**
2. **Train an emulator to map parameters to summary statistics using the simulation grid.**
3. **Construct the hierarchical likelihood using the empirical covariance of summary statistics.**
4. **For new data or test catalogs, use the emulator and likelihood to sample the posterior over parameters.**
5. **Validate inference by comparing posterior predictive summaries to actual catalog statistics.**
6. **Document all code, parameter choices, and runtime performance for reproducibility.**

---

This methodology ensures robust, efficient, and interpretable inference of cosmological and feedback parameters from multi-scale galaxy statistics, leveraging the full information content of the simulated catalogs while respecting computational constraints.