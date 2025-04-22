### Methodology for Identifying Feedback Parameter Thresholds for Star Formation Quenching in Massive Galaxies

#### 1. Data Preparation and Selection

- **Data Loading:**  
  Load the full galaxy-level DataFrame (`galaxies_full_optimal.parquet`) and the catalog-level DataFrame (`catalog_params_optimal.parquet`). The galaxy-level DataFrame contains all necessary galaxy properties and associated feedback/cosmological parameters for each galaxy.

- **Selection of Massive Galaxies:**  
  Restrict the analysis to galaxies with stellar mass \( M_\mathrm{star} > 10^{10} M_\odot \), as this regime is where AGN feedback is theoretically expected to dominate quenching. This cut yields a robust sample (127,720 galaxies) with a wide range of feedback parameters.

#### 2. Definition and Identification of Quenched Galaxies

- **Operational Definition:**  
  Define a galaxy as "quenched" if its specific star formation rate (sSFR = SFR / \( M_\mathrm{star} \)) is below a threshold. Use sSFR \( < 10^{-11} \) yr\(^{-1}\) as the primary criterion, but verify this threshold by inspecting the sSFR distribution to ensure a clear separation between star-forming and quenched populations.

- **Controlling for SFR–Mass Correlation:**  
  Since the SFR–stellar mass correlation is weak (\( r=0.10 \)), sSFR is an appropriate metric. However, as a robustness check, repeat the analysis using alternative sSFR thresholds and, if necessary, mass-dependent sSFR cuts to ensure results are not sensitive to the precise definition.

#### 3. Integration of Catalog-Level and Galaxy-Level Data

- **Parameter Assignment:**  
  Each galaxy row already contains the relevant feedback and cosmological parameters from its parent catalog. No further merging is required, but verify consistency by cross-checking catalog indices.

#### 4. Statistical Analysis Workflow

- **Binning and Visualization:**  
  - Bin the massive galaxy sample by each feedback parameter (\( A_\mathrm{AGN1} \), \( A_\mathrm{AGN2} \), \( A_\mathrm{SN1} \), \( A_\mathrm{SN2} \)), using 5–10 bins per parameter, ensuring sufficient galaxies per bin for statistical robustness.
  - For each bin, compute the quenched fraction (number of quenched galaxies divided by total galaxies in the bin).
  - Visualize the quenched fraction as a function of each feedback parameter to identify potential threshold behavior (e.g., a sharp rise in quenched fraction above a certain parameter value).

- **Threshold Identification:**  
  - Apply change-point detection or piecewise linear regression to the quenched fraction vs. feedback parameter curves to quantitatively estimate threshold values where quenching becomes efficient.
  - Use bootstrapping to estimate uncertainties on threshold locations.

- **Regression and Partial Correlation Analysis:**  
  - Fit logistic regression models predicting the probability of quenching as a function of all four feedback parameters, controlling for stellar mass, black hole mass, and cosmological parameters (\( \Omega_m \), \( \sigma_8 \)).
  - Compute partial correlation coefficients between each feedback parameter and quenching status, controlling for the other parameters, to assess the independent effect of AGN vs. SN feedback.

- **Relative Importance by Mass Regime:**  
  - Repeat the above analyses in sub-bins of stellar mass (e.g., \( 10^{10}–10^{11} M_\odot \), \( >10^{11} M_\odot \)) to test whether the importance of AGN vs. SN feedback varies with mass.
  - Compare the effect sizes and threshold locations for AGN and SN feedback parameters in each mass regime.

#### 5. Justification of Methodological Choices

- The use of sSFR and a fixed threshold is justified by the weak SFR–mass correlation and the clear bimodality in sSFR distributions observed in both simulations and real data.
- Binning and visualization are essential for identifying non-linear or threshold-like behavior, which is expected for feedback-driven quenching.
- Regression and partial correlation analyses allow for disentangling the effects of multiple, potentially correlated feedback and cosmological parameters.
- Bootstrapping and change-point detection provide quantitative, uncertainty-aware estimates of feedback thresholds.

#### 6. Summary of Workflow

1. Select massive galaxies (\( M_\mathrm{star} > 10^{10} M_\odot \)).
2. Define quenched galaxies using sSFR threshold.
3. Bin galaxies by feedback parameters and compute quenched fractions.
4. Visualize and statistically identify feedback thresholds.
5. Use regression and partial correlation to assess the independent effects of AGN and SN feedback.
6. Repeat analyses in different mass regimes to probe the mass dependence of feedback effects.

This methodology provides a comprehensive, statistically robust framework for quantifying the feedback parameter thresholds that drive star formation quenching in massive galaxies, leveraging the rich structure and parameter coverage of the simulation dataset.