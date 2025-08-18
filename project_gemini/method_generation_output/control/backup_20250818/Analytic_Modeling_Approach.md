<!-- filename: Analytic_Modeling_Approach.md -->
# Analytic Modeling Approach for Adaptive Cadence Recommendations

## 1. Analytic Estimation of Epoch Number and Spacing

The analytic framework for determining the number and spacing of follow-up epochs is based on the requirement to maintain phase connection—i.e., unambiguous pulse numbering—across the timing campaign. For each sub-population, the following steps are performed:

- **Initial Characterization Phase:**  
  Immediately after discovery, the pulsar’s period (P), period derivative (Ṗ), and initial S/N are estimated from the real-time search. The uncertainty in P and Ṗ, combined with the expected noise contributions, sets the maximum allowable interval (Δt) between follow-up epochs to avoid phase wraps:
  
  <code>
  Δt_max ≈ (1/2) × [σ_P / P + (1/2) σ_Ṗ × Δt / P]⁻¹
  </code>
  
  where σ_P and σ_Ṗ are the uncertainties in period and period derivative, respectively, including all noise sources.

- **Adaptive Cadence Phase:**  
  As timing residuals are accumulated, the cadence is dynamically adjusted. The interval between epochs is increased as the timing solution stabilizes, but is reduced if phase ambiguities or increased noise are detected. The analytic model prescribes a minimum number of epochs (N_min) and a maximum spacing (Δt_max) for each sub-population, based on their characteristic noise and variability.

## 2. Noise Contributors and Their Incorporation

Each noise source is explicitly modeled in the analytic framework:

- **Radiometer Noise (σ_rad):**  
  Determined by the system equivalent flux density (SEFD), bandwidth (Δν), integration time (t_int), and pulse width (W):
  <code>
  σ_rad ≈ SEFD / [√(n_pol × Δν × t_int)] × (W / (P - W))^0.5
  </code>
  Parameters: SEFD = 1.41–2.25 Jy, Δν ≈ 325 MHz (bottom 25% of 0.7–2 GHz), n_pol = 1, t_int = dwell time (60–1260 s).

- **Template Mismatch (σ_temp):**  
  Modeled as a fraction of σ_rad, typically 10–20% for high S/N profiles.

- **Pulse Jitter (σ_jit):**  
  Scales with the square root of the number of pulses averaged; more significant for MSPs and low S/N sources.

- **ISM Effects (σ_ISM):**  
  Includes DM variations and scattering. For high-DM or Galactic-center pulsars, σ_ISM can dominate and is modeled using empirical scaling relations (e.g., σ_DM ∝ DM^1.5, σ_scatt ∝ DM^2.2).

- **Red Timing Noise (σ_red):**  
  Modeled as a power-law process, with amplitude and spectral index drawn from population studies. Particularly important for young and high-B pulsars.

- **Glitches (σ_glitch):**  
  For young pulsars, glitch rates and amplitudes are incorporated probabilistically, with cadence adjusted to rapidly recover phase connection post-glitch.

- **Instrumental/Array/Clock Noise (σ_inst, σ_clk):**  
  Set by backend stability and array calibration; typically subdominant but included as a constant floor.

- **Solar-system Ephemeris and GWB (σ_SSE, σ_GWB):**  
  Relevant for MSPs; included as additional red noise terms.

The total timing uncertainty per epoch is the quadrature sum of all contributors:
<code>
σ_total^2 = σ_rad^2 + σ_temp^2 + σ_jit^2 + σ_ISM^2 + σ_red^2 + σ_glitch^2 + σ_inst^2 + σ_clk^2 + σ_SSE^2 + σ_GWB^2
</code>

## 3. Parameter Ranges and Consistency

All analytic calculations use parameter ranges directly from the telescope and search tables:

- **Telescope:** 1650 antennas, 6.15 m diameter, SEFD 1.41–2.25 Jy, Tsys/η 25–40 K, FoV 7 deg² at 1.35 GHz.
- **Backend:** 288 GB HBM4 per NVL144 rack, 50 PFLOPs compute, 13 TB/s bandwidth.
- **Survey:** Dwell time 60 s (blind) or 1260 s (targeted), 2500 channels, 0.1 ms time resolution, 500 DM trials.

## 4. Population Synthesis and Discovery S/N

Population synthesis fractions (from psrpoppy or similar) are used to weight the expected discovery rates per sub-population. The initial S/N from the discovery observation sets the minimum integration time required for subsequent epochs to achieve a target S/N (typically S/N > 10 for reliable TOAs), which in turn constrains the minimum feasible cadence.

## 5. Telescope and Backend Constraints

- **Dwell Time:**  
  Maximum per pointing is set by backend memory (60 s blind, 1260 s targeted).
- **S/N Requirements:**  
  Epoch spacing is adjusted to ensure each follow-up achieves sufficient S/N for phase connection, given the source flux and noise budget.
- **Memory and Compute:**  
  The number of beams, channels, and DM/acceleration trials are set to avoid exceeding backend memory during real-time search.

## 6. Sub-population-Specific Cadence Prescriptions

- **Young Pulsars:**  
  Dense initial cadence (e.g., 3–5 epochs in first week, then weekly), with rapid response to glitches.
- **MSPs:**  
  Regular cadence (e.g., every 2–4 days initially, then biweekly), with ISM monitoring.
- **Magnetars/High-B:**  
  Flexible, high-cadence during active phases, adaptive to emission state.
- **Intermittent/Nullers:**  
  Opportunistic, high-cadence during detected emission windows.
- **Galactic-center:**  
  Cadence set by ISM-induced phase loss timescale.

These analytic prescriptions are validated and refined through simulation, ensuring consistency with all telescope and backend constraints.