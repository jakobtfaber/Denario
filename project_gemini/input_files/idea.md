
Project Idea:
	* Catch Me If You Can: Optimizing Follow-up Cadence for Intermittent Pulsars Discovered in Targeted vs. Blind Surveys
		- This project investigates the optimal strategy for achieving phase connection for emission-intermittent pulsars (RRATs, nullers), whose discovery is highly dependent on survey strategy.
		- It will simulate the detection of a population of intermittent pulsars in both the long-dwell (1260 s) targeted search and the short-dwell (60 s) blind search, quantifying the difference in initial parameter estimation (period, S/N).
		- The core of the project is to design and test follow-up cadences tailored to each discovery scenario. For example, a single-burst detection from the blind survey may require a dense block of initial observations to confirm the period, while a multi-rotation detection from the targeted survey might allow for a more sparsely sampled follow-up.
		- The final output will be a recommendation on which survey mode is more efficient overall (discovery + follow-up time) for building a timed sample of intermittent pulsars and will specify the optimal number and spacing of follow-up epochs for each case.

- Idea 2:
	* Taming the Jitter: A Cadence Strategy to Characterize Red Noise and Achieve Phase Connection for Newly Discovered Millisecond Pulsars
		- This project focuses on designing a follow-up cadence specifically to mitigate the dominant noise sources in millisecond pulsars (MSPs): intrinsic red noise (timing noise) and pulse jitter, which can prevent a phase-connected solution even with high S/N.
		- It will involve creating analytic models to predict the growth of timing errors due to red noise as a function of observational spacing and total time baseline.
		- Using simulations, the project will compare different cadence strategies (e.g., uniform spacing, logarithmically spaced, nested/hierarchical) for their ability to characterize the red noise power spectrum efficiently. The simulations will incorporate realistic TOA uncertainties based on the telescope's SEFD.
		- The goal is to determine the cadence that minimizes the total telescope time required to not only achieve phase connection but also to robustly measure the pulsar's spin-down rate (P-dot) in the presence of red noise, a critical factor for MSP science.

- Idea 3:
	* Memory-Driven Pulsar Timing: Co-designing the Real-Time Search and Follow-up Cadence under NVIDIA GPU Constraints
		- This project explores the direct trade-off between the real-time search pipeline's design, constrained by the NVIDIA GPU memory (288 GB HBM4 per package), and the efficiency of the subsequent follow-up timing campaign.
		- It will first develop a precise model of the GPU memory footprint for the search pipeline, linking parameters like `T_dwell`, number of beams, and number of DM/acceleration trials to the memory requirements.
		- The project will then investigate how modifying the search parameters to maximize dwell time within the memory budget (e.g., reducing DM trials in the blind survey to increase `T_dwell` from 60 s to 120 s) alters the demographics of the discovered pulsar population.
		- For each search configuration (fiducial vs. memory-optimized), a corresponding optimal follow-up cadence will be designed and simulated. The final analysis will determine if co-designing the search and follow-up strategy yields a higher number of phase-connected pulsars per total hour of telescope time.

- Idea 4:
	* Timing Through the Haze: A Comparative Cadence Strategy for Phase-Connecting Pulsars in the Galactic Center versus the Disk
		- This project will design and compare optimal timing strategies for two scientifically critical but environmentally distinct populations: pulsars in the Galactic Center (GC) and those in the Galactic disk.
		- It will use population synthesis models to generate realistic pulsar samples for both locales, critically incorporating extreme ISM effects for the GC population, such as severe temporal scattering and high, variable dispersion measures (DMs).
		- The project will simulate the discovery of these pulsars and then design tailored follow-up cadences. The GC strategy will likely require more frequent, multi-frequency observations (utilizing the telescope's 0.7-2 GHz range) to measure and correct for DM variations, which is the primary obstacle to phase connection.
		- The key outcome will be a quantitative comparison of the timing yield, defined as the number of phase-connected solutions achieved per unit of telescope time, for the GC versus the disk. This will establish the 'observational cost' of timing a GC pulsar and provide a validated cadence prescription.

- Idea 5:
	* A Self-Correcting Cadence: An Adaptive, Bayesian Framework for Efficiently Timing a Diverse Pulsar Population
		- This project aims to develop a flexible, adaptive cadence strategy that dynamically adjusts its observation schedule based on incoming data, moving beyond fixed, pre-determined schedules for each pulsar class.
		- An adaptive algorithm will be built, likely using a Bayesian inference framework. After the first few follow-up observations, the system will update its estimates of the pulsar's parameters (P, P-dot) and their uncertainties, and classify the source probabilistically (e.g., 70% chance of being a young pulsar, 30% a high-B pulsar).
		- The algorithm will use pre-defined triggers to modify the cadence. For example, detecting significant timing residuals could trigger a series of closely-spaced observations to search for a glitch, while a non-detection could trigger a different sequence to test for intermittency.
		- The performance of this adaptive system will be simulated on a diverse, mixed population of newly discovered pulsars and compared directly to the efficiency of the best possible fixed-cadence strategies, aiming to prove a significant reduction in total telescope time to achieve phase connection across the population.

        