Here are two datasets made of 2 files each. 

These datasets contain subhalo and group-level properties from two different CAMELS simulations (A and B). The goal is to compare the distributions of these properties across both datasets.

Dataset A contains a file for groups and another file for subhalos.
Dataset B contains a file for groups and another file for subhalos.

The files are loaded as follows:

```python
groups_A_df = pd.read_pickle('{path_to_project_data}data/CAMELS/LOCAL/groups_200_mcut5e9.pkl')

subhalos_A_df = pd.read_pickle('{path_to_project_data}data/CAMELS/LOCAL/subhalos_200_mcut5e9.pkl')

groups_B_df = pd.read_pickle('{path_to_project_data}data/CAMELS/LOCAL/groups_n200_mcut5e9.pkl')

subhalos_B_df = pd.read_pickle('{path_to_project_data}data/CAMELS/LOCAL/subhalos_n200_mcut5e9.pkl')
```

<Info on groups from DATASET A>
output of groups_A_df.describe().to_markdown():
\n
|       |      GroupSFR |   Group_R_Mean200 |   Group_M_Mean200 |\n|:------|--------------:|------------------:|------------------:|\n| count | 43919         |        43919      |      43919        |\n| mean  |     0.0394391 |           69.119  |         10.795    |\n| std   |     0.349229  |           47.0143 |        181.113    |\n| min   |     0         |           41.544  |          0.500035 |\n| 25%   |     0         |           46.8392 |          0.716605 |\n| 50%   |     0         |           55.6308 |          1.20068  |\n| 75%   |     0         |           73.1278 |          2.72706  |\n| max   |    22.1854    |         1429.6    |      20376.9      |
\n
This gives you the mean, std, min and max of all features. 

output of groups_A_df.info():
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 43919 entries, 0 to 43918
Data columns (total 3 columns):
 id   Column           Non-Null Count  Dtype  
---  ------           --------------  -----  
 0   GroupSFR         43919 non-null  float32
 1   Group_R_Mean200  43919 non-null  float32
 2   Group_M_Mean200  43919 non-null  float32
dtypes: float32(3)
memory usage: 514.8 KB
</Info on groups from DATASET A>

