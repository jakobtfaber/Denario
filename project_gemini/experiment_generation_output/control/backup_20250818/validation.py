# filename: codebase/validation.py
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

# Add project root to python path to allow for module imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from codebase.pulsar_simulation_setup import PulsarSimulationSetup
from codebase.analytic_cadence import AnalyticCadence


class Validation:
    """
    Validates simulation outputs against analytic predictions.

    This class compares the results from the TimingCampaignSimulator with the
    predictions from the AnalyticCadence class to identify discrepancies,
    quantify them, and refine the understanding of the cadence strategies.
    """

    def __init__(self):
        """
        Initializes the Validation class by loading necessary data.
        """
        self.database_path = "data/"
        self.sim_setup = PulsarSimulationSetup()
        
        # Load data
        self.analytic_recs_df = self._load_data("analytic_cadence_recommendations.csv")
        self.sim_results_df = self._load_data("timing_simulation_results.csv")
        self.pulsar_catalog_df = self._load_data("synthetic_pulsar_population.csv")

        if self.analytic_recs_df is None or self.sim_results_df is None or self.pulsar_catalog_df is None:
            raise FileNotFoundError("Could not load one or more required data files.")
            
        self.cadence_analyzer = AnalyticCadence(self.sim_setup, self.pulsar_catalog_df)


    def _load_data(self, filename):
        """Loads a CSV file from the data directory."""
        file_path = os.path.join(self.database_path, filename)
        if not os.path.exists(file_path):
            print("Error: File not found at " + file_path)
            return None
        return pd.read_csv(file_path)

    def run_validation(self):
        """
        Performs the full validation process: comparison, quantification, and reporting.
        """
        print("--- Starting Validation of Simulation vs. Analytic Predictions ---")

        # 1. Aggregate simulation results using a dictionary to avoid syntax errors
        agg_dict = {
            'phase_connected': 'mean',
            'num_epochs': 'median',
            'total_telescope_time_s': 'median',
            'final_sigma_P_ns': 'median',
            'final_sigma_Pdot_1e-15': 'median'
        }
        sim_summary = self.sim_results_df.groupby('population_type').agg(agg_dict).reset_index()

        # Rename columns to the desired format
        sim_summary.rename(columns={
            'phase_connected': 'sim_success_rate',
            'num_epochs': 'sim_median_epochs',
            'total_telescope_time_s': 'sim_median_time_s',
            'final_sigma_P_ns': 'sim_median_sigma_P_ns',
            'final_sigma_Pdot_1e-15': 'sim_median_sigma_Pdot_1e-15'
        }, inplace=True)


        # 2. Recalculate analytic uncertainties for a fair comparison (2-year baseline)
        recalculated_analytics = []
        for index, row in sim_summary.iterrows():
            pop_type = row['population_type']
            analytic_row = self.analytic_recs_df[self.analytic_recs_df['population_type'] == pop_type].iloc[0]
            
            # Use simulation's median epochs and full 2-year time span
            n_epochs = row['sim_median_epochs']
            t_span_s = (2 * 365.25) * 86400.0
            sigma_toa_s = analytic_row['sigma_toa_us'] * 1e-6
            p_sec = analytic_row['P_median_s']

            recalc_sigma_p, recalc_sigma_pdot = self.cadence_analyzer.calculate_timing_uncertainties(
                sigma_toa_s, n_epochs, t_span_s, p_sec
            )
            
            recalculated_analytics.append({
                'population_type': pop_type,
                'analytic_recalc_sigma_P_ns': recalc_sigma_p * 1e9,
                'analytic_recalc_sigma_Pdot_1e-15': recalc_sigma_pdot / 1e-15
            })
        
        recalc_df = pd.DataFrame(recalculated_analytics)

        # 3. Merge analytic and simulation summaries
        comparison_df = pd.merge(self.analytic_recs_df, sim_summary, on='population_type')
        comparison_df = pd.merge(comparison_df, recalc_df, on='population_type')

        # 4. Quantify discrepancies
        # The analytic model assumes 100% success if cadence is followed.
        comparison_df['success_rate_discrepancy_pct'] = np.abs(comparison_df['sim_success_rate'] - 1.0) * 100

        comparison_df['sigma_P_discrepancy_pct'] = np.abs((comparison_df['sim_median_sigma_P_ns'] - comparison_df['analytic_recalc_sigma_P_ns']) / comparison_df['analytic_recalc_sigma_P_ns']) * 100

        comparison_df['sigma_Pdot_discrepancy_pct'] = np.abs((comparison_df['sim_median_sigma_Pdot_1e-15'] - comparison_df['analytic_recalc_sigma_Pdot_1e-15']) / comparison_df['analytic_recalc_sigma_Pdot_1e-15']) * 100

        # 5. Print the detailed comparison table
        print("\n--- Detailed Comparison: Analytic vs. Simulation ---")
        pd.set_option('display.width', 200)
        pd.set_option('display.max_columns', 20)
        
        display_cols = [
            'population_type', 'sim_success_rate', 'success_rate_discrepancy_pct',
            'analytic_recalc_sigma_P_ns', 'sim_median_sigma_P_ns', 'sigma_P_discrepancy_pct',
            'analytic_recalc_sigma_Pdot_1e-15', 'sim_median_sigma_Pdot_1e-15', 'sigma_Pdot_discrepancy_pct',
            'sim_median_epochs', 'sim_median_time_s'
        ]
        print(comparison_df[display_cols].to_string())
        
        # 6. Document reasons for discrepancies
        print("\n--- Interpretation of Discrepancies ---")
        print("The analytic model provides a baseline assuming ideal conditions and median pulsars.")
        print("The simulation introduces per-pulsar variations and stochastic events, leading to discrepancies:")
        print(" - Success Rate: Analytic model assumes 100% success. Simulation failures are caused by:")
        print("   - Magnetars/Young Pulsars: Glitches can cause phase loss if not caught quickly.")
        print("   - Intermittent Pulsars: Long 'off' states can prevent timely follow-up.")
        print("   - Galactic Center: Extreme ISM effects (not fully modeled by a single sigma_ism) and high noise.")
        print("   - Low S/N Pulsars: Some pulsars in the distribution are too faint for the fixed integration time, leading to large TOA errors.")
        print(" - Timing Uncertainty (sigma_P, sigma_Pdot): Discrepancies arise from:")
        print("   - The simulation using per-pulsar parameters, while the analytic model uses the median.")
        print("   - The distribution of TOA errors being non-Gaussian for some populations (e.g., jitter-dominated).")
        print("   - The final number of epochs varying per pulsar in the simulation.")

        # 7. Generate comparison plot
        self._generate_comparison_plot(comparison_df)
        
        print("\n--- Validation Complete ---")
        
        return comparison_df

    def _generate_comparison_plot(self, comparison_df):
        """
        Generates and saves a bar chart comparing analytic and simulated success rates.
        """
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(12, 7))

        pop_types = comparison_df['population_type']
        sim_success_rates = comparison_df['sim_success_rate']
        
        x = np.arange(len(pop_types))
        width = 0.4

        # Analytic success rate is implicitly 1.0 (100%)
        ax.bar(x - width/2, [1.0] * len(pop_types), width, label='Analytic Prediction (Ideal)', color='skyblue', edgecolor='black')
        ax.bar(x + width/2, sim_success_rates, width, label='Simulation Result', color='salmon', edgecolor='black')

        ax.set_ylabel('Phase-Connection Success Rate')
        ax.set_title('Validation: Analytic vs. Simulated Phase-Connection Success Rate')
        ax.set_xticks(x)
        ax.set_xticklabels(pop_types, rotation=45, ha='right')
        ax.set_ylim(0, 1.1)
        ax.legend()
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add percentage values on top of the simulation bars
        for i, v in enumerate(sim_success_rates):
            ax.text(x[i] + width/2, v + 0.02, str(round(v*100)) + '%', ha='center', color='black')

        fig.tight_layout()

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = "validation_success_rate_comparison_1_" + timestamp + ".png"
        output_path = os.path.join(self.database_path, filename)
        plt.savefig(output_path, dpi=300)
        plt.close(fig)

        print("\nComparison plot saved to: " + output_path)
        print("Plot Description: This bar chart compares the ideal analytic prediction for phase-connection success rate (100%) against the achieved success rate from the detailed simulation for each pulsar sub-population. It highlights the performance degradation due to stochastic noise and events like glitches and intermittency.")


if __name__ == "__main__":
    try:
        validator = Validation()
        validator.run_validation()
    except FileNotFoundError as e:
        print("Validation process failed.")
        print(e)
    except Exception as e:
        print("An unexpected error occurred during validation:")
        print(e)