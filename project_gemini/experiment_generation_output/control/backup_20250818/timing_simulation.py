# filename: codebase/timing_simulation.py
import os
import sys
import numpy as np
import pandas as pd

# Add project root to python path to allow for module imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from codebase.pulsar_simulation_setup import PulsarSimulationSetup
from codebase.analytic_cadence import AnalyticCadence


class TimingCampaignSimulator:
    """
    Simulates a timing campaign for a synthetic pulsar population.

    This class applies an adaptive cadence strategy, starting with an initial
    analytic prescription and then adjusting observation schedules based on the
    evolving timing solution. It simulates various noise sources and stochastic
    events to test the robustness of the cadence strategies.
    """

    def __init__(self, setup, pulsar_catalog, analytic_cadence):
        """
        Initializes the TimingCampaignSimulator.

        Args:
            setup (PulsarSimulationSetup): Object with telescope parameters.
            pulsar_catalog (pd.DataFrame): DataFrame of synthetic pulsars.
            analytic_cadence (AnalyticCadence): Object with analytic cadence logic.
        """
        self.setup = setup
        self.pulsar_catalog = pulsar_catalog
        self.analytic_cadence = analytic_cadence
        self.simulation_duration_days = 2 * 365.25
        self.initial_epochs_days = [0, 3, 10]
        
        # Glitch parameters: rate (events/year), log10 of fractional frequency change
        self.glitch_params = {
            "young": {"rate": 0.1, "df_f_meanlog": -7, "df_f_stdlog": 1.0},
            "magnetar": {"rate": 0.5, "df_f_meanlog": -5, "df_f_stdlog": 1.0},
        }

    def _get_observation_results(self, pulsar, t_int_s):
        """Calculates sigma_toa for a single observation."""
        sigma_toa = self.analytic_cadence.get_total_toa_uncertainty(pulsar, t_int_s)
        return sigma_toa

    def _update_timing_uncertainties(self, epochs, true_p):
        """
        Updates P and Pdot uncertainties based on the current set of epochs.
        Uses the analytic formulas from the AnalyticCadence class.
        """
        n_epochs = len(epochs)
        if n_epochs < 2:
            return np.inf, np.inf
        
        t_span_s = (epochs[-1][0] - epochs[0][0]) * 86400.0
        # Ensure t_span is non-zero to avoid division errors
        if t_span_s <= 0:
            t_span_s = 1.0 # A small, non-zero span for calculation purposes

        avg_sigma_toa = np.mean([e[1] for e in epochs])
        
        sigma_p, sigma_pdot = self.analytic_cadence.calculate_timing_uncertainties(
            avg_sigma_toa, n_epochs, t_span_s, true_p
        )
        return sigma_p, sigma_pdot

    def simulate_pulsar(self, pulsar_series):
        """
        Runs the full timing simulation for a single pulsar.

        Args:
            pulsar_series (pd.Series): A row from the pulsar catalog.

        Returns:
            dict: A dictionary containing the simulation results for one pulsar.
        """
        # --- Initialization ---
        pop_type = pulsar_series['population_type']
        true_p, true_pdot = pulsar_series['P'], pulsar_series['P_dot']
        
        # --- MODIFICATION: Calculate required integration time for this specific pulsar ---
        t_int_s = 60.0  # Start with 1 minute
        max_dwell = self.setup.search_params['targeted']['t_dwell_max']
        # This loop calculates the integration time needed for S/N > 20
        # (approximated by sigma_rad < P/20)
        while self.analytic_cadence.calculate_sigma_rad(pulsar_series["S1400"], pulsar_series["P"], pulsar_series["W"], t_int_s) > pulsar_series["P"] / 20.0:
            t_int_s *= 1.5
            if t_int_s > max_dwell:
                t_int_s = max_dwell
                break

        epochs = []  # List to store (observation_day, sigma_toa_s)
        total_telescope_time_s = 0
        is_phase_connected = True
        
        # --- Initial Characterization Campaign ---
        for day in self.initial_epochs_days:
            sigma_toa_s = self._get_observation_results(pulsar_series, t_int_s)
            epochs.append((day, sigma_toa_s))
            total_telescope_time_s += t_int_s

        # --- Initial Timing Model ---
        sigma_p, sigma_pdot = self._update_timing_uncertainties(epochs, true_p)
        # The "model" is a realization of the true parameters with added error
        model_p = true_p + np.random.normal(0, sigma_p)
        model_pdot = true_pdot + np.random.normal(0, sigma_pdot)

        # --- Adaptive Cadence Loop ---
        current_day = epochs[-1][0]
        while current_day < self.simulation_duration_days:
            # --- Schedule Next Observation ---
            delta_t_days = self.analytic_cadence.calculate_max_interval(model_p, sigma_p, sigma_pdot)
            
            safe_delta_t = max(1.0, delta_t_days * 0.8)
            next_obs_day = current_day + safe_delta_t

            if next_obs_day >= self.simulation_duration_days:
                break

            # --- Check for Phase Loss before observing ---
            dt_s = (next_obs_day - epochs[-1][0]) * 86400.0
            n_cycles_true = dt_s / true_p
            n_cycles_model = dt_s / model_p
            if abs(round(n_cycles_true) - round(n_cycles_model)) >= 1:
                is_phase_connected = False
                break

            # --- Simulate Stochastic Events for the Interval ---
            if pop_type in self.glitch_params:
                glitch_prob = self.glitch_params[pop_type]["rate"] * (safe_delta_t / 365.25)
                if np.random.random() < glitch_prob:
                    df_f_log = np.random.normal(
                        self.glitch_params[pop_type]["df_f_meanlog"],
                        self.glitch_params[pop_type]["df_f_stdlog"]
                    )
                    delta_f = (10**df_f_log) * (1.0 / true_p)
                    true_p = 1.0 / ((1.0 / true_p) + delta_f)

            # --- Simulate the Observation ---
            if pop_type == 'intermittent':
                if np.random.random() > pulsar_series['duty_cycle']:
                    current_day += 1.0 
                    continue

            sigma_toa_s = self._get_observation_results(pulsar_series, t_int_s)
            epochs.append((next_obs_day, sigma_toa_s))
            total_telescope_time_s += t_int_s
            current_day = next_obs_day

            # --- Refit Timing Model ---
            sigma_p, sigma_pdot = self._update_timing_uncertainties(epochs, true_p)
            model_p = true_p + np.random.normal(0, sigma_p)
            model_pdot = true_pdot + np.random.normal(0, sigma_pdot)

        # --- Compile Results ---
        return {
            'phase_connected': is_phase_connected,
            'final_sigma_P_ns': sigma_p * 1e9,
            'final_sigma_Pdot_1e-15': sigma_pdot / 1e-15,
            'total_telescope_time_s': total_telescope_time_s,
            'num_epochs': len(epochs),
            'population_type': pop_type
        }

    def run_simulation(self):
        """
        Runs the simulation for the entire pulsar catalog.
        """
        print("Starting timing campaign simulations for " + str(len(self.pulsar_catalog)) + " pulsars...")
        
        results = []
        pulsar_records = self.pulsar_catalog.to_dict('records')
        
        for i, pulsar in enumerate(pulsar_records):
            if (i + 1) % 1000 == 0:
                print("  Simulated " + str(i + 1) + " pulsars...")
            result = self.simulate_pulsar(pulsar)
            results.append(result)
        
        print("...Simulations complete.")
        return pd.DataFrame(results)


