# Methodology

### Framework Overview

The efficient follow-up of newly discovered pulsars is hampered by initial uncertainty in their physical characteristics. Fixed, pre-determined observational cadences are inherently sub-optimal, as a schedule ideal for a stable millisecond pulsar is wasteful for a glitch-prone young pulsar, and vice-versa. This research develops and evaluates a self-correcting, adaptive cadence strategy that dynamically optimizes the scheduling of follow-up observations based on incoming data.

The core of this methodology is a Bayesian adaptive scheduling framework. This approach treats the follow-up campaign as a sequential decision problem. After each observation yields a new pulse time-of-arrival (TOA), the system uses Bayes' theorem to update the probability distributions of the pulsar's timing model parameters (e.g., spin frequency `ν` and its derivative `ν̇`). It then uses these updated distributions to forecast the pulsar's future behavior and intelligently schedules the *next* observation at the time that maximizes the expected scientific return, subject to the constraint of maintaining phase connection.

The central hypothesis is that this adaptive framework can achieve phase-connected timing solutions for a diverse population of newly discovered pulsars using significantly less total telescope time than the best-performing set of fixed-cadence strategies tailored to each pulsar sub-class. The methodology is designed to test this hypothesis through detailed, end-to-end simulations.

### Simulated Pulsar Population and Discovery

To provide a realistic testbed, a synthetic pulsar population is generated using the `psrpoppy` software package. The population is modeled to reflect the expected distribution of pulsar types in the Milky Way, including all specified sub-categories: young canonical pulsars, millisecond pulsars (MSPs), magnetars, high-B/transition objects, emission-intermittent classes (RRATs, nullers), and pulsars in the Galactic Center. Each simulated pulsar is endowed with intrinsic properties (`P`, `Ṗ`, luminosity, sky position) and the specific noise characteristics of its class.

The simulation begins by modeling the initial discovery of each pulsar in one of two survey modes:
1.  **Targeted Search:** A 1260-second, high-sensitivity pointing. This long dwell time yields a high signal-to-noise ratio (S/N) detection, a precise initial measurement of `ν`, and a weak but non-zero constraint on `ν̇`.
2.  **Blind Search:** A 60-second, lower-sensitivity pointing. This short dwell time results in a lower S/N detection, a less precise `ν` measurement, and provides no meaningful initial constraint on `ν̇`.

This discovery observation establishes the initial TOA and is used to construct the prior probability distributions for the timing model parameters, which form the starting point for the adaptive scheduling algorithm. The priors derived from a targeted search are significantly more constrained than those from a blind search.

### Timing and Noise Models

The timing analysis relies on a standard rotational model and a suite of stochastic noise models tailored to each pulsar sub-population.

**1. Standard Timing Model:**
The pulse phase `φ(t)` at a barycentric time `t` is modeled by a Taylor expansion around a reference epoch `t₀`:
`φ(t) = φ₀ + ν(t - t₀) + (1/2)ν̇(t - t₀)²`
The parameters to be fit are the spin frequency `ν` (Hz), its first derivative `ν̇` (Hz/s), astrometric position (`α`, `δ`), and Dispersion Measure (`DM`, pc cm⁻³).

**2. Sub-Population Noise Models:**
In addition to radiometer noise derived from the telescope's SEFD, the following dominant noise sources are simulated:
*   **Young Pulsars/Magnetars (Glitches):** Rotational instabilities are modeled as a Poisson process with a mean rate `λ_g` (0.1-0.5 yr⁻¹ for young pulsars, >1 yr⁻¹ for magnetars). Glitch magnitudes (`Δν/ν`) are drawn from a power-law distribution, with typical sizes of `10⁻⁹`–`10⁻⁶` for young pulsars and `10⁻⁶`–`10⁻⁴` for magnetars.
*   **Millisecond Pulsars (Red Noise & Jitter):** Intrinsic, low-frequency timing noise is modeled with a power-law spectral density `P(f) = A²(f/f_yr)^-γ`, where `A` is the amplitude and `γ` is the spectral index. Pulse-to-pulse jitter is added as a white noise term `σ_J` in quadrature with the radiometer noise of each TOA.
*   **High-B/Transition Objects:** Modeled with moderate glitch rates (`λ_g` ≈ 0.5-1.0 yr⁻¹) and a significant red noise component.
*   **Intermittent Emitters (RRATs/Nullers):** Emission is modeled as a two-state (ON/OFF) semi-Markov process, parameterized by the mean durations of the ON-state (`⟨τ_on⟩`) and OFF-state (`⟨τ_off⟩`). A valid TOA can only be obtained if the source is in the ON state.
*   **Galactic Center Pulsars (ISM Effects):** The dominant noise is environmental. DM variations are modeled as a random walk process. Extreme temporal scattering (`τ_scatt ∝ ν⁻⁴`) broadens the pulse profile, significantly increasing the TOA uncertainty `σ_TOA`.

