# Results

This section presents the findings from the Data Envelopment Analysis (DEA) of U.S. Assisted Reproductive Technology (ART) clinics, utilizing data from 2020 to 2022. The analysis focuses on the technical efficiency of clinics in converting intended egg retrievals from own-egg cycles into live births, stratified by patient age group.

## Dataset and DEA Input-Output Specification

The analysis utilized the CDC’s National ART Surveillance System (NASS) Final ART Success Rates dataset, specifically for reporting years 2020, 2021, and 2022. Data were filtered to include only cycles where patients used their own eggs. The primary metric for constructing DEA variables was "What percentage of intended egg retrievals resulted in live-birth deliveries?", stratified by "Age of Patient" (`<35`, `35-37`, `38-40`, `>40`).

Each Decision Making Unit (DMU) in this study represents a unique combination of a clinic, reporting year, and patient age group. The DEA model employed was an input-oriented Banker, Charnes, Cooper (BCC-I) model, which assumes variable returns to scale (VRS). The single input and output were defined as:
*   **Input (X):** `Input_IntendedRetrievals` – The number of intended egg retrieval cycles reported by the clinic for a specific year and age group.
*   **Output (Y):** `Output_LiveBirths` – The number of live births resulting from these intended retrievals, calculated by multiplying the reported percentage of live births per intended retrieval (`Data_Value_num`) by the `Input_IntendedRetrievals` (`Cycle_Count`) and rounding to the nearest whole number.

After initial loading of 1,126,080 records, filtering for the specified years, "Patients using their own eggs" type, the relevant question, and age breakout category yielded 48,960 records. Subsequent cleaning for DEA requirements (positive inputs, valid outputs) and removal of 36 records corresponding to national summary data (ClinicId 9999) resulted in a final dataset of 31,164 DMUs for analysis. This prepared dataset is stored in `data/dea_analysis_results/eda_outputs/prepared_dea_input_output_data.csv`.

## Descriptive Analysis of DEA Inputs and Outputs

An exploratory data analysis (EDA) was conducted on the prepared dataset (excluding national data) to understand the characteristics of the DMUs. The detailed summary statistics for each stratum (Year, AgeGroup) are available in `data/dea_analysis_results/eda_outputs/eda_summary_statistics_by_stratum.csv`.

**Number of DMUs:** The dataset provided a substantial number of DMUs for each stratum. For instance, in 2020, the number of DMUs ranged from 2,464 for the `>40` age group to 2,752 for the `<35` age group. Similar counts were observed for 2021 and 2022, ensuring a robust basis for DEA within each stratum.

**Input: Intended Retrievals (`Input_IntendedRetrievals`)
The number of intended retrievals (IR) per DMU varied considerably.
*   **Central Tendency and Dispersion:** Mean IR values showed a tendency to increase slightly over the three-year period for most age groups. For example, in the `<35` age group, mean IR was 113.2 in 2020, 111.7 in 2021, and 133.8 in 2022. Median IR values were consistently lower than their respective means across all strata (e.g., for `<35` in 2020: median IR 43.0, mean IR 113.2). This, coupled with large standard deviations (e.g., 269.9 for `<35` in 2020) and high maximum values (e.g., 5021 cycles for a DMU in the `<35` group in 2020), indicates a significant right-skewness in the distribution of intended retrievals.
*   **Visualizations:** This skewness is visually confirmed by the histograms presented in `data/dea_analysis_results/eda_outputs/histograms_input_intendedretrievals_1_*.png`, which show a large number of DMUs with fewer retrievals and a long tail representing DMUs with many retrievals. The boxplots in `data/dea_analysis_results/eda_outputs/boxplots_input_intendedretrievals_4_*.png` further illustrate this, highlighting numerous outliers at the higher end of the distribution for each stratum.

**Output: Live Births (`Output_LiveBirths`)
The number of live births (LB) also exhibited wide variation and skewness.
*   **Central Tendency and Dispersion:** Mean LB generally followed trends similar to inputs, with slight increases over the years for younger age groups. For the `<35` group, mean LB was 47.2 in 2020, 46.0 in 2021, and 54.6 in 2022. A critical observation is that median LB values were frequently 0.0, particularly for older age groups. For instance, the `>40` age group reported a median LB of 0.0 across all three years. This indicates that at least half of the DMUs in these strata reported zero live births for the specific metric analyzed.
*   **Visualizations:** The distributions of live births were also highly right-skewed, as depicted in the histograms (`data/dea_analysis_results/eda_outputs/histograms_output_livebirths_2_*.png`) and boxplots (`data/dea_analysis_results/eda_outputs/boxplots_output_livebirths_5_*.png`).

