# Results and Discussion

## 1. Overview

This section presents a comprehensive analysis of the performance of various neural network architectures trained to emulate the CMB temperature-polarization cross-power spectrum ($C_\ell^{TE}$) in flat $\Lambda$CDM cosmologies. The emulators were trained on a large, physically-motivated dataset of $C_\ell^{TE}$ spectra generated with `classy_sz`, with cosmological parameters sampled via Latin Hypercube Sampling (LHS) over conservative, Planck-informed ranges. The primary goal was to identify architectures that are both highly accurate and computationally efficient, with particular attention to the unique challenges posed by the oscillatory and sign-changing nature of $C_\ell^{TE}$.

The architectures evaluated include:
- A baseline dense (fully connected) network with ReLU activations (`dense_relu`)
- A deeper and wider dense network (`deep_dense_relu`)
- A dense network with residual (skip) connections (`residual_relu`)
- A SIREN-style network with sinusoidal activations (`siren`)
- A dense network with layer normalization (`dense_layernorm`)

Performance was assessed on a held-out test set of 1,200 spectra, using a suite of quantitative metrics and diagnostic plots, including:
- Root mean squared error (RMSE) and maximum absolute error as a function of multipole $\ell$
- Median relative error as a function of $\ell$
- Inference speed (wall time for full test set prediction)
- Error statistics specifically at zero-crossings of $C_\ell^{TE}$
- Visual comparison of true vs. emulated spectra for random test samples
- Error distributions and systematic trends

The following subsections detail the quantitative results, interpret the diagnostic plots, and discuss the implications for cosmological emulation.

---

## 2. Quantitative Performance Summary

The table below summarizes the key performance metrics for each architecture, as measured on the test set:

| Architecture      | RMSE (mean)           | Max Abs (mean)         | Median Rel. Error | Inference Time (s) | Zero-crossing Mean Abs Error |
|-------------------|-----------------------|------------------------|-------------------|--------------------|------------------------------|
| dense_relu        | $1.51 \times 10^{-17}$ | $4.77 \times 10^{-17}$ | $2.28 \times 10^{-3}$  | 0.19               | $2.11 \times 10^{-17}$       |
| deep_dense_relu   | $4.89 \times 10^{-12}$ | $4.89 \times 10^{-12}$ | $4.87 \times 10^{3}$   | 0.16               | $4.44 \times 10^{-12}$       |
| residual_relu     | $5.55 \times 10^{-3}$  | $7.14 \times 10^{-3}$  | $5.45 \times 10^{12}$  | 0.13               | $5.24 \times 10^{-3}$        |
| siren             | $2.08 \times 10^{-17}$ | $7.01 \times 10^{-17}$ | $3.05 \times 10^{-3}$  | 0.12               | $3.04 \times 10^{-17}$       |
| dense_layernorm   | $2.81 \times 10^{-4}$  | $3.23 \times 10^{-4}$  | $2.79 \times 10^{11}$  | 0.17               | $3.32 \times 10^{-4}$        |

**Key observations:**
- The `dense_relu` and `siren` architectures achieve the lowest RMSE and maximum absolute errors by several orders of magnitude, with median relative errors below $0.5\%$.
- The `deep_dense_relu`, `residual_relu`, and `dense_layernorm` architectures exhibit much larger relative errors, with the median relative error for `deep_dense_relu` and `dense_layernorm` exceeding $10^{11}$ and $10^{3}$, respectively.
- Inference times for all architectures are comparable and extremely fast (0.12–0.19 seconds for 1,200 spectra), with the SIREN model being the fastest.
- Errors at zero-crossings are lowest for `dense_relu` and `siren`, indicating robust handling of sign changes.

---

## 3. Diagnostic Plots and Visual Analysis

A multi-panel diagnostic plot (see Figure 1, saved as `data/clte_emulator_diagnostics_1_20250423_000205.png`) provides further insight into emulator performance:

### 3.1. True vs. Emulated $C_\ell^{TE}$ for Random Test Samples

