# filename: codebase/pulsar_simulation_setup.py
import os
import numpy as np
import pandas as pd
import json


class PulsarSimulationSetup:
    """
    A class to define, document, and manage parameters for pulsar timing simulations.

    This class holds telescope, backend, search, noise, and pulsar population
    parameters. It also includes methods to generate synthetic pulsar populations
    based on these parameters.
    """

    def __init__(self):
        """
        Initializes the class by defining all relevant parameters.
        """
        self.database_path = "data/"
        if not os.path.exists(self.database_path):
            os.makedirs(self.database_path)

        # Telescope and Instrumental Parameters
        self.telescope_params = {
            "N_ant": {"value": 1650, "unit": "antennas", "description": "Number of antennas"},
            "D_dish": {"value": 6.15, "unit": "m", "description": "Dish diameter"},
            "FoV": {"value": 7, "unit": "deg^2", "description": "Field of view at 1.35 GHz"},
            "SEFD": {"value": 1.83, "unit": "Jy", "description": "Array SEFD at boresight (average)"},
            "T_sys_eta": {"value": 32.5, "unit": "K", "description": "System temperature over efficiency (average)"},
            "band_low": {"value": 0.7, "unit": "GHz", "description": "Band lower frequency"},
            "band_high": {"value": 2.0, "unit": "GHz", "description": "Band upper frequency"},
            "survey_band_bw": {"value": 325e6, "unit": "Hz", "description": "Survey bandwidth (bottom 25%)"},
            "n_chan_total": {"value": 10000, "unit": "", "description": "Total number of channels"},
        }

        # Fiducial Search Parameters
        self.search_params = {
            "targeted": {
                "n_beams": 4000,
                "n_chan": 2500,
                "t_dwell_max": 1260, # s
                "dt": 0.0001, # s
                "n_accel": 500,
            },
            "blind": {
                "n_beams": 200000,
                "n_chan": 2500,
                "t_dwell_max": 60, # s
                "dt": 0.0001, # s
                "n_accel": 5,
            },
            "common": {
                "n_dm_trials": 500,
                "n_pol": 1,
                "n_bits": 4,
                "p_range_min": 0.001, # s
                "p_range_max": 5.0, # s
            }
        }

        # Backend Parameters
        self.backend_params = {
            "name": "NVIDIA Vera Rubin NVL144",
            "memory_per_rack": 288, # GB
            "memory_bw": 13, # TB/s
            "compute": 50, # PFLOPs (FP4)
        }

        # Noise Contributor Placeholders
        self.noise_params = {
            "sigma_rad": {"description": "Radiometer noise (calculated per observation)"},
            "sigma_temp": {"description": "Template mismatch noise"},
            "sigma_jit": {"description": "Pulse jitter noise (stochastic)"},
            "sigma_ism": {"description": "ISM/DM/scattering noise"},
            "sigma_red": {"description": "Red timing noise"},
            "sigma_glitch": {"description": "Glitch-induced phase noise"},
            "sigma_inst": {"description": "Instrumental/array noise"},
            "sigma_clk": {"description": "Clock noise"},
            "sigma_sse": {"description": "Solar-system ephemeris error"},
            "sigma_gwb": {"description": "Gravitational wave background noise"},
        }

        # Pulsar Sub-population Parameters for Synthetic Generation
        # Using log-normal distributions: params are (mean_log, sigma_log)
        self.population_params = {
            "young": {
                "fraction": 0.70,
                "P_dist": {"mean": np.log10(0.5), "std": 0.5}, # log10(s)
                "Pdot_dist": {"mean": np.log10(1e-15), "std": 1.0}, # log10(s/s)
                "S1400_dist": {"mean": np.log10(1.0), "std": 0.7}, # log10(mJy)
                "DM_dist": {"mean": np.log10(100), "std": 0.4}, # log10(pc cm^-3)
            },
            "msp": {
                "fraction": 0.05,
                "P_dist": {"mean": np.log10(0.005), "std": 0.4}, # log10(s)
                "Pdot_dist": {"mean": np.log10(1e-20), "std": 0.8}, # log10(s/s)
                "S1400_dist": {"mean": np.log10(0.5), "std": 0.6}, # log10(mJy)
                "DM_dist": {"mean": np.log10(50), "std": 0.5}, # log10(pc cm^-3)
            },
            "magnetar": {
                "fraction": 0.01,
                "P_dist": {"mean": np.log10(8.0), "std": 0.2}, # log10(s)
                "Pdot_dist": {"mean": np.log10(1e-11), "std": 0.5}, # log10(s/s)
                "S1400_dist": {"mean": np.log10(0.2), "std": 0.5}, # log10(mJy)
                "DM_dist": {"mean": np.log10(500), "std": 0.3}, # log10(pc cm^-3)
            },
            "high_b": {
                "fraction": 0.04,
                "P_dist": {"mean": np.log10(2.0), "std": 0.5}, # log10(s)
                "Pdot_dist": {"mean": np.log10(1e-13), "std": 0.7}, # log10(s/s)
                "S1400_dist": {"mean": np.log10(0.8), "std": 0.6}, # log10(mJy)
                "DM_dist": {"mean": np.log10(300), "std": 0.4}, # log10(pc cm^-3)
            },
            "intermittent": {  # Includes RRATs, nullers
                "fraction": 0.15,
                "P_dist": {"mean": np.log10(1.0), "std": 0.6}, # log10(s)
                "Pdot_dist": {"mean": np.log10(1e-14), "std": 1.2}, # log10(s/s)
                "S1400_dist": {"mean": np.log10(5.0), "std": 0.8}, # log10(mJy, peak flux)
                "DM_dist": {"mean": np.log10(150), "std": 0.5}, # log10(pc cm^-3)
                "duty_cycle_dist": {"mean": 0.1, "std": 0.05}, # fraction
            },
            "galactic_center": {
                "fraction": 0.05,
                "P_dist": {"mean": np.log10(0.8), "std": 0.6}, # log10(s)
                "Pdot_dist": {"mean": np.log10(1e-14), "std": 1.0}, # log10(s/s)
                "S1400_dist": {"mean": np.log10(0.3), "std": 0.5}, # log10(mJy)
                "DM_dist": {"mean": np.log10(1000), "std": 0.2}, # log10(pc cm^-3)
            }
        }

    def document_parameters(self):
        """
        Prints all defined parameters to the console in a structured format.
        """
        print("--- Telescope and Instrumental Parameters ---")
        print(json.dumps(self.telescope_params, indent=4))
        print("\n--- Fiducial Search Parameters ---")
        print(json.dumps(self.search_params, indent=4))
        print("\n--- Backend Parameters ---")
        print(json.dumps(self.backend_params, indent=4))
        print("\n--- Noise Contributor Placeholders ---")
        print(json.dumps(self.noise_params, indent=4))
        print("\n--- Pulsar Sub-population Synthesis Parameters ---")
        print(json.dumps(self.population_params, indent=4))
        print("\n" + "=" * 50 + "\n")

    def generate_synthetic_population(self, n_pulsars, pop_type):
        """
        Generates a synthetic pulsar population for a given type.

        Args:
            n_pulsars (int): The number of pulsars to generate.
            pop_type (str): The key for the population type in self.population_params.

        Returns:
            pandas.DataFrame: A DataFrame containing the synthetic pulsar data.
        """
        params = self.population_params[pop_type]
        
        # Generate parameters from log-normal distributions
        p = 10 ** np.random.normal(params["P_dist"]["mean"], params["P_dist"]["std"], n_pulsars)
        p_dot = 10 ** np.random.normal(params["Pdot_dist"]["mean"], params["Pdot_dist"]["std"], n_pulsars)
        s1400 = 10 ** np.random.normal(params["S1400_dist"]["mean"], params["S1400_dist"]["std"], n_pulsars)
        dm = 10 ** np.random.normal(params["DM_dist"]["mean"], params["DM_dist"]["std"], n_pulsars)

        # Derived and other parameters
        w = p * np.random.uniform(0.01, 0.1, n_pulsars)  # Pulse width as 1-10% of Period
        b_surf = 3.2e19 * np.sqrt(p * p_dot)  # Surface magnetic field in Gauss
        tau_char = p / (2 * p_dot) / (365.25 * 24 * 3600)  # Characteristic age in years

        df_data = {
            "P": p,  # s
            "P_dot": p_dot,  # s/s
            "S1400": s1400,  # mJy
            "DM": dm,  # pc cm^-3
            "W": w,  # s
            "B_surf": b_surf,  # G
            "tau_char": tau_char,  # yr
            "population_type": pop_type
        }

        if pop_type == "intermittent":
            duty_cycle = np.random.normal(params["duty_cycle_dist"]["mean"], params["duty_cycle_dist"]["std"], n_pulsars)
            df_data["duty_cycle"] = np.clip(duty_cycle, 0.001, 1.0)
            df_data["activity_state"] = np.random.choice([0, 1], size=n_pulsars, p=[0.5, 0.5])

        return pd.DataFrame(df_data)


