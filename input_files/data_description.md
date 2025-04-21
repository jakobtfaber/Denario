
The data is located under:
root=/Users/boris/CMBAgents/AstroPilot/project_data/data/

Galaxy and Catalog DataFrames: Structure and Usage Guide

1. Full Galaxy DataFrame ('galaxies_full_optimal.parquet')

   - Each row: one galaxy at z=0 from one of 1000 simulated catalogs.

   - Columns: 17 galaxy features, catalog_number, and 6 cosmological/astrophysical parameters.

   - Shape: (720548, 24)

   - File format: Parquet (gzip compressed)


2. Catalog-level DataFrame ('catalog_params_optimal.parquet')

   - Each row: one catalog (simulation run).

   - Columns: catalog_number and 6 cosmological/astrophysical parameters.

   - Shape: (1000, 7)

   - File format: Parquet (gzip compressed)



Data Dictionary

----------------------------------------------------------------------
Column             Physical Meaning                         Units               
----------------------------------------------------------------------
M_g                Gas mass (including circumgalactic medium) Msun                
M_star             Stellar mass                             Msun                
M_BH               Black hole mass                          Msun                
M_t                Total mass (DM + gas + stars + BH)       Msun                
V_max              Maximum circular velocity                km/s                
sigma_v            Velocity dispersion (all particles)      km/s                
Z_g                Mass-weighted gas metallicity            Zsun                
Z_star             Mass-weighted stellar metallicity        Zsun                
SFR                Star formation rate                      Msun/yr             
J_spin             Subhalo spin modulus                     kpc km/s            
V_pecu             Subhalo peculiar velocity modulus        km/s                
R_star             Half-mass radius (stars)                 kpc                 
R_t                Half-mass radius (total)                 kpc                 
R_max              Radius at V_max                          kpc                 
U                  U-band magnitude                         mag                 
K                  K-band magnitude                         mag                 
g                  g-band magnitude                         mag                 
catalog_number     Catalog index (simulation run)           integer             
Omega_m            Matter density parameter                 dimensionless       
sigma_8            Power spectrum normalization             dimensionless       
A_SN1              SN wind energy per SFR                   dimensionless       
A_SN2              SN wind speed                            dimensionless       
A_AGN1             AGN feedback energy per accretion        dimensionless       
A_AGN2             AGN kinetic mode ejection speed          dimensionless       
----------------------------------------------------------------------

There a no missing values.

Example Usage: Loading and Analyzing the DataFrames
Load the full galaxy DataFrame:
df_galaxies = pd.read_parquet(root+'/galaxies_full_optimal.parquet')

Load the catalog-level DataFrame:
df_catalogs = pd.read_parquet(root+'/catalog_params_optimal.parquet')



constraints for proposed research projects:
- we are running calculations on a laptop with 8 available CPUs
- each calculation in this workflow should not take longer than O(10 minutes)