<Info on subhalos from DATASET A>
output of subhalos_A_df.describe().to_markdown():
\n
|       |   SubhaloGasMetallicity |   SubhaloMass |     SubhaloSFR |   SubhaloSpinMod |   SubhaloVmax |   SubhaloStellarPhotometrics_U |   SubhaloStellarPhotometrics_B |   SubhaloStellarPhotometrics_V |   SubhaloStellarPhotometrics_K |   SubhaloStellarPhotometrics_g |   SubhaloStellarPhotometrics_r |   SubhaloStellarPhotometrics_i |   SubhaloStellarPhotometrics_z |   SubhaloStarMetallicity |   SubhaloMassGAS |   SubhaloMassDM |   SubhaloMassSWP |   SubhaloMassBH |   SubhaloVelDisp |   SubhaloVmaxRad |\n|:------|------------------------:|--------------:|---------------:|-----------------:|--------------:|-------------------------------:|-------------------------------:|-------------------------------:|-------------------------------:|-------------------------------:|-------------------------------:|-------------------------------:|-------------------------------:|-------------------------:|-----------------:|----------------:|-----------------:|----------------:|-----------------:|-----------------:|\n| count |          19899          |  19899        | 19899          |     19899        |    19899      |                    19899       |                    19899       |                    19899       |                    19899       |                    19899       |                    19899       |                    19899       |                    19899       |          19899           |     19899        |     19899       |  19899           |  19899          |      19899       |     19899        |\n| mean  |              0.00241472 |     19.7995   |     0.086748   |       316.391    |       78.98   |                      -14.1532  |                      -14.2102  |                      -14.7898  |                      -16.8825  |                      -14.5539  |                      -15.0335  |                      -15.2574  |                      -15.382   |              0.00309677  |         1.68379  |        17.8896  |      0.223904    |      0.00217078 |         41.0045  |         9.79347  |\n| std   |              0.0047742  |    214.924    |     0.386424   |       985.495    |       44.8809 |                        2.5752  |                        2.58351 |                        2.57515 |                        2.76963 |                        2.5826  |                        2.57364 |                        2.57989 |                        2.60479 |              0.0054059   |        28.5536   |       185.34    |      1.67371     |      0.0166196  |         25.5705  |        14.8538   |\n| min   |              0          |      0.015274 |     0          |         0.632567 |       14.6426 |                      -23.1181  |                      -23.5218  |                      -24.388   |                      -27.3086  |                      -23.9762  |                      -24.7304  |                      -25.091   |                      -25.3442  |              0           |         0        |         0       |      0.000127053 |      0          |          5.66792 |         0.155282 |\n| 25%   |              0          |      1.23473  |     0          |        46.1689   |       54.6936 |                      -15.7095  |                      -15.8217  |                      -16.3773  |                      -18.5555  |                      -16.1497  |                      -16.6045  |                      -16.8166  |                      -16.9546  |              0           |         0        |         1.18732 |      0.00135345  |      0          |         27.247   |         4.88905  |\n| 50%   |              0          |      3.08521  |     0          |       121.217    |       66.2988 |                      -13.2746  |                      -13.3483  |                      -13.9588  |                      -15.9583  |                      -13.7009  |                      -14.2068  |                      -14.4306  |                      -14.5358  |              0.000476962 |         0.137651 |         2.92612 |      0.00361856  |      0          |         34.1553  |         7.20554  |\n| 75%   |              0.00230178 |      7.49199  |     0.00806652 |       287.393    |       86.6325 |                      -12.1195  |                      -12.1418  |                      -12.7148  |                      -14.6574  |                      -12.4812  |                      -12.9546  |                      -13.1792  |                      -13.287   |              0.00326121  |         0.448655 |         6.9552  |      0.022985    |      0.00197687 |         45.8289  |        10.7982   |\n| max   |              0.0500647  |  16390.3      |    11.7264     |     52957.2      |      891.599  |                       -9.20578 |                       -9.2193  |                       -9.79216 |                      -11.7395  |                       -9.55614 |                      -10.0368  |                      -10.2619  |                      -10.3751  |              0.0591522   |      2306.39     |     13965.4     |    117.125       |      1.39779    |        502.215   |       574.99     |
\n
This gives you the mean, std, min and max of all features. 

output of subhalos_A_df.info():
```
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 19899 entries, 0 to 19898
Data columns (total 20 columns):
 id   Column                        Non-Null Count  Dtype  
---  ------                        --------------  -----  
 0   SubhaloGasMetallicity         19899 non-null  float32
 1   SubhaloMass                   19899 non-null  float32
 2   SubhaloSFR                    19899 non-null  float32
 3   SubhaloSpinMod                19899 non-null  float32
 4   SubhaloVmax                   19899 non-null  float32
 5   SubhaloStellarPhotometrics_U  19899 non-null  float32
 6   SubhaloStellarPhotometrics_B  19899 non-null  float32
 7   SubhaloStellarPhotometrics_V  19899 non-null  float32
 8   SubhaloStellarPhotometrics_K  19899 non-null  float32
 9   SubhaloStellarPhotometrics_g  19899 non-null  float32
 10  SubhaloStellarPhotometrics_r  19899 non-null  float32
 11  SubhaloStellarPhotometrics_i  19899 non-null  float32
 12  SubhaloStellarPhotometrics_z  19899 non-null  float32
 13  SubhaloStarMetallicity        19899 non-null  float32
 14  SubhaloMassGAS                19899 non-null  float32
 15  SubhaloMassDM                 19899 non-null  float32
 16  SubhaloMassSWP                19899 non-null  float32
 17  SubhaloMassBH                 19899 non-null  float32
 18  SubhaloVelDisp                19899 non-null  float32
 19  SubhaloVmaxRad                19899 non-null  float32
dtypes: float32(20)
memory usage: 1.5 MB
```
</Info on subhalos from DATASET A>


