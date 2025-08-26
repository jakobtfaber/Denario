This document outlines the methodology for assessing the relative technical efficiency of U.S. ART clinics using Data Envelopment Analysis (DEA) on the NASS dataset for the years 2020-2022, focusing on own-egg cycles and stratifying by patient age group.

**1. Project Setup and Environment Configuration**

1.1. **Library Imports**:
    Begin by importing the necessary Python libraries:
    *   `pandas` for data manipulation and analysis.
    *   `numpy` for numerical operations.
    *   `scipy.optimize.linprog` for solving the linear programming problems required by DEA.
    *   `multiprocessing` for parallelizing DEA computations.
    *   `os` for file path management.
    *   `logging` for tracking progress and issues.

1.2. **Path Definitions and Output Directories**:
    Define base paths for data input and output. Create directories for storing intermediate data, final results, and any generated plots (though plots are for your internal use and not for inclusion in this methods description). For example:
    *   `DATA_PATH = '/mnt/ceph/users/fvillaescusa/AstroPilot/Medicine/Fertility1/data/art_data_2020_2024.csv'`
    *   `OUTPUT_DIR = './dea_analysis_results/'`
    *   `EDA_DIR = os.path.join(OUTPUT_DIR, 'eda_outputs/')`
    *   `DEA_RESULTS_DIR = os.path.join(OUTPUT_DIR, 'dea_scores/')`
    Ensure these output directories are created if they don't exist.

1.3. **Logging Configuration**:
    Set up basic logging to monitor the script's execution, especially for long-running processes or parallel tasks. Log messages should indicate successful completion of steps or any errors encountered.

**2. Data Loading and Initial Inspection**

2.1. **Load Dataset**:
    Load the `art_data_2020_2024.csv` file into a pandas DataFrame.
    python
    # Example:
    # df_raw = pd.read_csv(DATA_PATH)
    # print("Data loaded successfully.")
    # print(f"Raw dataset shape: {df_raw.shape}")
    

2.2. **Initial Data Overview**:
    Perform a preliminary inspection of the raw data:
    *   Display the first few rows (`df_raw.head()`).
    *   Print the list of all column names (`df_raw.columns`).
    *   Examine data types of each column (`df_raw.info()`).
    *   Generate basic descriptive statistics for numerical columns (`df_raw.describe(include='all')`).
    *   Check for missing values across columns (`df_raw.isnull().sum()`).

**3. Data Preprocessing and Filtering for DEA**

The goal is to create a dataset where each row represents a Decision Making Unit (DMU) – a specific clinic, in a specific year, for a specific patient age group – with one input (Number of Intended Retrievals) and one output (Number of Live Births).

3.1. **Filter by Reporting Year**:
    Retain data only for the years 2020, 2021, and 2022.
    python
    # Example:
    # years_of_interest = [2020, 2021, 2022]
    # df = df_raw[df_raw['Year'].isin(years_of_interest)].copy()
    # print(f"Data filtered for years {years_of_interest}. Shape: {df.shape}")
    

3.2. **Filter for Own-Egg Cycles**:
    Filter the dataset to include only records pertaining to "patients using their own eggs." This will likely involve using the `Type` column. Verify the exact string value from the data. A common value might be 'Patients using their own eggs'.
    python
    # Example:
    # own_egg_type_string = "Patients using their own eggs" # Verify this exact string from data exploration
    # df = df[df['Type'] == own_egg_type_string].copy()
    # print(f"Data filtered for own-egg cycles. Shape: {df.shape}")
    

