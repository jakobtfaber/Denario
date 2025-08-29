### Methodology

This study will evaluate the efficacy of a GPU-accelerated, adaptive observational cadence for achieving phase-connected timing solutions for newly discovered intermittent pulsars. The methodology is designed around a comparative analysis, pitting the proposed adaptive strategy against a traditional fixed-cadence approach within a high-fidelity simulation environment.

#### 1. Rationale, Hypotheses, and Feasibility

The primary challenge in timing intermittent pulsars (e.g., RRATs, nulling pulsars) is their unpredictable emission, which renders traditional, fixed-cadence observations highly inefficient and often unsuccessful. Large gaps between detections, caused by observations occurring during null states, prevent the unambiguous counting of pulsar rotations, a prerequisite for a phase-connected solution.

This research tests the hypothesis that an adaptive cadence, which uses quasi-real-time analysis to dynamically schedule follow-up observations based on the pulsar's emission state, will achieve significantly higher phase-connection completeness with greater telescope time efficiency than a fixed cadence.

The feasibility of this approach hinges on the ability to perform a full pulsar search analysis within the observation dwell time. Using the blind search parameters as a worst-case scenario (60 s dwell time), the required data ingestion rate is 2.5 TB/s (<code>2e5 beams * 2500 channels * 4 bits / 0.1 ms</code>). This is well within the **13 TB/s** memory bandwidth of the NVIDIA Vera Rubin NVL144 GPU rack. The computational load is estimated at ~480 TFLOPS, which is less than 1% of the rack's **50 PFLOPs** peak performance. This confirms that the analysis is memory-bound but computationally feasible, allowing for real-time feedback to a dynamic telescope scheduler.

#### 2. Simulation Framework and Cadence Algorithms

A synthetic population of 1,000 intermittent pulsars will be generated using <code>psrpoppy</code>, with distributions for period (P), period-derivative (Ṗ), nulling fraction (NF), and mean burst/null durations drawn from published statistics of the known RRAT and nuller populations. For each simulated pulsar, a set of "true" topocentric times-of-arrival (TOAs) will be generated over an 18-month campaign using <code>libstempo</code>.

Simulated observations will incorporate realistic noise sources. Radiometer noise for each TOA will be calculated based on the DSA-1650's System Equivalent Flux Density (SEFD) of 1.8 Jy (average). Additional noise terms will be injected, including: a) single-pulse jitter noise, b) red noise with parameters typical for young pulsars, and c) stochastic DM variations modeled as a random walk process to simulate ISM turbulence.

Two distinct cadence strategies will be simulated for each pulsar:

*   **Control Group (Fixed Cadence):** This strategy serves as the baseline. Each pulsar will be observed with a fixed cadence of one 20-minute observation every 14 days for the entire 18-month campaign, regardless of the outcome of previous observations.

*   **Experimental Group (Adaptive Cadence):** This strategy employs a state-based logic driven by real-time detection outcomes. A detection is defined as a signal-to-noise ratio (S/N) > 8.
    1.  **Initial Confirmation:** After discovery, three observations are scheduled within the first 7 days. A single detection transitions the source to the <code>Intensive Monitoring</code> state. Failure to detect in all three triggers the <code>Exponential Backoff</code> state.
    2.  **Intensive Monitoring:** The goal is to secure phase connection quickly. The source is observed every 2-3 days. After three consecutive detections, the source transitions to <code>Maintenance</code>. A non-detection triggers a re-observation within 24 hours; two consecutive non-detections revert the source to <code>Exponential Backoff</code>.
    3.  **Maintenance:** Once phase-connected, the cadence is relaxed to one observation every 21 days to maintain the solution efficiently. A non-detection immediately triggers a return to <code>Intensive Monitoring</code>.
    4.  **Exponential Backoff:** For non-detections, the time to the next observation is doubled, starting from an initial 7-day wait (i.e., 7 days, 14 days, 28 days...), up to a maximum of 60 days. A successful detection at any point immediately transitions the source to <code>Intensive Monitoring</code>.

#### 3. Performance Evaluation and Analysis

For each simulated pulsar, the TOAs collected under both strategies will be fitted to a timing model using the <code>PINT</code> software package. A solution will be considered successfully **phase-connected** if it meets two criteria over the 18-month baseline: the reduced chi-squared of the fit is < 1.5, and there are no cycle count ambiguities between observations.

The strategies will be compared using the following primary metrics, averaged over the population:
*   **Phase-Connection Completeness (%):** The fraction of pulsars for which a phase-connected solution was achieved.
*   **Parameter Precision:** The final fractional uncertainty on P (σ_P / P) and Ṗ (σ_Ṗ / Ṗ) for successfully timed pulsars.
*   **Total Telescope Time (hours):** The mean total observation time used per pulsar.