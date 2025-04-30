### Methodology for Quantifying the Dependence of Black Hole–Galaxy Scaling Relations on Feedback and Cosmological Parameters

#### 1. Data Preparation and Integration

- **Data Loading:**  
  Load the galaxy-level DataFrame (`galaxies_full_optimal.parquet`) and the catalog-level DataFrame (`catalog_params_optimal.parquet`) using efficient I/O routines.

- **Galaxy Selection:**  
  Filter the galaxy-level data to include only galaxies with non-zero black hole mass (\( M_\mathrm{BH} > 0 \)), as motivated by the EDA and physical considerations.

- **Stellar Mass Binning:**  
  Assign each galaxy to one of three stellar mass bins:
  - Low: \( M_\mathrm{star} < 10^9\,M_\odot \)
  - Intermediate: \( 10^9 \leq M_\mathrm{star} < 10^{10}\,M_\odot \)
  - High: \( M_\mathrm{star} \geq 10^{10}\,M_\odot \)

- **Data Merging:**  
  Ensure that each galaxy is associated with its parent catalog’s cosmological and feedback parameters, either by using the columns already present in the galaxy DataFrame or by merging with the catalog-level DataFrame on `catalog_number`.

#### 2. Per-Catalog Scaling Relation Fitting

- **Catalog-wise Analysis:**  
  For each of the 1,000 catalogs:
  - Select all galaxies belonging to the catalog and with \( M_\mathrm{BH} > 0 \).
  - For each stellar mass bin, fit the following scaling relations:
    - \( \log_{10} M_\mathrm{BH} = \alpha + \beta \log_{10} M_\mathrm{star} + \epsilon \)
    - \( \log_{10} M_\mathrm{BH} = \alpha' + \beta' \log_{10} \sigma_v + \epsilon' \)
  - Use ordinary least squares (OLS) linear regression in log–log space to estimate the slope (\( \beta \)), intercept (\( \alpha \)), and intrinsic scatter (\( \sigma_\mathrm{int} \)), where scatter is defined as the standard deviation of the residuals.
  - If the number of galaxies in a bin is below a minimum threshold (e.g., 20), skip the fit for that bin to avoid unreliable estimates.

- **Parallelization:**  
  Distribute the per-catalog fitting tasks across the available 8 CPUs using multiprocessing or joblib, ensuring that each process handles a subset of catalogs. This approach keeps each calculation well within the 10-minute runtime constraint.

#### 3. Construction of the Catalog-Level Summary Table

- **Summary Table:**  
  For each catalog and each stellar mass bin, record:
  - Best-fit slope, intercept, and scatter for both \( M_\mathrm{BH} \)–\( M_\mathrm{star} \) and \( M_\mathrm{BH} \)–\( \sigma_v \) relations.
  - The catalog’s cosmological and feedback parameters (\( \Omega_m, \sigma_8, A_\mathrm{SN1}, A_\mathrm{SN2}, A_\mathrm{AGN1}, A_\mathrm{AGN2} \)).
  - The number of galaxies used in each fit.

- **Data Structure:**  
  The resulting summary table will have one row per (catalog, mass bin) combination, with columns for all fit parameters and catalog-level parameters.

#### 4. Quantifying Parameter Dependence

- **Exploratory Visualization:**  
  - Plot the distribution of best-fit slopes, intercepts, and scatter as a function of each cosmological and feedback parameter, for each mass bin.
  - Use scatter plots, violin plots, and heatmaps to visually assess trends and correlations.

- **Statistical Analysis:**
  - **Partial Correlation Analysis:**  
    Compute partial correlation coefficients between each scaling relation parameter (slope, intercept, scatter) and each cosmological/feedback parameter, controlling for the others. This helps disentangle the effects of correlated parameters.
  - **Multivariate Regression:**  
    Fit linear models of the form:
    \[
    \text{Slope} = c_0 + c_1 \Omega_m + c_2 \sigma_8 + c_3 A_\mathrm{SN1} + c_4 A_\mathrm{SN2} + c_5 A_\mathrm{AGN1} + c_6 A_\mathrm{AGN2} + \epsilon
    \]
    and similarly for intercept and scatter, for each mass bin and scaling relation.
    - Use standardized coefficients to compare the relative importance of each parameter.
    - Assess statistical significance and goodness-of-fit.
  - **Feature Importance (Machine Learning):**  
    As a complementary approach, use random forest regression or gradient boosting to predict the slope/intercept/scatter from the six catalog parameters. Extract feature importances to quantify the relative influence of cosmology versus feedback.
    - Use cross-validation to ensure robustness.
    - Restrict tree depth and number of estimators to maintain computational efficiency.

- **Nonlinear Effects:**  
  If strong nonlinearities are observed, consider fitting polynomial or interaction terms, or use kernel-based methods, but only if justified by initial results and computationally feasible.

#### 5. Results Summarization

- **Tables and Figures:**  
  - Present tables of mean and standard deviation of slopes, intercepts, and scatter as a function of each parameter (binned or continuous).
  - Provide summary plots showing the dependence of scaling relation parameters on cosmological and feedback parameters, for each mass bin.
  - Highlight the most influential parameters as determined by regression coefficients and feature importances.

- **Key Statistics:**  
  - Report the range and typical values of slopes and scatter across the parameter space.
  - Quantify the fraction of variance in scaling relation parameters explained by cosmology versus feedback.

#### 6. Computational Considerations

- **Batch Processing:**  
  - If memory or runtime becomes limiting, process catalogs in batches (e.g., 100 at a time), aggregating results after each batch.

- **Catalog Sampling (if needed):**  
  - For initial tests or if full-sample analysis is infeasible, select a stratified random sample of catalogs that span the full range of cosmological and feedback parameters.

- **Efficient Storage:**  
  - Store intermediate and final results in compressed, columnar formats (e.g., Parquet) to facilitate rapid access and downstream analysis.

#### 7. Reproducibility and Robustness

- **Code Modularity:**  
  - Structure the analysis pipeline so that each step (data loading, fitting, summary, regression) can be rerun independently.

- **Validation:**  
  - Perform sanity checks by comparing aggregate scaling relations (across all catalogs) to those in the literature and to the EDA results.
  - Test the sensitivity of results to binning choices and fitting thresholds.

---

This methodology ensures a rigorous, efficient, and interpretable quantification of how black hole–galaxy scaling relations depend on cosmological and feedback parameters, leveraging the statistical power and parameter coverage of the CAMELS dataset while respecting computational constraints.