3.3. **Identify Relevant Metrics for DEA**:
    The DEA requires one input (Intended Retrieval Cycles) and one output (Live Births). These need to be extracted or calculated.
    *   **Patient Age Group**: This will be used for stratification. It's found in the `Breakout` column when `Breakout_Category` is 'Age group of patient' (or a similar string; verify this).
    *   **Metric Identification**: We need rows where the `Question` column describes "% Live Birth per Intended Retrieval". Let's call this `target_question_lb_rate`. The `Data_Value_num` column will provide this percentage, and the `Cycle_Count` column on the *same row* is assumed to be the number of intended retrieval cycles for which this rate applies. This `Cycle_Count` will serve as our DEA input.

    python
    # Example:
    # target_question_lb_rate = "% Live Births per Intended Retrieval" # Verify this exact string
    # age_breakout_category = "Age group of patient" # Verify this exact string
    #
    # df_metrics = df[
    #     (df['Question'].str.contains(target_question_lb_rate, case=False, na=False)) &
    #     (df['Breakout_Category'] == age_breakout_category)
    # ].copy()
    # print(f"Filtered for relevant metrics and age breakouts. Shape: {df_metrics.shape}")
    
    Ensure `Data_Value_num` and `Cycle_Count` are numeric. Convert if necessary, handling non-numeric placeholders. Values like '*' or '-' in `Data_Value` often mean data is suppressed or not applicable; these should become NaN in `Data_Value_num` or `Cycle_Count` if not already handled by the dataset's `Data_Value_num` column.

3.4. **Construct DEA Input and Output Variables**:
    For each unique `ClinicId`, `Year`, and `Breakout` (Age Group):
    *   **DEA Input (X)**: `Number_of_Intended_Retrievals`. This is the `Cycle_Count` from the filtered `df_metrics`.
    *   **DEA Output (Y)**: `Number_of_Live_Births`. This is calculated as:
        `(Data_Value_num / 100) * Cycle_Count`. `Data_Value_num` here is the "% Live Birth per Intended Retrieval".

    python
    # Example:
    # df_dea_data = df_metrics[['ClinicId', 'Year', 'Breakout', 'Cycle_Count', 'Data_Value_num', 'FacilityName']].copy()
    # df_dea_data.rename(columns={
    #     'Breakout': 'AgeGroup',
    #     'Cycle_Count': 'Input_IntendedRetrievals'
    # }, inplace=True)
    #
    # # Ensure Data_Value_num is percentage (e.g., 30 for 30%)
    # df_dea_data['Output_LiveBirths'] = (df_dea_data['Data_Value_num'] / 100) * df_dea_data['Input_IntendedRetrievals']
    # df_dea_data['Output_LiveBirths'] = df_dea_data['Output_LiveBirths'].round(0).astype(int) # Live births are counts
    # print("DEA input and output variables constructed.")
    

3.5. **Handle Missing or Invalid Data for DEA**:
    DEA requires positive values for inputs and outputs.
    *   Remove rows where `Input_IntendedRetrievals` is missing, zero, or non-positive.
    *   Remove rows where `Output_LiveBirths` is missing or negative (zero live births is a valid outcome but might require specific DEA model variants or can be problematic if all DMUs have zero output. For standard DEA, positive outputs are preferred. If many zeros, this needs careful consideration. For now, we allow zero outputs but not negative or NaN).
    *   Log the number of records removed at this stage.

    python
    # Example:
    # initial_rows = len(df_dea_data)
    # df_dea_data.dropna(subset=['Input_IntendedRetrievals', 'Output_LiveBirths'], inplace=True)
    # df_dea_data = df_dea_data[df_dea_data['Input_IntendedRetrievals'] > 0]
    # # If Output_LiveBirths can be zero, this is okay. If not, filter:
    # # df_dea_data = df_dea_data[df_dea_data['Output_LiveBirths'] > 0]
    # rows_after_cleaning = len(df_dea_data)
    # print(f"Removed {initial_rows - rows_after_cleaning} rows due to missing/invalid inputs/outputs for DEA.")
    # print(f"Final prepared DEA dataset shape: {df_dea_data.shape}")
    
    Save this cleaned, prepared dataset:
    python
    # Example:
    # df_dea_data.to_csv(os.path.join(EDA_DIR, 'prepared_dea_input_output_data.csv'), index=False)
    # print("Prepared DEA data saved.")
    

**4. Exploratory Data Analysis (EDA) of Prepared DEA Data**

Before running DEA, analyze the characteristics of the prepared input and output data for each stratum (Year, Age Group).