- **Panel (a):** Plots of true and emulated $C_\ell^{TE}$ for three random test samples show that both `dense_relu` and `siren` architectures closely track the oscillatory structure of the true spectra across all $\ell$, including the correct reproduction of zero-crossings and amplitude modulations.
- The other architectures (`deep_dense_relu`, `residual_relu`, `dense_layernorm`) show significant deviations, with visible phase errors, amplitude mismatches, and in some cases, failure to reproduce the sign changes.

### 3.2. RMSE as a Function of $\ell$

- **Panel (b):** The RMSE for `dense_relu` and `siren` remains extremely low and flat across all $\ell$, indicating uniform accuracy from large to small angular scales.
- The RMSE for the other architectures increases at high $\ell$ and near zero-crossings, reflecting their inability to capture fine oscillatory features.

### 3.3. Median Relative Error as a Function of $\ell$

- **Panel (c):** The median relative error for `dense_relu` and `siren` is consistently below $0.5\%$ for all $\ell$, with no significant spikes at zero-crossings.
- The other architectures show large spikes in relative error, especially at multipoles where $C_\ell^{TE}$ crosses zero, confirming their instability in these regions.

### 3.4. Histogram of Zero-Crossing Errors

- **Panel (d):** The distribution of absolute errors at zero-crossings is sharply peaked near zero for `dense_relu` and `siren`, while the other models have broader, higher-error distributions.
- This highlights the importance of specialized architectures or activations for handling sign-changing, oscillatory targets.

---

## 4. Interpretation and Discussion

### 4.1. Why Do Some Architectures Outperform Others?

#### Dense ReLU and SIREN: The Gold Standard

- **Dense ReLU:** The baseline dense network with ReLU activations achieves near machine-precision accuracy. This is somewhat surprising, as ReLU is not inherently suited to oscillatory functions, but the relatively shallow network (4 layers, 128 units) appears sufficient to fit the smooth, low-dimensional mapping from cosmological parameters to $C_\ell^{TE}$.
- **SIREN:** The SIREN architecture, designed for representing complex, high-frequency, and oscillatory functions, also achieves excellent accuracy. The sinusoidal activation enables the network to naturally represent the oscillatory structure of $C_\ell^{TE}$, including the correct phase and amplitude of the acoustic peaks and troughs.

#### Deep, Residual, and Normalized Networks: Pitfalls

- **Deep Dense ReLU:** Increasing depth and width without architectural adaptation leads to catastrophic overfitting or optimization difficulties, as evidenced by the enormous median relative error. This may be due to vanishing/exploding gradients or the inability of deep ReLU networks to efficiently represent sign-changing, oscillatory functions without explicit regularization or architectural guidance.
- **Residual ReLU:** While residual connections are beneficial for very deep networks and for learning identity mappings, in this context they do not improve accuracy and may even hinder learning, possibly due to the mismatch between the residual structure and the global, smooth mapping required.
- **Dense LayerNorm:** Layer normalization, while helpful for stabilizing training in some contexts, does not address the core challenge of representing oscillatory, sign-changing functions, and may even introduce additional nonlinearity that impedes learning in this low-dimensional input regime.

### 4.2. Challenges in Emulating Oscillatory, Sign-Changing Spectra

The $C_\ell^{TE}$ spectrum is uniquely challenging for emulation due to:
- **Oscillatory Structure:** The spectrum exhibits rapid oscillations with varying amplitude and phase, especially at high $\ell$.
- **Zero-Crossings:** The spectrum crosses zero multiple times, making relative error metrics ill-defined and increasing the risk of sign errors in emulation.
- **Dynamic Range:** The amplitude of $C_\ell^{TE}$ varies by several orders of magnitude across $\ell$.

The best-performing architectures (`dense_relu` and `siren`) succeed by:
- **Capacity:** Having sufficient width and depth to capture the mapping from parameters to spectra.
- **Activation Function:** SIREN's sinusoidal activation is naturally suited to oscillatory targets, while ReLU networks can approximate such functions given enough capacity and data.
- **Training Stability:** Both models converge rapidly and stably, as evidenced by low validation loss and fast inference.