**Live Birth Rate per Intended Retrieval (`Data_Value_num`)
The original reported live birth rate (LBRate) per intended retrieval, which was used to calculate the `Output_LiveBirths`, showed expected trends with age.
*   **Central Tendency and Age-Related Trends:** Mean LBRate was highest for the `<35` age group (e.g., 22.46% in 2020) and systematically decreased with increasing patient age, reaching as low as 1.95% for the `>40` age group in 2020. Median LBRates were also frequently 0.0%, especially for the `35-37`, `38-40`, and `>40` age groups across all years. This reinforces the finding that a substantial proportion of DMUs reported no successful live births.
*   **Visualizations:** Histograms (`data/dea_analysis_results/eda_outputs/histograms_data_value_num_3_*.png`) show a high concentration of LBRates at or near zero for older age groups. For the `<35` group, the distribution was more dispersed but still skewed. Boxplots (`data/dea_analysis_results/eda_outputs/boxplots_data_value_num_6_*.png`) clearly illustrate the declining trend in LBRate with increasing patient age and the prevalence of zero values.

The high incidence of zero live births and, consequently, zero live birth rates, particularly in older patient age groups, is a notable characteristic of the input data for DEA and is anticipated to significantly influence the efficiency scores.

## Clinic Efficiency Scores

The BCC-I DEA model yielded efficiency scores for 31,164 DMUs, stored in `data/dea_analysis_results/dea_scores/clinic_efficiency_scores.csv`. An efficiency score of 1.0 signifies that a DMU operates on the efficiency frontier (representing best practice within its stratum), while scores below 1.0 indicate relative inefficiency.

The aggregate statistics for all calculated efficiency scores are: mean = 0.2488, median = 0.1000, standard deviation = 0.2804, minimum = 0.0004, and maximum = 1.0000. The low mean and median scores suggest that, on average, DMUs operated considerably below the efficiency frontier established by their peers. No NaN scores were encountered, indicating successful computation for all DMUs.

### Stratum-Specific Efficiency Score Analysis

A detailed breakdown of efficiency scores by year and age group is provided in Table 1 (derived from `data/dea_analysis_results/dea_scores/efficiency_score_summary_by_stratum.csv`).

**Table 1: Summary of DEA Efficiency Scores by Year and Patient Age Group**
*(This table would be a formatted version of the content from `efficiency_score_summary_by_stratum.csv`)*
| Year | Age Group | Num DMUs | Mean Efficiency | Median Efficiency | Min Efficiency | Max Efficiency | Std Efficiency | Num Efficient (Score ≥ 0.9999) | % Efficient |
|------|-----------|----------|-----------------|-------------------|----------------|----------------|----------------|------------------------------------|---------------|
| 2020 | <35       | 2752     | 0.3434          | 0.2500            | 0.0007         | 1.0            | 0.3161         | 100                                | 3.63%         |
| 2020 | 35-37     | 2548     | 0.2577          | 0.0769            | 0.0013         | 1.0            | 0.2921         | 123                                | 4.83%         |
| 2020 | 38-40     | 2524     | 0.2139          | 0.0807            | 0.0013         | 1.0            | 0.2585         | 124                                | 4.91%         |
| 2020 | >40       | 2464     | 0.1859          | 0.0833            | 0.0018         | 1.0            | 0.2458         | 130                                | 5.28%         |
| 2021 | <35       | 2720     | 0.3247          | 0.2000            | 0.0004         | 1.0            | 0.3040         | 81                                 | 2.98%         |
| 2021 | 35-37     | 2496     | 0.2504          | 0.0769            | 0.0004         | 1.0            | 0.2851         | 108                                | 4.33%         |
| 2021 | 38-40     | 2491     | 0.2171          | 0.0833            | 0.0004         | 1.0            | 0.2537         | 95                                 | 3.81%         |
| 2021 | >40       | 2441     | 0.1783          | 0.0769            | 0.0004         | 1.0            | 0.2386         | 117                                | 4.79%         |
| 2022 | <35       | 2849     | 0.3188          | 0.2500            | 0.0025         | 1.0            | 0.2934         | 65                                 | 2.28%         |
| 2022 | 35-37     | 2699     | 0.2612          | 0.1000            | 0.0004         | 1.0            | 0.2835         | 98                                 | 3.63%         |
| 2022 | 38-40     | 2640     | 0.2353          | 0.1000            | 0.0004         | 1.0            | 0.2671         | 107                                | 4.05%         |
| 2022 | >40       | 2540     | 0.1719          | 0.0714            | 0.0004         | 1.0            | 0.2339         | 109                                | 4.29%         |