if __name__ == "__main__":
    # 1. Initialize and document all parameters
    setup = PulsarSimulationSetup()
    print("Initializing simulation setup and documenting parameters...")
    setup.document_parameters()

    # 2. Generate synthetic populations for each sub-category
    print("Generating synthetic pulsar populations...")
    total_pulsars_to_simulate = 10000
    all_pulsars_df = []

    for pop_type, params in setup.population_params.items():
        n_pop = int(total_pulsars_to_simulate * params["fraction"])
        print("Generating " + str(n_pop) + " pulsars of type: " + pop_type)
        pop_df = setup.generate_synthetic_population(n_pop, pop_type)
        all_pulsars_df.append(pop_df)

    # 3. Combine into a single DataFrame
    pulsar_catalog = pd.concat(all_pulsars_df, ignore_index=True)

    # 4. Document and save the generated population data
    output_file = os.path.join(setup.database_path, "synthetic_pulsar_population.csv")
    pulsar_catalog.to_csv(output_file, index=False)

    print("\n--- Synthetic Pulsar Population Summary ---")
    print("Total number of pulsars generated: " + str(len(pulsar_catalog)))
    print("Data saved to: " + output_file)
    
    print("\nPopulation distribution:")
    print(pulsar_catalog['population_type'].value_counts())
    
    print("\nDataframe Info:")
    pulsar_catalog.info()
    
    print("\nDescriptive Statistics of the Full Catalog:")
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_columns', 15)
    print(pulsar_catalog.describe())