4.1. **Descriptive Statistics per Stratum**:
    Group the `df_dea_data` by `Year` and `AgeGroup`. For each group, calculate:
    *   Number of unique clinics (DMUs).
    *   For `Input_IntendedRetrievals`: mean, median, min, max, standard deviation.
    *   For `Output_LiveBirths`: mean, median, min, max, standard deviation.
    *   Also, calculate statistics for the original `Data_Value_num` (Live Birth Rate %) to understand its distribution.

    Present these statistics in a series of tables (one for each year, or a combined table).

    **Example Table Structure (for one Year, e.g., 2020):**

    | Age Group | Num Clinics | Mean IR | Median IR | Min IR | Max IR | Std IR | Mean LB | Median LB | Min LB | Max LB | Std LB | Mean LB Rate (%) | Median LB Rate (%) |
    |:----------|:------------|:--------|:----------|:-------|:-------|:-------|:--------|:----------|:-------|:-------|:-------|:-----------------|:-------------------|
    | <35       | N1          | ...     | ...       | ...    | ...    | ...    | ...     | ...       | ...    | ...    | ...    | ...              | ...                |
    | 35-37     | N2          | ...     | ...       | ...    | ...    | ...    | ...     | ...       | ...    | ...    | ...    | ...              | ...                |
    | ...       | ...         | ...     | ...       | ...    | ...    | ...    | ...     | ...       | ...    | ...    | ...    | ...              | ...                |

    *IR = Intended Retrievals, LB = Live Births, LB Rate = % Live Birth per Intended Retrieval*

    python
    # Example:
    # eda_summary_list = []
    # for year_val in df_dea_data['Year'].unique():
    #     for age_group_val in df_dea_data['AgeGroup'].unique():
    #         stratum_data = df_dea_data[(df_dea_data['Year'] == year_val) & (df_dea_data['AgeGroup'] == age_group_val)]
    #         if stratum_data.empty:
    #             continue
    #         num_clinics = stratum_data['ClinicId'].nunique()
    #         stats_ir = stratum_data['Input_IntendedRetrievals'].agg(['mean', 'median', 'min', 'max', 'std']).to_dict()
    #         stats_lb = stratum_data['Output_LiveBirths'].agg(['mean', 'median', 'min', 'max', 'std']).to_dict()
    #         stats_lbrate = stratum_data['Data_Value_num'].agg(['mean', 'median']).to_dict() # Original percentage
    #
    #         eda_summary_list.append({
    #             'Year': year_val, 'AgeGroup': age_group_val, 'NumClinics': num_clinics,
    #             'Mean_IR': stats_ir['mean'], 'Median_IR': stats_ir['median'], 'Min_IR': stats_ir['min'], 'Max_IR': stats_ir['max'], 'Std_IR': stats_ir['std'],
    #             'Mean_LB': stats_lb['mean'], 'Median_LB': stats_lb['median'], 'Min_LB': stats_lb['min'], 'Max_LB': stats_lb['max'], 'Std_LB': stats_lb['std'],
    #             'Mean_LBRate': stats_lbrate['mean'], 'Median_LBRate': stats_lbrate['median']
    #         })
    # eda_summary_df = pd.DataFrame(eda_summary_list)
    # eda_summary_df.to_csv(os.path.join(EDA_DIR, 'eda_summary_statistics_by_stratum.csv'), index=False)
    # print("EDA summary statistics saved.")
    # print("\nEDA Summary Statistics by Stratum:")
    # print(eda_summary_df) # This is the table to be included in the methods section
    
    *The actual numerical values for the table above will be generated when you run this EDA step.*

**5. Data Envelopment Analysis (DEA)**

Perform DEA separately for each stratum (Year and AgeGroup).

