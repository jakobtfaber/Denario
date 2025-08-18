# filename: codebase/results_visualization.py
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


class ResultsVisualizer:
    """
    Generates final plots and summary statistics for the pulsar timing campaign.

    This class loads the analytic and simulation results, creates a unified
    comparison DataFrame, prints a summary table for the researcher, and
    generates plots for key metrics like timing uncertainty and telescope time usage.
    """

    def __init__(self):
        """
        Initializes the visualizer by loading all necessary data.
        """
        self.database_path = "data/"
        self.sim_setup = PulsarSimulationSetup()

        # Load data
        self.analytic_recs_df = self._load_data("analytic_cadence_recommendations.csv")
        self.sim_results_df = self._load_data("timing_simulation_results.csv")
        self.pulsar_catalog_df = self._load_data("synthetic_pulsar_population.csv")

        if self.analytic_recs_df is None or self.sim_results_df is None or self.pulsar_catalog_df is None:
            raise FileNotFoundError("Could not load one or more required data files. Please run previous steps.")

        self.cadence_analyzer = AnalyticCadence(self.sim_setup, self.pulsar_catalog_df)
        self.comparison_df = self._prepare_data()

    def _load_data(self, filename):
        """Loads a CSV file from the data directory."""
        file_path = os.path.join(self.database_path, filename)
        if not os.path.exists(file_path):
            print("Error: File not found at " + file_path)
            return None
        return pd.read_csv(file_path)

    def _prepare_data(self):
        """
        Aggregates simulation results and merges with analytic predictions.
        """
        # Aggregate simulation results
        agg_dict = {
            'phase_connected': 'mean',
            'num_epochs': 'median',
            'total_telescope_time_s': 'median',
            'final_sigma_P_ns': 'median',
            'final_sigma_Pdot_1e-15': 'median'
        }
        sim_summary = self.sim_results_df.groupby('population_type').agg(agg_dict).reset_index()
        sim_summary.rename(columns={
            'phase_connected': 'sim_success_rate',
            'num_epochs': 'sim_median_epochs',
            'total_telescope_time_s': 'sim_median_time_s',
            'final_sigma_P_ns': 'sim_median_sigma_P_ns',
            'final_sigma_Pdot_1e-15': 'sim_median_sigma_Pdot_1e-15'
        }, inplace=True)

        # Recalculate analytic uncertainties for a 2-year baseline
        recalculated_analytics = []
        for index, row in sim_summary.iterrows():
            pop_type = row['population_type']
            analytic_row = self.analytic_recs_df[self.analytic_recs_df['population_type'] == pop_type].iloc[0]
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

        # Merge all data into a final comparison DataFrame
        comparison_df = pd.merge(self.analytic_recs_df, sim_summary, on='population_type')
        comparison_df = pd.merge(comparison_df, recalc_df, on='population_type')
        return comparison_df

    def print_summary_table(self):
        """
        Prints the final summary table of key statistics for the researcher.
        """
        print("\n" + "="*120)
        print("--- Final Summary Table: Analytic Recommendations vs. Simulation Outcomes ---")
        print("="*120)
        
        display_cols = [
            'population_type',
            'recommended_cadence_days',
            'sim_success_rate',
            'sim_median_epochs',
            'sim_median_time_s',
            'analytic_recalc_sigma_P_ns',
            'sim_median_sigma_P_ns',
            'analytic_recalc_sigma_Pdot_1e-15',
            'sim_median_sigma_Pdot_1e-15'
        ]
        
        # Formatting for display
        formatted_df = self.comparison_df[display_cols].copy()
        formatted_df['sim_success_rate'] = formatted_df['sim_success_rate'].map('{:.2%}'.format)
        formatted_df['sim_median_time_ks'] = formatted_df['sim_median_time_s'] / 1000.0
        
        formatted_df.rename(columns={
            'recommended_cadence_days': 'Analytic Cadence (days)',
            'sim_success_rate': 'Sim. Success Rate',
            'sim_median_epochs': 'Sim. Median Epochs',
            'sim_median_time_ks': 'Sim. Median Time (ks)',
            'analytic_recalc_sigma_P_ns': 'Analytic sigma_P (ns)',
            'sim_median_sigma_P_ns': 'Sim. sigma_P (ns)',
            'analytic_recalc_sigma_Pdot_1e-15': 'Analytic sigma_Pdot (1e-15)',
            'sim_median_sigma_Pdot_1e-15': 'Sim. sigma_Pdot (1e-15)'
        }, inplace=True)
        
        # Reorder and drop old time column
        final_cols = [
            'population_type', 'Analytic Cadence (days)', 'Sim. Success Rate',
            'Sim. Median Epochs', 'Sim. Median Time (ks)', 'Analytic sigma_P (ns)',
            'Sim. sigma_P (ns)', 'Analytic sigma_Pdot (1e-15)', 'Sim. sigma_Pdot (1e-15)'
        ]
        
        pd.set_option('display.width', 200)
        pd.set_option('display.max_columns', 20)
        print(formatted_df[final_cols].to_string(index=False))
        print("="*120 + "\n")

    def plot_timing_uncertainties(self):
        """
        Generates a 2-panel plot comparing analytic and simulated timing uncertainties.
        """
        plt.style.use('default')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
        
        pop_types = self.comparison_df['population_type']
        x = np.arange(len(pop_types))
        width = 0.35

        # --- Panel 1: Sigma_P ---
        ax1.bar(x - width/2, self.comparison_df['analytic_recalc_sigma_P_ns'], width, label='Analytic Prediction', color='skyblue', edgecolor='black')
        ax1.bar(x + width/2, self.comparison_df['sim_median_sigma_P_ns'], width, label='Simulation Result', color='salmon', edgecolor='black')
        ax1.set_ylabel('Median sigma_P (ns)')
        ax1.set_title('Comparison of Period and Period-Derivative Uncertainties')
        ax1.set_yscale('log')
        ax1.legend()
        ax1.grid(axis='y', linestyle='--', which='both', alpha=0.7)

        # --- Panel 2: Sigma_Pdot ---
        ax2.bar(x - width/2, self.comparison_df['analytic_recalc_sigma_Pdot_1e-15'], width, label='Analytic Prediction', color='skyblue', edgecolor='black')
        ax2.bar(x + width/2, self.comparison_df['sim_median_sigma_Pdot_1e-15'], width, label='Simulation Result', color='salmon', edgecolor='black')
        ax2.set_ylabel('Median sigma_Pdot (1e-15 s/s)')
        ax2.set_yscale('log')
        ax2.grid(axis='y', linestyle='--', which='both', alpha=0.7)
        
        plt.xticks(x, pop_types, rotation=45, ha='right')
        fig.tight_layout()

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = "timing_uncertainty_comparison_2_" + timestamp + ".png"
        output_path = os.path.join(self.database_path, filename)
        plt.savefig(output_path, dpi=300)
        plt.close(fig)

        print("Timing uncertainty comparison plot saved to: " + output_path)
        print("Plot Description: This plot compares the predicted (analytic) and achieved (simulation) median timing uncertainties for P and P-dot over a 2-year campaign. The log scale highlights the orders-of-magnitude differences between pulsar populations.")

    def plot_telescope_time_usage(self):
        """
        Generates a box plot of the total telescope time used per source.
        """
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(12, 7))

        # Prepare data for boxplot
        pop_order = self.comparison_df['population_type'].tolist()
        data_to_plot = [self.sim_results_df[self.sim_results_df['population_type'] == pop]['total_telescope_time_s'] for pop in pop_order]

        ax.boxplot(data_to_plot, labels=pop_order, patch_artist=True, medianprops={'color': 'black'})
        
        ax.set_ylabel('Total Telescope Time per Source (s)')
        ax.set_title('Distribution of Telescope Time Usage per Source (2-Year Campaign)')
        ax.set_yscale('log')
        ax.grid(axis='y', linestyle='--', which='both', alpha=0.7)
        plt.xticks(rotation=45, ha='right')
        
        fig.tight_layout()

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = "telescope_time_usage_3_" + timestamp + ".png"
        output_path = os.path.join(self.database_path, filename)
        plt.savefig(output_path, dpi=300)
        plt.close(fig)

        print("\nTelescope time usage plot saved to: " + output_path)
        print("Plot Description: This box plot shows the distribution of total telescope time required per source over a 2-year campaign for each pulsar sub-population. The log scale accommodates the wide range in observation time, driven by factors like source brightness and cadence requirements.")

    def run_analysis(self):
        """
        Executes the full visualization and reporting workflow.
        """
        self.print_summary_table()
        self.plot_timing_uncertainties()
        self.plot_telescope_time_usage()
        print("\n--- Results Visualization and Summary Complete ---")


if __name__ == "__main__":
    try:
        visualizer = ResultsVisualizer()
        visualizer.run_analysis()
    except FileNotFoundError as e:
        print("Visualization process failed.")
        print(e)
    except Exception as e:
        print("An unexpected error occurred during visualization:")
        print(e)