<Info on groups of DATASET B>
output of groups_B_df.describe().to_markdown():
\n
|       |      GroupSFR |   Group_R_Mean200 |   Group_M_Mean200 |\n|:------|--------------:|------------------:|------------------:|\n| count | 44288         |        44288      |      44288        |\n| mean  |     0.0422433 |           69.2228 |         10.7355   |\n| std   |     0.429011  |           47.0008 |        177.43     |\n| min   |     0         |           41.5453 |          0.500062 |\n| 25%   |     0         |           46.8837 |          0.718632 |\n| 50%   |     0         |           55.7362 |          1.2075   |\n| 75%   |     0         |           73.2698 |          2.74314  |\n| max   |    37.2313    |         1428.54   |      20331.6      |
\n
This gives you the mean, std, min and max of all features. 

output of groups_B_df.info():
```
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 44288 entries, 0 to 44287
Data columns (total 3 columns):
 id   Column           Non-Null Count  Dtype  
---  ------           --------------  -----  
 0   GroupSFR         44288 non-null  float32
 1   Group_R_Mean200  44288 non-null  float32
 2   Group_M_Mean200  44288 non-null  float32
dtypes: float32(3)
memory usage: 519.1 KB
```
</Info on groups of DATASET B>


<Info on subhalos of DATASET B>
output of subhalos_B_df.describe().to_markdown():
\n
|       |   SubhaloGasMetallicity |   SubhaloMass |     SubhaloSFR |   SubhaloSpinMod |   SubhaloVmax |   SubhaloStellarPhotometrics_U |   SubhaloStellarPhotometrics_B |   SubhaloStellarPhotometrics_V |   SubhaloStellarPhotometrics_K |   SubhaloStellarPhotometrics_g |   SubhaloStellarPhotometrics_r |   SubhaloStellarPhotometrics_i |   SubhaloStellarPhotometrics_z |   SubhaloStarMetallicity |   SubhaloMassGAS |   SubhaloMassDM |   SubhaloMassSWP |   SubhaloMassBH |   SubhaloVelDisp |   SubhaloVmaxRad |\n|:------|------------------------:|--------------:|---------------:|-----------------:|--------------:|-------------------------------:|-------------------------------:|-------------------------------:|-------------------------------:|-------------------------------:|-------------------------------:|-------------------------------:|-------------------------------:|-------------------------:|-----------------:|----------------:|-----------------:|----------------:|-----------------:|-----------------:|\n| count |          20382          | 20382         | 20382          |      20382       |    20382      |                    20382       |                    20382       |                    20382       |                    20382       |                    20382       |                    20382       |                    20382       |                    20382       |          20382           |     20382        |     20382       |  20382           |  20382          |      20382       |     20382        |\n| mean  |              0.00238127 |    19.4284    |     0.0914536  |        317.282   |       77.9824 |                      -14.1589  |                      -14.2142  |                      -14.791   |                      -16.8777  |                      -14.5569  |                      -15.0336  |                      -15.2562  |                      -15.3799  |              0.00303963  |         1.66305  |        17.5501  |      0.213218    |      0.00210229 |         40.5932  |        10.0095   |\n| std   |              0.00467078 |   210.281     |     0.513093   |       1001.07    |       43.9643 |                        2.56884 |                        2.57773 |                        2.56797 |                        2.75787 |                        2.57637 |                        2.56583 |                        2.57107 |                        2.59519 |              0.00530365  |        27.8491   |       181.508   |      1.52575     |      0.0159994  |         25.2384  |        15.2057   |\n| min   |              0          |     0.0159726 |     0          |          1.17564 |       10.2123 |                      -23.1801  |                      -23.5313  |                      -24.3584  |                      -27.1762  |                      -23.9709  |                      -24.6873  |                      -25.0282  |                      -25.2637  |              0           |         0        |         0       |      0.000163077 |      0          |          4.59465 |         0.307768 |\n| 25%   |              0          |     1.22453   |     0          |         46.2172  |       54.1398 |                      -15.7662  |                      -15.8733  |                      -16.4076  |                      -18.5786  |                      -16.2088  |                      -16.6382  |                      -16.8536  |                      -16.9868  |              0           |         0        |         1.16785 |      0.00134983  |      0          |         26.9895  |         5.01202  |\n| 50%   |              0          |     3.07819   |     0          |        121.712   |       65.6042 |                      -13.2776  |                      -13.3486  |                      -13.9556  |                      -15.9564  |                      -13.702   |                      -14.208   |                      -14.4271  |                      -14.5336  |              0.000480832 |         0.138162 |         2.9099  |      0.00356472  |      0          |         33.8581  |         7.39513  |\n| 75%   |              0.00229632 |     7.48532   |     0.00824189 |        290.865   |       85.6452 |                      -12.128   |                      -12.1513  |                      -12.7236  |                      -14.6586  |                      -12.4893  |                      -12.9648  |                      -13.1885  |                      -13.2945  |              0.00314217  |         0.45165  |         6.96169 |      0.0227119   |      0.00195949 |         45.4213  |        11.2365   |\n| max   |              0.0432014  | 16541.6       |    36.6898     |      57571       |      868.704  |                       -9.49047 |                       -9.63056 |                      -10.3286  |                      -12.3199  |                      -10.0174  |                      -10.6145  |                      -10.8462  |                      -10.9588  |              0.0397323   |      2358.29     |     14083.7     |     98.1971      |      1.46984    |        482.48    |       605.262    |
\n
This gives you the mean, std, min and max of all features. 

