# filename: codebase/analytic_cadence.py
import sys
import os
import numpy as np
import pandas as pd

# Add project root to python path to allow for module imports
# Assuming the script is in project_root/codebase/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from codebase.pulsar_simulation_setup import PulsarSimulationSetup


class AnalyticCadence:
    """
    Develops analytic cadence prescriptions for pulsar sub-populations.

    This class uses the telescope parameters and a synthetic pulsar catalog to
    derive the optimal spacing of follow-up observations needed to achieve and
    maintain phase-connected timing solutions. It incorporates a detailed noise
    budget and calculates expected uncertainties in pulsar spin parameters.
    """

    def __init__(self, setup, pulsar_catalog):
        """
        Initializes the AnalyticCadence class.

        Args:
            setup (PulsarSimulationSetup): An object containing telescope and
                                           simulation parameters.
            pulsar_catalog (pd.DataFrame): A DataFrame with the synthetic
                                           pulsar population.
        """
        self.setup = setup
        self.pulsar_catalog = pulsar_catalog
        self.database_path = setup.database_path

        # Fixed noise budget contributions in microseconds (us) for each population
        # These are estimates and will be refined in simulation.
        self.fixed_noise_budget_us = {
            # pop_type: [sigma_jit, sigma_ism, sigma_red, sigma_inst, sigma_clk, sigma_sse, sigma_gwb]
            "msp":            [0.1, 0.2, 0.05, 0.1, 0.05, 0.03, 0.02],
            "young":          [10.0, 2.0, 0.05, 0.1, 0.05, 0.03, 0.02],
            "magnetar":       [1000.0, 10.0, 0.1, 0.1, 0.05, 0.03, 0.02],
            "high_b":         [50.0, 5.0, 0.05, 0.1, 0.05, 0.03, 0.02],
            "intermittent":   [20.0, 3.0, 0.05, 0.1, 0.05, 0.03, 0.02],
            "galactic_center":[100.0, 500.0, 0.1, 0.1, 0.05, 0.03, 0.02]
        }

    def calculate_sigma_rad(self, s_mean_mjy, p_sec, w_sec, t_int_sec):
        """
        Calculates the radiometer noise contribution to TOA uncertainty.

        Args:
            s_mean_mjy (float): Mean flux density of the pulsar in mJy.
            p_sec (float): Period of the pulsar in seconds.
            w_sec (float): Effective pulse width of the pulsar in seconds.
            t_int_sec (float): Integration time of the observation in seconds.

        Returns:
            float: Radiometer noise (sigma_rad) in seconds.
        """
        s_mean_jy = s_mean_mjy * 1e-3
        sefd = self.setup.telescope_params["SEFD"]["value"]  # Jy
        n_pol = self.setup.search_params["common"]["n_pol"]
        delta_nu = self.setup.telescope_params["survey_band_bw"]["value"]  # Hz

        # Avoid division by zero or negative sqrt for very wide pulses
        if w_sec >= p_sec:
            w_sec = p_sec * 0.5
        
        snr_term = s_mean_jy * np.sqrt(n_pol * delta_nu * t_int_sec) / sefd
        if snr_term == 0:
            return np.inf

        # Radiometer error formula from Lorimer & Kramer, Handbook of Pulsar Astronomy
        # Handle case where w_sec is very close to p_sec
        denominator = p_sec - w_sec
        if denominator <= 0:
            return np.inf
        sigma_rad = (p_sec / snr_term) * np.sqrt(w_sec / denominator)
        return sigma_rad

    def get_total_toa_uncertainty(self, pulsar, t_int_sec):
        """
        Calculates the total TOA uncertainty by combining all noise sources.

        Args:
            pulsar (pd.Series): A row from the pulsar catalog DataFrame.
            t_int_sec (float): The integration time for the observation.

        Returns:
            float: The total TOA uncertainty (sigma_total) in seconds.
        """
        pop_type = pulsar["population_type"]
        
        # Radiometer noise in seconds
        sigma_rad_s = self.calculate_sigma_rad(
            pulsar["S1400"], pulsar["P"], pulsar["W"], t_int_sec
        )

        # Fixed noise contributions in seconds
        noise_values_us = self.fixed_noise_budget_us.get(pop_type, [0]*7)
        noise_values_s = [n * 1e-6 for n in noise_values_us]
        
        # Sum all noise sources in quadrature
        sigma_total_sq = sigma_rad_s**2 + sum(n**2 for n in noise_values_s)
        
        return np.sqrt(sigma_total_sq)

    def calculate_timing_uncertainties(self, sigma_toa_s, n_epochs, t_span_s, p_sec):
        """
        Estimates uncertainties in P and P_dot after an initial campaign.

        Args:
            sigma_toa_s (float): Total TOA uncertainty per epoch in seconds.
            n_epochs (int): Number of observation epochs.
            t_span_s (float): Total time span of the campaign in seconds.
            p_sec (float): Pulsar period in seconds.

        Returns:
            tuple: A tuple containing (sigma_P, sigma_Pdot).
        """
        if n_epochs < 3 or t_span_s == 0:
            return (np.inf, np.inf)

        # Using approximate scaling relations for evenly spaced observations
        sigma_p = (1.1 * p_sec**2 * sigma_toa_s) / (t_span_s * np.sqrt(n_epochs))
        sigma_pdot = (3.4 * p_sec * sigma_toa_s) / (t_span_s**2 * np.sqrt(n_epochs))

        return sigma_p, sigma_pdot

    def calculate_max_interval(self, p_sec, sigma_p, sigma_pdot):
        """
        Calculates the max interval to the next observation to maintain phase.

        The phase uncertainty must be < 0.5 cycles. This is solved by finding
        the positive root of the quadratic equation:
        0.5 * (sigma_Pdot/P^2) * dt^2 + (sigma_P/P^2) * dt - 0.5 = 0

        Args:
            p_sec (float): Pulsar period in seconds.
            sigma_p (float): Uncertainty in period.
            sigma_pdot (float): Uncertainty in period derivative.

        Returns:
            float: The maximum time interval (delta_t_max) in days.
        """
        if p_sec == 0 or np.isinf(sigma_p) or np.isinf(sigma_pdot):
            return 0

        # Coefficients of the quadratic equation for delta_t
        a = 0.5 * sigma_pdot / p_sec**2
        b = sigma_p / p_sec**2
        c = -0.5

        # Handle cases to avoid division by zero and other errors
        if b == 0:
            if a <= 0:
                return np.inf  # No real positive solution
            delta_t_s = np.sqrt(-c / a)
        elif a == 0 or abs(a / b) < 1e-9:  # Linear approximation is sufficient
            delta_t_s = -c / b
        else:
            discriminant = b**2 - 4 * a * c
            if discriminant < 0:
                return 0  # No real solution, phase connection already lost
            
            # Positive root of the quadratic formula
            delta_t_s = (-b + np.sqrt(discriminant)) / (2 * a)

        return delta_t_s / (24.0 * 3600.0)  # Convert seconds to days

    def develop_cadence_prescriptions(self):
        """
        Develops and prints cadence prescriptions for each sub-population.
        """
        print("--- Analytic Cadence Prescriptions by Population ---")
        
        all_results = []

        for pop_type in self.pulsar_catalog['population_type'].unique():
            pop_df = self.pulsar_catalog[self.pulsar_catalog['population_type'] == pop_type]
            if pop_df.empty:
                continue

            # Use the median pulsar as a representative for the population
            rep_pulsar = pop_df.median(numeric_only=True)
            rep_pulsar['population_type'] = pop_type  # Add back pop_type field

            # --- Initial Characterization Campaign ---
            # Assume 3 epochs at Day 0, Day 3, Day 10
            n_epochs = 3
            t_span_days = 10.0
            t_span_s = t_span_days * 24 * 3600

            # Determine required integration time for follow-ups to get S/N > 20
            t_int_followup_s = 60.0  # Start with 1 minute
            while self.calculate_sigma_rad(rep_pulsar["S1400"], rep_pulsar["P"], rep_pulsar["W"], t_int_followup_s) > rep_pulsar["P"] / 20.0:
                t_int_followup_s *= 1.5
                if t_int_followup_s > self.setup.search_params['targeted']['t_dwell_max']:
                    t_int_followup_s = self.setup.search_params['targeted']['t_dwell_max']
                    break
            
            # Calculate total TOA uncertainty for a typical follow-up
            sigma_toa_s = self.get_total_toa_uncertainty(rep_pulsar, t_int_followup_s)

            # Calculate expected P, Pdot uncertainties after the initial campaign
            sigma_p, sigma_pdot = self.calculate_timing_uncertainties(
                sigma_toa_s, n_epochs, t_span_s, rep_pulsar["P"]
            )

            # Calculate the recommended ongoing cadence
            delta_t_max_days = self.calculate_max_interval(rep_pulsar["P"], sigma_p, sigma_pdot)

            # Store results
            result = {
                'population_type': pop_type,
                'P_median_s': rep_pulsar['P'],
                'Pdot_median_ss': rep_pulsar['P_dot'],
                'S1400_median_mJy': rep_pulsar['S1400'],
                'DM_median_pccm3': rep_pulsar['DM'],
                't_int_followup_s': t_int_followup_s,
                'sigma_toa_us': sigma_toa_s * 1e6,
                'sigma_P_ns': sigma_p * 1e9,
                'sigma_Pdot_1e-15': sigma_pdot / 1e-15,
                'recommended_cadence_days': delta_t_max_days
            }
            all_results.append(result)

            # --- Print Summary for this Population ---
            print("\n" + "="*50)
            print("Population: " + pop_type.upper())
            print("="*50)
            print("Representative Pulsar (Median Values):")
            print("  P: " + ("%0.4f" % rep_pulsar['P']) + " s")
            print("  P_dot: " + ("%0.2e" % rep_pulsar['P_dot']) + " s/s")
            print("  S1400: " + ("%0.2f" % rep_pulsar['S1400']) + " mJy")
            print("  DM: " + ("%0.1f" % rep_pulsar['DM']) + " pc cm^-3")
            
            print("\nNoise Budget & Observation Parameters:")
            print("  Recommended Follow-up Integration Time: " + ("%0.1f" % t_int_followup_s) + " s")
            print("  Resulting Total TOA Uncertainty (sigma_toa): " + ("%0.2f" % (sigma_toa_s * 1e6)) + " us")
            
            noise_budget_us = self.fixed_noise_budget_us.get(pop_type, [])
            sigma_rad_us = self.calculate_sigma_rad(rep_pulsar["S1400"], rep_pulsar["P"], rep_pulsar["W"], t_int_followup_s) * 1e6
            print("    - Radiometer Noise: " + ("%0.2f" % sigma_rad_us) + " us")
            print("    - Jitter Noise:     " + ("%0.2f" % noise_budget_us[0]) + " us")
            print("    - ISM Noise:        " + ("%0.2f" % noise_budget_us[1]) + " us")

            print("\nInitial Campaign (3 Epochs over 10 days):")
            print("  Expected sigma_P: " + ("%0.2f" % (sigma_p * 1e9)) + " ns")
            print("  Expected sigma_Pdot: " + ("%0.4f" % (sigma_pdot / 1e-15)) + " (x 10^-15 s/s)")

            print("\n--- CADENCE RECOMMENDATION ---")
            print("  Max Interval for Next Observation: " + ("%0.1f" % delta_t_max_days) + " days")
            print("="*50)

        # Save detailed results to CSV
        results_df = pd.DataFrame(all_results)
        output_file = os.path.join(self.database_path, "analytic_cadence_recommendations.csv")
        results_df.to_csv(output_file, index=False)
        print("\nFull analytic cadence recommendations saved to: " + output_file)
        print("\nSummary of recommendations:")
        print(results_df.to_string())


if __name__ == "__main__":
    # 1. Initialize the simulation setup
    sim_setup = PulsarSimulationSetup()

    # 2. Load the synthetic pulsar population
    pulsar_catalog_file = os.path.join(sim_setup.database_path, "synthetic_pulsar_population.csv")
    if not os.path.exists(pulsar_catalog_file):
        print("Error: Synthetic pulsar catalog not found at " + pulsar_catalog_file)
        print("Please run the pulsar_simulation_setup.py script first.")
    else:
        pulsar_catalog_df = pd.read_csv(pulsar_catalog_file)

        # 3. Develop and display analytic cadence prescriptions
        cadence_analyzer = AnalyticCadence(sim_setup, pulsar_catalog_df)
        cadence_analyzer.develop_cadence_prescriptions()