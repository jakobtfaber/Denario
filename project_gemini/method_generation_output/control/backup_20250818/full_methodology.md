<!-- filename: full_methodology.md -->

# Methodology: Unified Adaptive Cadence Framework for Phase-Connecting the Pulsar Census

## 1. Overview

This methodology details the stepwise implementation of a unified, adaptive observational cadence framework for achieving phase-connected timing solutions of newly discovered radio pulsars. The approach integrates analytic modeling and simulation, explicitly accounting for telescope, backend, and noise parameters, and is structured to maximize timing completeness and telescope efficiency across all major pulsar sub-populations.

---

## 2. Variable and Parameter Documentation

**Telescope/Instrumental Parameters:**
- $N_{\rm ant}$: Number of antennas (1650)
- $D_{\rm dish}$: Dish diameter (6.15 m)
- $\rm SEFD$: System Equivalent Flux Density (1.41–2.25 Jy)
- $T_{\rm sys}/\eta$: System temperature over efficiency (25–40 K)
- $\rm FoV$: Field of view (7 deg$^2$ at 1.35 GHz)
- $\Delta\nu$: Bandwidth (approx. 325 MHz, bottom 25% of 0.7–2 GHz)
- $t_{\rm dwell}$: Maximum dwell time (60 s blind, 1260 s targeted)
- $n_{\rm pol}$: Number of polarizations (1)
- $n_{\rm chan}$: Number of channels (2500)
- $\delta t$: Time resolution (0.1 ms)
- $n_{\rm DM}$: Number of DM trials (500)
- $n_{\rm acc}$: Number of acceleration trials (500 targeted, 5 blind)
- $n_{\rm bits}$: Number of bits (4)
- Backend: NVIDIA Vera Rubin NVL144, 288 GB HBM4 per rack, 50 PFLOPs compute

**Pulsar/Population Parameters:**
- $P$: Spin period (ms–s)
- $\dot{P}$: Period derivative
- $S_{\rm 1.4}$: Flux density at 1.4 GHz (mJy)
- $DM$: Dispersion measure (pc cm$^{-3}$)
- $W$: Pulse width (ms)
- Sub-population: Young, MSP, magnetar, high-B, intermittent, Galactic-center
- Population fractions: From psrpoppy or equivalent

**Noise Contributors:**
- $\sigma_{\rm rad}$: Radiometer noise
- $\sigma_{\rm temp}$: Template mismatch
- $\sigma_{\rm jit}$: Pulse jitter
- $\sigma_{\rm ISM}$: ISM/DM/scattering noise
- $\sigma_{\rm red}$: Red timing noise
- $\sigma_{\rm glitch}$: Glitch-induced phase noise
- $\sigma_{\rm inst}$: Instrumental/array noise
- $\sigma_{\rm clk}$: Clock noise
- $\sigma_{\rm SSE}$: Solar-system ephemeris error
- $\sigma_{\rm GWB}$: Gravitational wave background

---

## 3. Stepwise Methodology

### 3.1 Initial Characterization Phase

1. **Discovery and Parameter Extraction**
   - For each new pulsar, extract $P$, $\dot{P}$, $DM$, $S_{\rm 1.4}$, and initial S/N from real-time search output.
   - Assign sub-population based on $P$, $\dot{P}$, $DM$, and location.

2. **Analytic Cadence Prescription**
   - Calculate initial uncertainties ($\sigma_P$, $\sigma_{\dot{P}}$) using radiometer and template noise models:
     <code>
     \sigma_{\rm rad} \approx \frac{\rm SEFD}{\sqrt{n_{\rm pol} \Delta\nu t_{\rm int}}} \left(\frac{W}{P-W}\right)^{0.5}
     </code>
   - Estimate maximum safe interval between epochs ($\Delta t_{\rm max}$) to avoid phase wraps:
     <code>
     \Delta t_{\rm max} \approx \frac{1}{2} \left[ \frac{\sigma_P}{P} + \frac{1}{2} \frac{\sigma_{\dot{P}} \Delta t}{P} \right]^{-1}
     </code>
   - Set initial cadence: 3–5 epochs in first week (young/high-B), 2–4 days (MSP), opportunistic (intermittent), tailored for ISM (Galactic-center).