output of subhalos_B_df.info():
```
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 20382 entries, 0 to 20381
Data columns (total 20 columns):
 id   Column                        Non-Null Count  Dtype  
---  ------                        --------------  -----  
 0   SubhaloGasMetallicity         20382 non-null  float32
 1   SubhaloMass                   20382 non-null  float32
 2   SubhaloSFR                    20382 non-null  float32
 3   SubhaloSpinMod                20382 non-null  float32
 4   SubhaloVmax                   20382 non-null  float32
 5   SubhaloStellarPhotometrics_U  20382 non-null  float32
 6   SubhaloStellarPhotometrics_B  20382 non-null  float32
 7   SubhaloStellarPhotometrics_V  20382 non-null  float32
 8   SubhaloStellarPhotometrics_K  20382 non-null  float32
 9   SubhaloStellarPhotometrics_g  20382 non-null  float32
 10  SubhaloStellarPhotometrics_r  20382 non-null  float32
 11  SubhaloStellarPhotometrics_i  20382 non-null  float32
 12  SubhaloStellarPhotometrics_z  20382 non-null  float32
 13  SubhaloStarMetallicity        20382 non-null  float32
 14  SubhaloMassGAS                20382 non-null  float32
 15  SubhaloMassDM                 20382 non-null  float32
 16  SubhaloMassSWP                20382 non-null  float32
 17  SubhaloMassBH                 20382 non-null  float32
 18  SubhaloVelDisp                20382 non-null  float32
 19  SubhaloVmaxRad                20382 non-null  float32
dtypes: float32(20)
memory usage: 1.6 MB
```
</Info on subhalos of DATASET B>

Datasets A and B are catalogs of objects (groups and subhalos) that inherently depend the local primordial non-Gaussianity parameter values fNL=200 for A and fNL=-200 for B.

Description of the group features: 
 0   GroupSFR                      Sum of the individual star formation rates of all gas cells in this group. In units of Msun/yr.
 1   Group_R_Mean200               Comoving Radius of a sphere centered at the GroupPos of this Group whose mean density is 200 times the mean density of the Universe, at the time the halo is considered. In units of ckpc/h.
 2   Group_M_Mean200               Total Mass of this group enclosed in a sphere whose mean density is 200 times the mean density of the Universe, at the time the halo is considered, in units of 1e10 Msun/h.