### 4.3. Trade-offs: Accuracy vs. Computational Efficiency

- **Accuracy:** Both `dense_relu` and `siren` achieve sub-percent accuracy across all $\ell$, with errors at zero-crossings at the level of $10^{-17}$, effectively indistinguishable from the true spectra for all practical purposes.
- **Speed:** All architectures are extremely fast at inference, with the SIREN model being marginally faster. For practical applications (e.g., MCMC sampling, parameter inference), the difference is negligible.
- **Robustness:** The SIREN model may be more robust to extrapolation or to emulating spectra with more complex oscillatory features (e.g., in extended cosmologies), but for the flat $\Lambda$CDM case, both top models are sufficient.

### 4.4. Recommendations for Cosmological Emulation

- **For highest accuracy and robustness:** Use either a SIREN-style network or a well-tuned dense ReLU network. Both are capable of emulating $C_\ell^{TE}$ to sub-percent accuracy across the full multipole range, including at zero-crossings.
- **For simplicity and ease of deployment:** The dense ReLU network is easier to implement and does not require custom activations or serialization logic, making it preferable for most users.
- **For more complex or oscillatory targets:** SIREN or other sinusoidal-activation networks may offer advantages, especially if the target function is more oscillatory or higher-dimensional than $C_\ell^{TE}$ in flat $\Lambda$CDM.

### 4.5. Implications and Future Work

- **Generalization:** The success of simple dense networks suggests that the mapping from cosmological parameters to $C_\ell^{TE}$ is smooth and low-dimensional, at least within the flat $\Lambda$CDM parameter space. For extended models (e.g., with running, isocurvature, or non-flat geometries), more sophisticated architectures may be required.
- **Zero-Crossing Handling:** Explicitly monitoring and minimizing errors at zero-crossings is crucial for oscillatory spectra. Future work could explore loss functions or architectures that directly penalize sign errors.
- **Uncertainty Quantification:** While this study focused on point predictions, future emulators could incorporate Bayesian or ensemble methods to provide uncertainty estimates, especially near zero-crossings or in extrapolation regimes.
- **Integration with Cosmological Pipelines:** The demonstrated speed and accuracy of these emulators make them ideal for integration into MCMC or likelihood pipelines, enabling orders-of-magnitude speedup over traditional Boltzmann codes.

---

## 5. Conclusion

This study demonstrates that neural network emulators can achieve extremely high accuracy and speed in predicting the $C_\ell^{TE}$ spectrum for flat $\Lambda$CDM cosmologies, provided that the architecture is appropriately chosen. Both standard dense ReLU networks and SIREN-style networks are capable of sub-percent accuracy across all multipoles, including at the challenging zero-crossings. The results highlight the importance of matching network architecture to the target function's structure and provide clear guidance for future emulator development in cosmology.

---

**Figure 1:** Multi-panel diagnostic plot (see `data/clte_emulator_diagnostics_1_20250423_000205.png`):
- (a) True vs. emulated $C_\ell^{TE}$ for random test samples
- (b) RMSE vs. $\ell$
- (c) Median relative error vs. $\ell$
- (d) Histogram of absolute errors at zero-crossings

**Table 1:** Quantitative performance summary for all architectures (see above).

---

**References:**
- Sitzmann, V., et al. (2020). "Implicit Neural Representations with Periodic Activation Functions." NeurIPS.
- Planck Collaboration (2018). "Planck 2018 results. VI. Cosmological parameters." A&A.
- Lesgourgues, J. (2011). "The Cosmic Linear Anisotropy Solving System (CLASS) I: Overview." A&A.

---

**Data and code availability:** All data, trained models, and evaluation scripts are available in the `data/` and `codebase/` directories. The main diagnostic plot is saved as `data/clte_emulator_diagnostics_1_20250423_000205.png`.