5.1. **DEA Model Selection**:
    We will use an input-oriented Banker, Charnes, Cooper (BCC-I) model. This model assumes variable returns to scale (VRS), which is generally more appropriate for entities like clinics, and focuses on proportional input reduction capability.
    For each DMU_o (clinic being evaluated) in a stratum, with input `x_o` (Intended Retrievals) and output `y_o` (Live Births), we solve:
    Minimize θ
    Subject to:
    Σ (λ_j * x_j) <= θ * x_io  (for the single input i=1, Intended Retrievals)
    Σ (λ_j * y_j) >= y_ro      (for the single output r=1, Live Births)
    Σ λ_j = 1                  (VRS constraint)
    λ_j >= 0                   (for all DMUs j in the stratum)

    The efficiency score for DMU_o is θ. A score of 1 indicates technical efficiency (on the frontier).

5.2. **DEA Implementation Function**:
    Create a Python function that takes arrays of inputs (X) and outputs (Y) for all DMUs in a stratum, and the index of the DMU_o to be evaluated. This function will use `scipy.optimize.linprog`.

    python
    # Example DEA function:
    # def solve_dea_bcc_input_oriented(inputs_arr, outputs_arr, dmu_idx):
    #     num_dmus = inputs_arr.shape[0]
    #     # inputs_arr is (num_dmus, num_inputs), outputs_arr is (num_dmus, num_outputs)
    #     # For this project, num_inputs=1, num_outputs=1
    #
    #     x_o = inputs_arr[dmu_idx, :]
    #     y_o = outputs_arr[dmu_idx, :]
    #
    #     # Objective function: minimize theta
    #     # Variables: [theta, lambda_1, ..., lambda_N] (N = num_dmus)
    #     # c = [1, 0, 0, ..., 0]
    #     c = np.zeros(num_dmus + 1)
    #     c[0] = 1
    #
    #     # Inequality constraints (Ax <= b)
    #     # 1. Sum(lambda_j * x_ij) - theta * x_io <= 0  =>  Sum(lambda_j * x_ij) - theta * x_io <= 0
    #     #    Rewritten for linprog: theta * x_io - Sum(lambda_j * x_ij) >= 0
    #     #    This is for each input. Here, one input.
    #     #    A_ub matrix rows:
    #     #    [x_io, -x_1, -x_2, ..., -x_N]  (for the input constraint, but linprog expects <=, so multiply by -1)
    #     #    Let's structure for linprog:
    #     #    theta * x_io - sum(lambda_j * x_j) >= 0  => sum(lambda_j * x_j) - theta * x_io <= 0
    #     A_ub_input_rows = np.hstack([
    #         -x_o.reshape(-1, 1), # Coeff for theta (negative because x_o is on RHS of theta)
    #         inputs_arr.T         # Coeffs for lambdas
    #     ]) # Shape: (num_inputs, num_dmus + 1)
    #     b_ub_input_rows = np.zeros(inputs_arr.shape[1])
    #
    #     # 2. Sum(lambda_j * y_rj) >= y_ro  =>  y_ro - Sum(lambda_j * y_rj) <= 0
    #     #    A_ub matrix rows:
    #     #    [0, -y_1, -y_2, ..., -y_N]
    #     A_ub_output_rows = np.hstack([
    #         np.zeros((outputs_arr.shape[1], 1)), # Coeff for theta
    #         -outputs_arr.T                       # Coeffs for lambdas (negative because original is >=)
    #     ]) # Shape: (num_outputs, num_dmus + 1)
    #     b_ub_output_rows = -y_o
    #
    #     A_ub = np.vstack([A_ub_input_rows, A_ub_output_rows])
    #     b_ub = np.concatenate([b_ub_input_rows, b_ub_output_rows])
    #
    #     # Equality constraints (Aeq x = beq)
    #     # Sum(lambda_j) = 1
    #     # A_eq = [0, 1, 1, ..., 1]
    #     A_eq = np.ones((1, num_dmus + 1))
    #     A_eq[0, 0] = 0
    #     b_eq = np.array([1])
    #
    #     # Bounds for variables:
    #     # theta >= 0 (implicitly, can be set to (None, None) or (0, None) or (0,1] if input oriented)
    #     # lambda_j >= 0
    #     bounds = [(None, None)] + [(0, None)] * num_dmus # Theta can be unbounded or (0,1] for input-oriented.
    #                                                    # (0,1] might be better for input-oriented theta.
    #                                                    # Let's use (0,None) for theta, as some formulations allow >1 for super-efficiency if input > peer sum.
    #                                                    # For standard efficiency, theta <=1. LP solver will find smallest positive.
    #     bounds[0] = (0,1) # Theta for input-oriented efficiency score is <=1
    #
    #     res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs') # 'highs' is default in newer scipy
    #
    #     if res.success:
    #         return res.fun # This is theta
    #     else:
    #         # print(f"Optimization failed for DMU {dmu_idx}: {res.message}")
    #         return np.nan
    

