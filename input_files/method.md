## Detailed Methodology for the Analysis of Coupled Harmonic Oscillators

This document describes a step-by-step methodology for analyzing energy transfer dynamics and beat frequencies in coupled harmonic oscillators. The objective is to connect the theoretical predictions derived from the mathematical model with computational results, using a suite of quantitative and visualization techniques.

### 1. Theoretical Model and Mathematical Formulations

The foundation of the analysis is the set of coupled second-order differential equations that govern the motion of two harmonic oscillators:

  m · d²x₁/dt² + c · dx₁/dt + k · x₁ + k_c · (x₁ - x₂) = 0  
  m · d²x₂/dt² + c · dx₂/dt + k · x₂ + k_c · (x₂ - x₁) = 0

where:
- m: Mass of each oscillator.
- k: Individual spring constant.
- c: Damping coefficient.
- k_c: Coupling strength between oscillators.
- x₁(t) and x₂(t): Displacement time series for oscillator 1 and 2, respectively.

These equations provide a concrete basis for understanding the phenomena of energy transfer and the modulation (beat frequencies) arising in weak, strong, and intermediate coupling regimes. In particular, the interplay between k and k_c determines the emergence of symmetric (in-phase) and antisymmetric (out-of-phase) normal modes.

### 2. Simulation and Data Generation

Simulations are executed using a 4th order Runge-Kutta numerical integration scheme to solve the aforementioned differential equations. The simulation framework produces time series data for:
- Positions (x₁ and x₂)
- Velocities (derived from the displacement derivatives)
- Energy components (kinetic energy from ½ m·v² and potential energy from ½ k·x² including the coupling potential energy from ½ k_c·(x₁ − x₂)²)

Key simulation parameters include:
- Varying the coupling strength k_c to observe changes in dynamical behavior.
- Different initial conditions to probe synchronization versus phase lag effects.
- A fixed or varied damping coefficient c to balance energy dissipation with oscillatory behavior.

The simulation runtime is capped (e.g., total simulation time and chosen time step dt) to ensure that data generation completes on a standard laptop within 3 minutes.

### 3. Data Preprocessing

Once the simulation output is generated, preprocessing is performed:
- **Normalization:** Time series of positions, velocities, and energy are normalized (using z-score normalization) to bring them to a common numerical range. This is crucial for comparing signals across coupling regimes.
- **Smoothing and Filtering:** A low-pass filter (for instance, a moving average or Savitzky–Golay filter) is applied to remove small-scale numerical noise while preserving key features like beat modulation and energy fluctuations.
- **Windowing:** For frequency domain analysis, segments of the time series are multiplied with window functions (Hann or Blackman) to minimize spectral leakage during Fourier transformation.

### 4. Analysis Techniques

#### A. Fourier Analysis for Beat Frequency Identification

The Fourier Transform (using FFT) converts the time-domain signals (positions) into the frequency domain:
- **Process:** Compute the power spectral density (PSD) for each oscillator’s displacement.
- **Rationale:** The resulting spectrum is analyzed to identify peak frequencies, frequency splitting, and sidebands that correspond to beat phenomena. When oscillators are coupled, slight differences in natural frequencies produce beat patterns.
- **Comparative Analysis:** The derived frequency spectra are compared across different k_c values to observe systematic shifts in dominant frequencies and amplitude modulations, providing quantitative validation of the energy transfer mechanism.

#### B. Energy Dynamics and Transfer Rate Estimation

- **Energy Time Series:** Total, kinetic, and potential energy are calculated as functions of time.  
  Kinetic Energy: ½ m (v₁² + v₂²)  
  Potential Energy: ½ k (x₁² + x₂²) + ½ k_c (x₁ - x₂)²
- **Rate of Change:** The temporal derivative (or finite differences) of the energy data is computed to quantify instantaneous energy transfer rates.
- **Rationale:** Comparing energy exchange dynamics across different coupling strengths allows identification of regimes in which energy is exchanged rapidly (indicative of strong coupling) or with slower modulation (typical in weak coupling).

#### C. Phase Space Visualization and Poincaré Analysis

- **Phase Portraits:** Plot x vs. v for each oscillator. This visualization highlights trajectory patterns such as limit cycles or convergent behavior.
- **Poincaré Sections:** By extracting points at specific events (for instance, when x crosses zero from negative to positive), a Poincaré map is constructed to reduce the continuous dynamics to a discrete set. This helps in identifying periodic or quasi-periodic orbits and possible phase locking.
- **Rationale:** Both trajectories and Poincaré sections are used to validate the synchronization dynamics and the modulation regimes predicted by theory.

#### D. Dimensional Reduction and Mode Decomposition

- **Principal Component Analysis (PCA):** PCA is applied to the concatenated time series data (positions, velocities, energy profiles) to extract the dominant modes of variability.
- **Interpretation:** The principal components are mapped back to physical modes along symmetric (in-phase) and antisymmetric (out-of-phase) axes. This mapping aids in interpreting the appearance of beat frequencies as a consequence of mixing these modal contributions.
- **Rationale:** Dimensional reduction helps in simplifying complex inter-oscillator dynamics without losing critical information about energy transfer trends.

### 5. Workflow Summary

1. **Data Loading:** Retrieve simulation data from the saved `.npz` file.
2. **Preprocessing:** Normalize and smooth the time series; apply window functions as necessary.
3. **Fourier Analysis:** Compute FFT and analyze spectral components to detail beat frequencies.
4. **Energy Analysis:** Plot energy evolution and compute its derivatives to quantify energy transfer rates.
5. **Phase Space Reconstruction:** Generate phase portraits and Poincaré sections for both oscillators.
6. **Dimensional Reduction:** Perform PCA for identifying dominant modes and validate connections with theoretical modes.

### 6. Extensions for More Complex Systems

To extend this methodology while remaining within computational constraints:
- **Multiple Coupled Oscillators:** The simulation framework can be generalized to systems with more oscillators by constructing higher-dimensional state vectors and coupling matrices. The analysis pipeline (Fourier analysis, phase space visualization, PCA) remains largely applicable.
- **Non-linear Coupling:** Incorporate non-linear coupling terms (e.g., cubic or quadratic interactions) into the equations of motion. Advanced integration schemes and modifications in the preprocessing (e.g., more robust filtering) may be required.
- **Hybrid Analysis Techniques:** For both extended systems, consider combining time–frequency methods (such as wavelet transforms) with PCA to capture transient phenomena and non-stationary beat patterns.

### Conclusion

This methodology provides a robust workflow that leverages numerical simulations, Fourier-based spectral analysis, energy dynamics computations, phase space visualizations, and dimensional reduction techniques. The combination of these methods allows for a detailed and quantitative connection between the theoretical model of coupled harmonic oscillators and the computationally generated data. The outlined approach is readily extendable to investigate more complex systems, ensuring that the fundamental physics of energy transfer and beat phenomena are accurately captured and analyzed within practical computational constraints.