if __name__ == "__main__":
    # 1. Initialize setup and load data
    sim_setup = PulsarSimulationSetup()
    
    catalog_path = os.path.join(sim_setup.database_path, "synthetic_pulsar_population.csv")
    analytic_path = os.path.join(sim_setup.database_path, "analytic_cadence_recommendations.csv")

    if not os.path.exists(catalog_path) or not os.path.exists(analytic_path):
        print("Error: Required data files not found.")
        print("Please run previous steps (pulsar_simulation_setup.py, analytic_cadence.py) first.")
    else:
        pulsar_catalog_df = pd.read_csv(catalog_path)

        # 2. Initialize analytic and simulation classes
        cadence_analyzer = AnalyticCadence(sim_setup, pulsar_catalog_df)
        # This call prints the analytic summary based on median pulsars.
        # The simulation itself now calculates t_int for each pulsar individually.
        cadence_analyzer.develop_cadence_prescriptions()

        simulator = TimingCampaignSimulator(sim_setup, pulsar_catalog_df, cadence_analyzer)

        # 3. Run the simulation
        simulation_results_df = simulator.run_simulation()

        # 4. Save and report results
        output_file = os.path.join(sim_setup.database_path, "timing_simulation_results.csv")
        simulation_results_df.to_csv(output_file, index=False)
        print("\n--- Timing Simulation Results ---")
        print("Detailed simulation results saved to: " + output_file)

        # Calculate and print summary statistics
        summary = simulation_results_df.groupby('population_type').agg(
            success_rate=('phase_connected', lambda x: x.mean()),
            median_epochs=('num_epochs', 'median'),
            median_time_ks=('total_telescope_time_s', lambda x: x.median() / 1000.0)
        ).reset_index()

        print("\n--- Summary of Simulation Outcomes by Population ---")
        pd.set_option('display.width', 1000)
        pd.set_option('display.max_columns', 10)
        print(summary.to_string())
