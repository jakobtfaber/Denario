<!-- filename: simulation_workflow_cadence.md -->
# Simulation Workflow for Validating and Refining Analytic Cadence Strategies

## 1. Simulation Inputs

### Pulsar Population Parameters
- **Population Synthesis:** Generate synthetic pulsar populations for each sub-category (young, MSP, magnetar, high-B, intermittent, Galactic-center) using distributions from psrpoppy or equivalent, including period (P), period derivative (Ṗ), dispersion measure (DM), scattering timescale, and flux density.
- **Population Fractions:** Weight each sub-population according to expected Galactic abundance and survey sensitivity.
- **Intrinsic Variability:** Assign sub-population-specific properties such as glitch rates (young, high-B), nulling/intermittency fractions (RRATs, nullers), and red noise amplitudes (young, magnetar, high-B).

### Noise Models
- **Radiometer Noise:** Calculate per-epoch using SEFD, bandwidth, integration time, and pulse width.
- **Template Mismatch and Jitter:** Model as additional white noise, scaling with S/N and pulse count.
- **ISM Effects:** Simulate DM variations and scattering using empirical scaling with DM and line-of-sight.
- **Red Noise:** Implement as a power-law process with amplitude and spectral index drawn from sub-population distributions.
- **Glitches:** For relevant populations, inject glitches stochastically based on observed rates and amplitudes.
- **Instrumental/Array/Clock Noise:** Add as a constant or slowly varying term, consistent with backend specs.
- **Solar-system Ephemeris and GWB:** For MSPs, include as additional red noise terms.

### Telescope/Instrumental Parameters
- **Array Configuration:** 1650 × 6.15 m dishes, SEFD 1.41–2.25 Jy, Tsys/η 25–40 K, 0.7–2 GHz band.
- **Backend Constraints:** Dwell time (60 s blind, 1260 s targeted), 2500 channels, 0.1 ms resolution, 500 DM trials, 288 GB HBM4 memory per NVL144 rack.
- **Survey Strategy:** Simulate both targeted (4000 beams) and blind (2e5 beams) search modes, with real-time detection and no search-mode data storage.

## 2. Timing Campaign Simulation

### Initial Characterization Phase
- For each synthetic discovery, simulate the initial follow-up epochs using analytic cadence prescriptions (from Step 2), ensuring S/N and integration time are consistent with telescope constraints.
- Generate synthetic TOAs by adding all relevant noise contributions to the true pulse phase.

### Adaptive Cadence Adjustment
- After each epoch, update the timing solution (P, Ṗ, phase residuals) using standard pulsar timing software (e.g., TEMPO2 or PINT).
- Dynamically adjust the interval to the next epoch based on:
  - Current phase uncertainty (to avoid phase wraps)
  - Detected increases in noise or phase residuals
  - Sub-population-specific triggers (e.g., post-glitch, emission state change)
- Continue until phase connection is achieved over a pre-defined campaign duration (e.g., 6–12 months) or until phase connection is lost.

### Sub-population-Specific Logic
- **Young/High-B:** Simulate glitch events and rapid cadence response.
- **MSPs:** Emphasize ISM monitoring and regular cadence.
- **Intermittent:** Model emission windows and opportunistic scheduling.
- **Galactic-center:** Include enhanced ISM noise and scattering.

## 3. Evaluation Metrics

- **Phase-Connection Success Rate:** Fraction of sources per sub-population achieving phase connection over the campaign.
- **Timing Uncertainties:** Distributions of final period and period derivative uncertainties (σ_P, σ_Ṗ).
- **Telescope Time Efficiency:** Total telescope time expended per phase-connected source.
- **Cadence Adaptivity Gain:** Improvement in success rate and/or efficiency compared to fixed-cadence baselines.

## 4. Validation Against Analytic Predictions

- For each sub-population, compare simulated phase-connection rates, timing uncertainties, and telescope time usage to analytic expectations.
- Identify discrepancies and iteratively refine analytic cadence prescriptions as needed.
- Document agreement and any systematic deviations, attributing causes (e.g., unmodeled noise, cadence inflexibility).

## 5. Sensitivity and Robustness Testing

- Systematically vary key noise parameters (e.g., increase red noise amplitude, ISM variability) and telescope constraints (e.g., reduce dwell time, increase SEFD).
- Re-run simulations to assess the robustness of adaptive cadence strategies.
- Quantify the impact on phase-connection rates and timing precision, ensuring that adaptive approaches consistently outperform fixed-cadence alternatives under a range of plausible conditions.

## 6. Documentation and Output

- Record all simulation parameters, variable definitions, and units.
- Archive synthetic timing datasets, cadence schedules, and evaluation metrics for each run.
- Summarize results in tables and figures, highlighting the performance of the adaptive framework across all sub-populations and survey strategies.