5.3. **Parallelized DEA Execution**:
    Iterate through each Year and AgeGroup stratum. For each stratum:
    *   Extract the input and output arrays for all clinics.
    *   Use the `multiprocessing.Pool` to apply the `solve_dea_bcc_input_oriented` function to each clinic in parallel.
    *   Store the resulting efficiency scores.

    python
    # Example of loop and parallel execution:
    # all_results = []
    # unique_strata = df_dea_data[['Year', 'AgeGroup']].drop_duplicates()
    #
    # for index, row in unique_strata.iterrows():
    #     year = row['Year']
    #     age_group = row['AgeGroup']
    #     stratum_df = df_dea_data[(df_dea_data['Year'] == year) & (df_dea_data['AgeGroup'] == age_group)].copy()
    #
    #     if len(stratum_df) < 2: # Need at least 2 DMUs for comparison, ideally more
    #         print(f"Skipping stratum Year {year}, AgeGroup {age_group} due to insufficient DMUs ({len(stratum_df)}).")
    #         # Assign NaN or 1 to single DMUs if any (a single DMU is always efficient)
    #         if len(stratum_df) == 1:
    #             stratum_df['EfficiencyScore'] = 1.0
    #             all_results.append(stratum_df)
    #         continue
    #
    #     inputs_arr = stratum_df['Input_IntendedRetrievals'].values.reshape(-1, 1)
    #     outputs_arr = stratum_df['Output_LiveBirths'].values.reshape(-1, 1)
    #
    #     # Handle cases where all outputs are zero for a stratum
    #     if np.all(outputs_arr == 0):
    #         print(f"All outputs are zero for stratum Year {year}, AgeGroup {age_group}. Assigning NaN to efficiency scores.")
    #         stratum_df['EfficiencyScore'] = np.nan
    #         all_results.append(stratum_df)
    #         continue
    #
    #     # If an output is 0 for a DMU, it can cause issues if it's the only one producing that output.
    #     # Small positive value (epsilon) can be added to outputs if they are zero,
    #     # but this changes the data. Standard DEA handles zero outputs if other DMUs have positive outputs.
    #     # If an output is essential and a DMU has zero of it, it will likely be inefficient.
    #
    #     num_dmus = len(stratum_df)
    #     # tasks = [(inputs_arr, outputs_arr, i) for i in range(num_dmus)]
    #
    #     # Use with Pool for context management (auto-closes pool)
    #     # with multiprocessing.Pool(processes=min(os.cpu_count(), 128)) as pool:
    #     #    efficiency_scores = pool.starmap(solve_dea_bcc_input_oriented_wrapper, tasks) # Need a wrapper if func is not top-level
    #
    #     # For simplicity here, sequential execution (replace with parallel for actual run)
    #     efficiency_scores = []
    #     for i in range(num_dmus):
    #          # If solve_dea_bcc_input_oriented is defined within this script, it might need to be passed or made global for multiprocessing.
    #          # Or use a helper function that can be pickled.
    #          score = solve_dea_bcc_input_oriented(inputs_arr, outputs_arr, i)
    #          efficiency_scores.append(score)
    #
    #     stratum_df['EfficiencyScore'] = efficiency_scores
    #     all_results.append(stratum_df)
    #     print(f"DEA scores calculated for Year {year}, AgeGroup {age_group}.")
    #
    # final_dea_results_df = pd.concat(all_results, ignore_index=True)
    # final_dea_results_df.to_csv(os.path.join(DEA_RESULTS_DIR, 'clinic_efficiency_scores.csv'), index=False)
    # print("All DEA efficiency scores calculated and saved.")
    
    *Note: The `solve_dea_bcc_input_oriented` function should be defined at the top level of a module or passed carefully for `multiprocessing` to work correctly. For this document, its placement is illustrative.*

