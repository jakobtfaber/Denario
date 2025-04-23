
Find best neural net architecture for cl TE emulators in flat LCDM (we want accurate cl's at all l's)
Input parameters include the cosmological parameters. 
We want to determine the architecture that is both as accurate as possible and as fast as possible to compute.
The challenge is that cl TE is oscillating around 0. 

Constraints:
- use classy_sz for computing cl TE to generate the data.
- Cosmological parameters are omega_b, omega_cdm, H0, logA, n_s and tau_reio
- Training set should have at least 5k spectra.
- The training/testing data should be created in a different step as training the neural nets.
- The step to train the neural nets should only be for training. Plotting and performances should be done in another step.