*   **Mean and Median Efficiency:** As shown in Table 1, mean efficiency scores were consistently low, generally ranging from approximately 0.17 (for `>40` age group in 2022) to 0.34 (for `<35` age group in 2020). Median efficiency scores were notably lower than the means, particularly for older age groups (e.g., 0.0714 for `>40` in 2022), indicating a right-skewed distribution of efficiency scores within each stratum. This suggests that many DMUs exhibit low efficiency, while a smaller number achieve higher scores, thereby elevating the mean relative to the median.
*   **Percentage of Efficient DMUs:** The proportion of DMUs operating on the efficiency frontier (score ≥ 0.9999) was small across all strata, typically ranging between 2% and 5%. For example, in 2022, this percentage varied from 2.28% for the `<35` age group to 4.29% for the `>40` age group.

**Distribution Visualizations:**
*   The histograms of efficiency scores, available in `data/dea_analysis_results/dea_scores/plots/hist_efficiency_scores_1_*.png`, visually confirm the right-skewness. These plots typically show a high frequency of DMUs with low efficiency scores (near 0) and a smaller peak at an efficiency score of 1.0, representing the efficient DMUs.
*   The violin plots, found in `data/dea_analysis_results/dea_scores/plots/violin_efficiency_scores_2_*.png`, offer a more nuanced view of these distributions. They illustrate that for all age groups and years, the majority of the distribution density is concentrated at lower efficiency values, with a tail extending towards 1.0. The `<35` age group consistently displays a distribution that is somewhat shifted towards higher efficiency scores compared to older age groups, whose distributions are more heavily concentrated near zero.

## Temporal and Age-Group Trends in Efficiency

### Temporal Trends (2020-2022)
The analysis of efficiency score trends over the three-year period is summarized in `data/dea_analysis_results/dea_scores/temporal_efficiency_trends_by_agegroup.csv`. Figure 1 (derived from `data/dea_analysis_results/dea_scores/plots/plot_temporal_mean_efficiency_4_*.png`) illustrates the temporal trends in mean efficiency.

*(Insert Figure 1 here: Line plot of Mean Efficiency Scores over Years, for each Age Group. Caption: Figure 1. Temporal Trend of Mean Efficiency Scores by Patient Age Group (2020-2022). Data sourced from `plot_temporal_mean_efficiency_4_*.png`.)*

*   **Mean Efficiency Trends:**
    *   For the `<35` age group, mean efficiency exhibited a slight decline from 0.343 in 2020 to 0.325 in 2021, and further to 0.319 in 2022.
    *   The `35-37` age group showed relative stability in mean efficiency: 0.258 (2020), 0.250 (2021), and 0.261 (2022).
    *   The `38-40` age group experienced a modest increase in mean efficiency, from 0.214 in 2020 to 0.217 in 2021, and then to 0.235 in 2022.
    *   For the `>40` age group, mean efficiency slightly decreased from 0.186 in 2020 to 0.178 in 2021, and then to 0.172 in 2022.
    These year-over-year changes in mean efficiency were generally minor, suggesting no substantial widespread shifts in overall clinic efficiency during the observed period.
*   **Median Efficiency Trends:** Median efficiency scores also showed varied but generally minor changes. For the `<35` age group, median efficiency was 0.250 in 2020, 0.200 in 2021, and 0.250 in 2022. The `35-37` and `38-40` age groups saw slight increases in median efficiency by 2022, while the `>40` age group's median remained low and showed a slight decrease. Overall, median efficiencies remained low, indicating that the typical DMU's performance relative to the frontier did not change dramatically.