### The Adaptive Scheduling Algorithm

The adaptive algorithm operates in a continuous loop of Bayesian inference and decision-making.
1.  **Propose:** Using the current posterior probability distributions for the timing parameters, the algorithm forecasts the evolution of uncertainty. It seeks to determine the optimal time for the next observation, `t_next`, by maximizing a utility function, `U(t_next)`. The utility is defined as the expected information gain on the spin-down rate, which is equivalent to minimizing the predicted uncertainty `σ_predicted(ν̇)`:
    `Utility(t_next) ∝ 1 / σ_predicted(ν̇ | t_next)`
    This optimization is performed under the critical constraint that phase connection must be maintained. The algorithm calculates the maximum time gap, `t_max`, before the extrapolated phase uncertainty `δφ` exceeds a threshold of 0.4 cycles. The search for `t_next` is restricted to `t_now < t_next ≤ t_now + t_max`. This logic forces the scheduler to lengthen the timing baseline as aggressively as possible without risking phase ambiguity.
2.  **Simulate:** The simulation advances the pulsar's true state to the proposed `t_next`, applying any stochastic events (glitches, DM changes) that occur in the intervening time. A new TOA is generated with realistic uncertainty.
3.  **Update:** The new TOA is incorporated into the dataset, and the posterior distributions of the timing model parameters are updated using a Bayesian fitting routine (e.g., MCMC). This refined posterior becomes the prior for the next iteration.
4.  **Iterate:** The loop repeats until a stopping condition is met.

### Performance Evaluation and Benchmarking

The effectiveness of the adaptive strategy is quantified by simulating its performance on the synthetic pulsar population and comparing it against a baseline of fixed-cadence strategies.

**Simulation Workflow and Metrics:**
For each pulsar drawn from the `psrpoppy` population, the discovery is simulated, and the adaptive scheduling loop is initiated. The simulation for each source terminates upon reaching one of the following conditions:
*   **Success:** The fractional uncertainty in the spin-down rate is reduced below a target threshold: `σ(ν̇) / |ν̇| < 0.1`.
*   **Failure:** Phase connection is lost, the cumulative observation time exceeds a 3-hour budget, or (for intermittent sources) 5 consecutive scheduled observations yield non-detections.

The primary performance metrics are the **phase-connection success rate** (fraction of pulsars successfully timed) and the **total telescope time** (sum of all dwell times) required to reach the success condition.

**Benchmark Fixed-Cadence Strategies:**
The adaptive scheduler's performance is compared to that of a set of expert-designed, fixed cadences, which represent the conventional follow-up approach. The same simulated pulsars are timed using these fixed schedules:
*   **Canonical/High-B Pulsars:** Logarithmically spaced observations at `t = 1, 3, 7, 15, 30, 60, 120` days post-discovery.
*   **Millisecond Pulsars:** A sparse cadence at `t = 3, 10, 30, 90, 180` days.
*   **Magnetars/GC Pulsars:** A dense initial cadence at `t = 1, 2, 4, 7, 14, 30, 60` days.
*   **Intermittent Pulsars:** A block-based cadence at `t = 1, 2, 3, 10, 17, 24, 31` days.

The final analysis will directly compare the success rates and total telescope time consumed by the adaptive algorithm versus the fixed strategies across the entire population and within each sub-class, thereby providing a quantitative measure of the adaptive framework's efficiency.