3. **Noise Budget Assembly**
   - For each source, sum all relevant noise terms in quadrature to obtain total TOA uncertainty per epoch:
     <code>
     \sigma_{\rm total}^2 = \sum_i \sigma_i^2
     </code>
   - Adjust integration time per epoch to ensure S/N $>$ 10, within $t_{\rm dwell}$ constraints.

---

### 3.2 Adaptive Cadence Adjustment

1. **Timing Solution Update**
   - After each epoch, update timing solution ($P$, $\dot{P}$, phase residuals) using standard timing software (e.g., TEMPO2, PINT).

2. **Dynamic Cadence Recalculation**
   - Recompute $\Delta t_{\rm max}$ and noise budget after each new TOA.
   - If phase uncertainty approaches 0.5 pulse, schedule next epoch sooner.
   - If timing solution stabilizes, increase interval between epochs.

3. **Sub-population-Specific Triggers**
   - For young/high-B: If glitch detected, trigger rapid follow-up (within 1–2 days).
   - For intermittent: If emission detected, schedule dense follow-up during active window.
   - For MSPs: Monitor ISM/DM; if excess residuals, increase cadence.

---

### 3.3 Simulation and Validation

1. **Synthetic Population Generation**
   - Use psrpoppy or equivalent to generate synthetic populations for each sub-category, with realistic $P$, $\dot{P}$, $DM$, $S_{\rm 1.4}$, and noise properties.

2. **Noise Realization and TOA Simulation**
   - For each synthetic pulsar, simulate TOAs by adding all relevant noise contributions per epoch.
   - Inject stochastic events (e.g., glitches, nulling) as appropriate.

3. **Timing Campaign Simulation**
   - Apply analytic cadence prescription for initial epochs.
   - Implement adaptive cadence logic as timing solution evolves.
   - Record whether phase connection is maintained, final parameter uncertainties, and total telescope time used.

4. **Evaluation Metrics**
   - Phase-connection success rate per sub-population.
   - Distributions of $\sigma_P$, $\sigma_{\dot{P}}$.
   - Telescope time per phase-connected source.
   - Comparison of adaptive vs. fixed-cadence strategies.

5. **Validation**
   - Compare simulation outputs to analytic predictions for each sub-population.
   - Identify and document any systematic discrepancies.
   - Refine analytic cadence prescriptions as needed.

---

### 3.4 Output Analysis and Documentation

1. **Results Compilation**
   - Tabulate phase-connection rates, timing uncertainties, and telescope time efficiency for each sub-population and survey mode.
   - Generate figures comparing analytic and simulation results.

2. **Documentation**
   - Archive all variable definitions, parameter values, and units.
   - Store synthetic timing datasets, cadence schedules, and evaluation metrics.

---

## 4. Final Review Checklist

- [ ] All variables and parameters are clearly defined with units.
- [ ] Analytic cadence prescriptions are derived for each sub-population.
- [ ] All relevant noise sources are included in both analytic and simulation models.
- [ ] Telescope and backend constraints are enforced in all calculations.
- [ ] Simulation workflow is implemented for each sub-population, with adaptive cadence logic.
- [ ] Phase-connection success rates, timing uncertainties, and telescope time usage are quantified and compared between analytic and simulation results.
- [ ] All outputs are documented, archived, and ready for analysis.

---

## 5. Integration of Analytic and Simulation Approaches

- Analytic models provide initial cadence and noise estimates, setting the baseline for simulation.
- Simulations validate and refine analytic prescriptions, ensuring robustness to real-world noise and variability.
- Iterative feedback between analytic and simulation components ensures optimal cadence strategies for all sub-populations, maximizing timing completeness and telescope efficiency.

---

This methodology is structured for direct implementation and ensures that all steps, from initial discovery to final output analysis, are rigorously documented and validated.