Description of the subhalo features:
 0   SubhaloGasMetallicity         Mass-weighted average metallicity (Mz/Mtot, where Z = any element above He) of the gas cells bound to this Subhalo, but restricted to cells within twice the stellar half mass radius. 
 1   SubhaloMass                   Total mass of all member particle/cells which are bound to this Subhalo, of all types. Particle/cells bound to subhaloes of this Subhalo are NOT accounted for. In units of 1e10 Msun/h.
 2   SubhaloSFR                    Sum of the individual star formation rates of all gas cells in this subhalo. In units of Msun/yr.
 3   SubhaloSpinMod                Total 3D spin modulus, computed for each as the mass weighted sum of the relative coordinate times relative velocity of all member particles/cells. In units of (kpc/h)(km/s).
 4   SubhaloVmax                   Maximum value of the spherically-averaged rotation curve. All available particle types (e.g. gas, stars, DM, and SMBHs) are included in this calculation. In units of km/s.
 5   SubhaloStellarPhotometrics_U  Magnitude in U-band based on the summed-up luminosities of all the stellar particles of the group. In mag units.
 6   SubhaloStellarPhotometrics_B  Magnitude in B-band based on the summed-up luminosities of all the stellar particles of the group. In mag units. 
 7   SubhaloStellarPhotometrics_V  Magnitude in V-band based on the summed-up luminosities of all the stellar particles of the group. In mag units. 
 8   SubhaloStellarPhotometrics_K  Magnitude in K-band based on the summed-up luminosities of all the stellar particles of the group. In mag units. 
 9   SubhaloStellarPhotometrics_g  Magnitude in g-band based on the summed-up luminosities of all the stellar particles of the group. In mag units. 
 10  SubhaloStellarPhotometrics_r  Magnitude in r-band based on the summed-up luminosities of all the stellar particles of the group. In mag units.
 11  SubhaloStellarPhotometrics_i  Magnitude in i-band based on the summed-up luminosities of all the stellar particles of the group. In mag units.
 12  SubhaloStellarPhotometrics_z  Magnitude in z-band based on the summed-up luminosities of all the stellar particles of the group. In mag units.
 13  SubhaloStarMetallicity        Mass-weighted average metallicity (Mz/Mtot, where Z = any element above He) of the star particles bound to this Subhalo, but restricted to stars within twice the stellar half mass radius.
 14  SubhaloMassGAS                Gas mass of all member particle/cells which are bound to this Subhalo, separated by type. Particle/cells bound to subhaloes of this Subhalo are NOT accounted for. In units of 1e10 Msun/h.
 15  SubhaloMassDM                 Dark Matter mass of all member particle/cells which are bound to this Subhalo, separated by type. Particle/cells bound to subhaloes of this Subhalo are NOT accounted for. In units of 1e10 Msun/h.
 16  SubhaloMassSWP                Mass of Stars & Wind particles which are bound to this Subhalo, separated by type. Particle/cells bound to subhaloes of this Subhalo are NOT accounted for. In units of 1e10 Msun/h.
 17  SubhaloMassBH                 Black Hole mass of all member particle/cells which are bound to this Subhalo, separated by type. Particle/cells bound to subhaloes of this Subhalo are NOT accounted for. In units of 1e10 Msun/h.
 18  SubhaloVelDisp                One-dimensional velocity dispersion of all the member particles/cells (the 3D dispersion divided by sqrt(3))
 19  SubhaloVmaxRad                Maximum value of the spherically-averaged rotation curve. All available particle types (e.g. gas, stars, DM, and SMBHs) are included in this calculation.


Groups and subhalos should be considered as separate objects (they dont have the same features).

There is no information on object positions, thus it is not possible to compute spatial correlation functions.