### Age-Group Trends in Efficiency
A consistent pattern was observed regarding the relationship between patient age group and clinic efficiency across all three years:
*   **Higher Efficiency in Younger Age Groups:** DMUs associated with patients in the `<35` age group consistently demonstrated the highest mean and median efficiency scores (Table 1, `violin_efficiency_scores_2_*.png`).
*   **Decreasing Efficiency with Age:** As patient age increased through the `35-37`, `38-40`, and `>40` categories, both mean and median efficiency scores generally decreased. The `>40` age group consistently exhibited the lowest average efficiency scores. This trend is clearly visible in the violin plots (`violin_efficiency_scores_2_*.png`), where the distributions for older age groups are more compressed towards lower efficiency values. This pattern suggests that achieving high relative efficiency is more challenging, or performance is more variable, in older patient populations, even when compared against peers treating the same age group.

## Impact of Zero Live Births on Efficiency (Sensitivity Analysis)

A sensitivity analysis was performed to assess the impact of DMUs reporting zero live births (`Output_LiveBirths = 0`) on their efficiency scores. The findings are summarized in `data/dea_analysis_results/dea_scores/sensitivity_analysis_zero_outputs_summary.csv` and visualized in Figure 2 (derived from `data/dea_analysis_results/dea_scores/plots/violin_sensitivity_zero_outputs_3_*.png`).

*(Insert Figure 2 here: Violin plots comparing Efficiency Scores for DMUs with Zero vs. Positive Live Births, by Year and Age Group. Caption: Figure 2. Distribution of Efficiency Scores for DMUs with Zero Live Births vs. Positive Live Births, Stratified by Year and Patient Age Group. Data sourced from `violin_sensitivity_zero_outputs_3_*.png`.)*

*   **Significant Efficiency Discrepancy:** A pronounced difference in efficiency scores was observed between DMUs with zero live births and those with at least one live birth.
    *   DMUs reporting **zero live births** consistently had very low mean and median efficiency scores across all strata. For example, in 2020 for the `35-37` age group, DMUs with zero output had a mean efficiency of 0.139 and a median of 0.034, whereas DMUs with positive output had a mean efficiency of 0.503 and a median of 0.503. This pattern was consistent across all years and age groups.
    *   DMUs reporting **positive live births** had substantially higher mean and median efficiency scores. While these scores were still generally below 1.0 (indicating some relative inefficiency even among those achieving success), they were markedly greater than those of DMUs with no live births.
*   **Distributional Impact:** Figure 2 clearly shows that the efficiency score distributions for DMUs with zero live births are heavily concentrated at the lower end of the scale (near zero). In contrast, DMUs with positive live births exhibit distributions that, while still skewed, are shifted towards higher efficiency values.
*   **Interpretation:** This finding underscores that a primary driver of low efficiency scores in this dataset is the failure to achieve any live births from the intended retrieval cycles for a specific DMU. A DMU producing zero output from a non-zero input will inherently be assessed as inefficient by DEA, particularly when compared to peers achieving positive outputs.

## Benchmarking and Implications

The DEA results facilitate the identification of benchmark performance and highlights areas for potential improvement.
*   **Benchmarking Performance:** DMUs achieving an efficiency score of 1.0 (or ≥0.9999) are considered to be on the efficiency frontier, representing best practice within their stratum. As indicated in Table 1, the percentage of such fully efficient DMUs was consistently low (generally 2-5%), implying that a vast majority of DMUs operate below the observed benchmark.
*   **Performance Variation:** The wide distribution of efficiency scores and the low overall averages suggest significant heterogeneity in the performance of U.S. ART clinics concerning the conversion of intended retrievals into live births, even after accounting for patient age.
*   **Implications of Zero-Output Cases:** The profound impact of zero live births on efficiency scores suggests that a critical factor influencing a clinic's relative efficiency is its ability to achieve at least some level of success (i.e., at least one live birth) within a given age group and year. Addressing the underlying causes of zero-output cycles could be a key area for improving overall efficiency metrics.

In summary, the DEA of U.S. ART clinics from 2020-2022 reveals generally low technical efficiency, with significant variation influenced by patient age and, critically, by whether any live births were achieved. Younger patient age groups are associated with higher efficiency scores. Temporal changes in efficiency were modest over the study period. A small fraction of clinics consistently operate on the efficiency frontier, indicating substantial opportunities for performance improvement across the sector.