**6. Post-DEA Analysis and Reporting**

6.1. **Analyze Efficiency Score Distributions**:
    Using the `final_dea_results_df` containing efficiency scores:
    *   For each Year and AgeGroup stratum:
        *   Calculate descriptive statistics of `EfficiencyScore` (mean, median, min, max, std dev).
        *   Count the number and percentage of efficient clinics (EfficiencyScore ≈ 1, e.g., >= 0.9999 due to potential floating-point inaccuracies).
    *   Aggregate these statistics into a summary table.

    python
    # Example:
    # efficiency_summary_list = []
    # for year_val in final_dea_results_df['Year'].unique():
    #     for age_group_val in final_dea_results_df['AgeGroup'].unique():
    #         stratum_scores = final_dea_results_df[
    #             (final_dea_results_df['Year'] == year_val) &
    #             (final_dea_results_df['AgeGroup'] == age_group_val)
    #         ]['EfficiencyScore'].dropna()
    #
    #         if stratum_scores.empty:
    #             continue
    #
    #         desc_stats = stratum_scores.agg(['mean', 'median', 'min', 'max', 'std']).to_dict()
    #         num_efficient = (stratum_scores >= 0.9999).sum() # Using a threshold for float precision
    #         pct_efficient = (num_efficient / len(stratum_scores)) * 100 if len(stratum_scores) > 0 else 0
    #
    #         efficiency_summary_list.append({
    #             'Year': year_val, 'AgeGroup': age_group_val,
    #             'Num_DMUs_in_Stratum': len(stratum_scores),
    #             'Mean_Efficiency': desc_stats['mean'], 'Median_Efficiency': desc_stats['median'],
    #             'Min_Efficiency': desc_stats['min'], 'Max_Efficiency': desc_stats['max'], # Max should be 1
    #             'Std_Efficiency': desc_stats['std'],
    #             'Num_Efficient_Clinics': num_efficient, 'Pct_Efficient_Clinics': pct_efficient
    #         })
    #
    # efficiency_summary_df = pd.DataFrame(efficiency_summary_list)
    # efficiency_summary_df.to_csv(os.path.join(DEA_RESULTS_DIR, 'efficiency_score_summary_by_stratum.csv'), index=False)
    # print("Efficiency score summary statistics saved.")
    # print("\nEfficiency Score Summary by Stratum:")
    # print(efficiency_summary_df)
    

6.2. **Temporal Analysis of Efficiency**:
    Analyze how average efficiency scores change over the three years (2020, 2021, 2022) for each age group.
    *   Group the `efficiency_summary_df` by `AgeGroup` and examine the trend of `Mean_Efficiency` across years.
    *   This can be presented in a table or used to describe trends.

    python
    # Example:
    # temporal_analysis = efficiency_summary_df.pivot_table(
    #     index='AgeGroup',
    #     columns='Year',
    #     values='Mean_Efficiency'
    # )
    # temporal_analysis.to_csv(os.path.join(DEA_RESULTS_DIR, 'temporal_mean_efficiency_by_agegroup.csv'))
    # print("\nTemporal Analysis of Mean Efficiency by Age Group:")
    # print(temporal_analysis)
    

This detailed methodology provides a step-by-step guide to performing the DEA for assessing ART clinic efficiency. Ensure each step is executed carefully, and intermediate results are saved and verified. The use of parallel processing for DEA calculations will be critical for managing computation time. Remember to generate plots for your own understanding at each stage, especially during EDA and when analyzing efficiency score distributions, but do not include references to them in the final methods write-up based on the project instructions.