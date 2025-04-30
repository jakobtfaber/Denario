### Methodology for Quantifying Quenching Efficiency Across Feedback and Cosmological Parameter Space

#### 1. Data Preparation and Feature Engineering

- **Data Loading:**  
  Load the full galaxy-level DataFrame (`galaxies_full_optimal.parquet`) and the catalog-level DataFrame (`catalog_params_optimal.parquet`) using efficient, chunked reading if necessary to manage memory.
- **Feature Calculation:**  
  Compute the specific star formation rate (sSFR = SFR / M_star) for each galaxy.
- **Quenched Classification:**  
  Assign a binary flag to each galaxy: quenched if sSFR < 10^(-11) yr^(-1), star-forming otherwise.
- **Merging Catalog Parameters:**  
  Ensure each galaxy row is associated with its catalog’s feedback and cosmological parameters, using the catalog_number as the join key.

#### 2. Binning Strategy

- **Stellar Mass Bins:**  
  Use three bins, as established in the EDA:
  - Low: M_star < 10^9 M_☉
  - Intermediate: 10^9 ≤ M_star < 10^(10) M_☉
  - High: M_star ≥ 10^(10) M_☉
- **Catalog Parameter Binning:**  
  For visualization and some analyses, bin feedback and cosmological parameters into quantiles (e.g., quartiles or quintiles) to ensure roughly equal numbers of catalogs per bin. For regression analyses, use the raw (continuous) parameter values.
- **Additional Binning (if needed):**  
  For robustness checks, consider finer mass bins or SFR bins, but ensure sufficient galaxy counts per bin to maintain statistical power.

#### 3. Calculation of Quenching Metrics

- **Quenched Fraction (f_Q):**  
  For each catalog and stellar mass bin, compute the fraction of galaxies classified as quenched.
- **Median sSFR:**  
  Calculate the median sSFR in each mass bin and catalog.
- **Suppression Factor:**  
  For each catalog and mass bin, compute the ratio of the median sSFR to the global median at that mass.

#### 4. Statistical Analysis

**A. Univariate Trends and Visualization**
- Plot the quenched fraction as a function of each feedback and cosmological parameter, for each mass bin.
- Use binned parameter values (e.g., quartiles) to visualize trends and assess monotonicity.

**B. Multivariate Regression Analysis**
- **Model Specification:**  
  Fit generalized linear models (GLMs) or logistic regression models to predict the quenched fraction (or probability of quenching for individual galaxies) as a function of:
    - Feedback parameters: A_SN1, A_SN2, A_AGN1, A_AGN2
    - Cosmological parameters: Omega_m, sigma_8
    - Stellar mass (as a categorical or continuous variable)
- **Model Formulation:**  
  For catalog-level analysis (preferred for computational efficiency), use:
  f_Q = β_0 + β_1 A_SN1 + β_2 A_SN2 + β_3 A_AGN1 + β_4 A_AGN2 + β_5 Omega_m + β_6 sigma_8 + ε
  Fit separate models for each mass bin.
- **Partial Correlation Analysis:**  
  Compute partial correlations between each parameter and the quenched fraction, controlling for stellar mass and other parameters, to disentangle their independent effects.

**C. Interaction Effects**
- Test for interaction terms between feedback and cosmological parameters (e.g., A_AGN1 × Omega_m) to assess whether the impact of feedback depends on cosmological context.

**D. Effect Size and Significance**
- **Effect Size Metrics:**  
  Report standardized regression coefficients and odds ratios (for logistic models) to quantify the strength of each parameter’s effect.
- **Statistical Significance:**  
  Use a significance threshold of p < 0.01 (Bonferroni-corrected for multiple comparisons if needed). Report confidence intervals for all key coefficients.

#### 5. Handling Confounding Variables

- **Stellar Mass Control:**  
  All analyses are stratified by stellar mass bin to control for the strong mass dependence of quenching.
- **Environmental Proxies:**  
  As a robustness check, repeat analyses including proxies for environment (e.g., total mass, velocity dispersion) as additional covariates.
- **Catalog Size Normalization:**  
  Weight catalog-level statistics by the number of galaxies per catalog to avoid bias from catalogs with few galaxies.

#### 6. Computational Strategy

- **Parallelization:**  
  Exploit the 8 available CPUs by parallelizing:
    - Per-mass-bin analyses (each mass bin can be processed independently)
    - Per-catalog computations (e.g., calculating quenched fractions)
    - Bootstrapping or permutation tests (if used for uncertainty estimation)
- **Chunked Processing:**  
  For memory efficiency, process the galaxy DataFrame in chunks when computing sSFR and quenched flags.
- **Runtime Management:**  
  Limit the number of regression models and the complexity of interaction terms to ensure each computation completes within 10 minutes. For exploratory analyses, use random subsampling (e.g., 10–20% of catalogs) to validate trends before running on the full dataset.

#### 7. Interpretation and Reporting

- **Parameter Impact:**  
  Interpret the sign, magnitude, and significance of each feedback and cosmological parameter’s effect on quenching, both in isolation and after controlling for confounders.
- **Visualization:**  
  Present heatmaps and contour plots of quenched fraction as a function of two parameters at a time (e.g., A_AGN1 vs. A_SN1), stratified by mass bin.
- **Summary Statistics:**  
  Report the range and distribution of quenched fractions across the parameter space, highlighting regions of particularly efficient or inefficient quenching.
- **Robustness Checks:**  
  Compare results using alternative quenching definitions (e.g., main sequence offset) and including environmental proxies.

#### 8. Justification of Methodological Choices

- The binning strategy and quenching threshold are based on the EDA, which shows clear mass dependence and a broad sSFR distribution.
- Regression and partial correlation analyses are chosen to disentangle the effects of correlated parameters and to quantify independent contributions.
- The use of catalog-level statistics (rather than individual galaxies) for regression is motivated by computational efficiency and the structure of the data.
- Parallelization and chunked processing are essential to meet computational constraints given the dataset size.

---

This methodology provides a rigorous, statistically robust framework for mapping the efficiency of star formation quenching across the multidimensional space of feedback and cosmological parameters in the CAMELS simulations, while fully leveraging the dataset’s richness and controlling for key confounders.