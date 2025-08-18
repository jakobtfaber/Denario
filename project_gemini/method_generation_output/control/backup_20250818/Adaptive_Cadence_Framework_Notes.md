<!-- filename: Adaptive_Cadence_Framework_Notes.md -->
# Scientific Reasoning, Hypotheses, and Assumptions Underlying the Adaptive Cadence Framework

## Scientific Motivation

Achieving phase-connected timing solutions for newly discovered radio pulsars is essential for precise measurement of their rotational and orbital parameters, enabling studies of neutron star physics, binary evolution, and tests of fundamental physics. The diversity of pulsar sub-populations—ranging from young, noisy, glitch-prone objects to stable millisecond pulsars (MSPs) and emission-intermittent sources—necessitates tailored observational strategies. A unified, adaptive cadence framework is required to maximize the fraction of sources for which phase connection is achieved, while optimizing the use of limited telescope time and computational resources.

## Hypotheses

- **Cadence optimization, when dynamically adapted to the evolving timing solution and noise properties of each pulsar, will maximize the phase-connection success rate per unit telescope time compared to fixed-cadence approaches.**
- **Sub-population-specific cadence strategies, informed by analytic models and validated by simulations, will yield higher timing completeness and lower parameter uncertainties, especially for challenging populations (e.g., intermittent, high-B, or highly scattered sources).**
- **Integration of real-time discovery S/N and initial spin parameters, as provided by the NVIDIA Vera Rubin NVL144 backend, enables rapid transition from detection to efficient timing, minimizing the risk of phase ambiguities.**

## Key Assumptions

### Pulsar Populations

- Population fractions and parameter distributions (period, period derivative, DM, scattering) are drawn from population synthesis models (e.g., psrpoppy), with sub-populations defined as: young canonical pulsars, recycled MSPs (field and cluster), magnetars, high-B/transition objects, emission-intermittent classes, and Galactic-center pulsars.
- Each sub-population exhibits characteristic noise and variability properties (e.g., glitch rates for young pulsars, red noise for MSPs, nulling for RRATs).

### Noise Sources

- All relevant noise contributors are explicitly modeled: radiometer noise (set by SEFD, bandwidth, dwell time), template mismatch, pulse jitter, ISM effects (DM variations, scattering), red timing noise, glitches, instrumental and array-level noise, clock errors, Solar-system ephemeris uncertainties, and gravitational wave background (GWB).
- Noise parameter values are referenced to the telescope and search parameter tables (e.g., SEFD = 1.41–2.25 Jy, Tsys/η = 25–40 K, time resolution = 0.1 ms).

### Telescope and Instrumental Constraints

- Observations are performed with a 1650-element, 6.15-m dish array, with a 7 deg² field of view at 1.35 GHz, and a maximum dwell time per pointing of 1260 s (targeted) or 60 s (blind), as set by backend memory (288 GB HBM4 per NVL144 rack) and real-time search requirements.
- Backend compute and memory constraints (NVIDIA Vera Rubin NVL144: 50 PFLOPs, 288 GB HBM4 per package) limit the number of beams, channels, and DM/acceleration trials per search.
- No search-mode data are stored; all follow-up scheduling must be based on real-time detection outputs.

## Links Between Population Characteristics and Timing Efficiency

- **Young pulsars**: High glitch rates and red noise require denser initial cadence and rapid response to phase ambiguities.
- **MSPs**: Low intrinsic noise but sensitive to ISM and clock errors; benefit from high S/N and regular cadence.
- **Magnetars and high-B objects**: Irregular emission and timing noise necessitate flexible, adaptive scheduling.
- **Intermittent sources**: Require opportunistic, high-cadence follow-up to capture emission windows and maintain phase connection.
- **Galactic-center pulsars**: High DM and scattering demand tailored cadence to mitigate ISM-induced phase loss.

## Main Methodological Questions

1. **How should the number and spacing of follow-up epochs be analytically determined for each sub-population, given their noise and variability properties?**
2. **How can the cadence be dynamically adapted as the timing solution evolves, and what triggers should be used for cadence adjustment?**
3. **How are timing success rates and parameter uncertainties quantified, both analytically and via simulation, for each sub-population?**
4. **How can analytic predictions be validated and refined using detailed simulations, ensuring consistency with telescope and backend constraints?**
5. **How can the overall framework be optimized to maximize phase-connected timing completeness and telescope efficiency across the full pulsar census?**