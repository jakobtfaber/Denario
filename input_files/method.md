# Detailed Methodology for Probing Primordial Non-Gaussianity Using CAMELS Datasets

This document outlines the precise steps, techniques, and rationale for the analysis of group and subhalo properties in two CAMELS datasets—one with fNL=200 and the other with fNL=-200. We will focus on comparing the mass distributions and structural properties of galaxy groups, with special emphasis on the high-mass tail of the halo mass function.

## 1. Data Loading and Quality Inspection

- **Dataset Retrieval:**  
  We load the four datasets (groups and subhalos for both A and B) using the provided pickle files. Each dataset is thoroughly checked for completeness. The key features (GroupSFR, Group_R_Mean200, Group_M_Mean200) and subhalo attributes (e.g., SubhaloMass, SubhaloSFR, SubhaloSpinMod, SubhaloVmax) are examined for null values and consistency.

- **Inspection Outputs:**  
  Descriptive statistics (mean, standard deviation, min, max, quartiles) for each group feature are generated. For instance, the summary of Group_M_Mean200 shows mean values around 10.79 and 10.74 for Datasets A and B, respectively, with similar spread. These outputs confirm that the datasets are reliable and require no missing-value imputation or outlier removal.

## 2. Distribution Analysis of Group Mass and Radius

- **Histogram and CDF Visualization:**  
  Overlaid histograms and cumulative distribution functions (CDFs) are created for Group_M_Mean200 using a logarithmic x-scale due to the wide dynamic range. These plots facilitate a visual comparison of the full mass distributions between the datasets.  
  - **Key Observation:** The central statistical properties (mean, median) of the two distributions are nearly identical.
  
- **Statistical Testing:**  
  To quantitatively compare the distributions, we employ:
  - **Anderson-Darling k-sample Test:** Sensitive to tail behavior, which returned a capped p-value (~0.250) for Group_M_Mean200.
  - **Cramér-von Mises Test:** Provided a test statistic with a p-value approximately 0.886.
  
  Both tests indicate no statistically significant difference between the full distributions of the two datasets.

## 3. Filtering and Tail Modeling

- **High-Mass Tail Isolation:**  
  We define the high-mass tail as those groups with Group_M_Mean200 values exceeding the 95th percentile.  
  - **Parameter:** For Dataset A, the threshold is approximately 18.097 (in 1e10 Msun/h units) and for Dataset B about 18.273.
  - **Sample Size:** This filtering selects roughly 2,200 groups per dataset.

- **Fitting the High-Mass Tail:**  
  To characterize the tail behavior, we fit a power-law model of the form:
  
  f(x) = A · x^(–α)
  
  - **Fitting Procedure:**  
    - The histogram for the tail data is computed using logarithmically spaced bins between the minimum and maximum tail values.
    - A non-linear least-squares fit (using SciPy's `curve_fit`) is performed in log-log space, with an initial guess of A equal to the maximum histogram count and α set to 2.0.
    - **Result Parameters:**  
      The fits yield nearly identical parameters for both datasets (e.g., A ≈ 8.32e+03 for A and 8.55e+03 for B, with α ≈ 0.851 and 0.854, respectively).

## 4. Analysis of Structural Properties

- **Mass-to-Radius Ratio:**  
  We compute the ratio Group_M_Mean200 / Group_R_Mean200 for every group.  
  - **Outcome:**  
    The histograms of the mass-to-radius ratios are nearly identical between the two datasets, which reinforces that the large-scale structural attributes (such as halo concentration) remain consistent.

- **Regression Analysis:**  
  Linear regression is performed with Group_R_Mean200 as the dependent variable and Group_M_Mean200 as the independent variable.  
  - **Method:**  
    A simple least-squares fit (using NumPy’s `polyfit`) is used to determine the slope and intercept.  
  - **Results:**  
    Both datasets yield almost identical regression parameters (e.g., slope ≈ 0.1487 for Dataset A vs. ≈ 0.1515 for Dataset B; intercepts around 67.5–67.6). This similarity confirms that the correlation between group mass and physical scale is robust across different fNL setups.

## 5. Addressing Potential Systematic Biases

- **Consistent Data Processing:**  
  The same filtering criteria (95th percentile) and the same feature transformations (logarithmic scaling for visualization and fitting) are applied to both datasets. This uniform treatment minimizes processing biases.
  
- **Robust Statistical Methods:**  
  Using two independent statistical tests (Anderson-Darling and Cramér-von Mises) for comparing distributions and employing regression analysis ensures that subtle differences are not masked by methodology inconsistencies.

## 6. Workflow Summary

1. **Data Preparation:**  
   Load datasets and perform quality checks to validate completeness and consistency.

2. **Visual and Statistical Comparison:**  
   - Create histograms and CDFs for Group_M_Mean200.
   - Apply Anderson-Darling and Cramér-von Mises tests to assess overall distribution differences.

3. **High-Mass Tail Extraction and Modeling:**  
   - Filter groups with Group_M_Mean200 above the 95th percentile.
   - Fit the high-mass tail using a power-law model in logarithmic bins (parameter range determined by the minimum and maximum of the tail sample).
   - Record fitted parameters (A and α) for direct comparison.

4. **Structural Analysis:**  
   - Compute the mass-to-radius ratio and compare distributions.
   - Perform regression analysis (Group_R_Mean200 vs. Group_M_Mean200) to quantify the relationship between mass and group size.

5. **Subhalo Analysis (Conditional):**  
   - If a linking column such as ‘id’ exists, extract corresponding subhalo properties for groups in the high-mass tail for further comparison.
   - In our current datasets, this step is skipped due to the absence of an 'id' column.

By adhering to this methodology, we ensure that all comparisons between the two CAMELS datasets are carried out with consistency and high statistical rigor. The similar outcomes across key tests and analyses reinforce that any potential differences due to primordial non-Gaussianity are subtle and require sensitive, well-controlled methods.