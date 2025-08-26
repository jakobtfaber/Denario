OxWalk Annotated Step Count Dataset

DATA DESCRIPTION:
Annotated step data during unscripted, free living in 39 healthy adult volunteers (aged 18 and above) with no lower limb injury within the previous 6 months and who were able to walk without an assistive device. 
Participants wore four triaxial accelerometers concurrently (AX3, Axivity, Newcastle, UK), two placed side-by-side on the dominant wrist and two clipped to the dominant-side hip at the midsagittal plane. Accelerometers were synchronised using the Open Movement GUI software (v.1.0.0.42), with one recording at 100 Hz and the other at 25 Hz at each body location. Foot-facing video was captured using an action camera (Action Camera CT9500, Crosstour, Shenzhen, China) mounted at the participant’s beltline. 

DATA ANNOTATION:
Foot-facing video was captured for up to one hour using an action camera (Action Camera CT9500, Crosstour, Shenzhen, China) mounted at the participant’s beltline. Annotation of steps was conducted within video annotation software (Elan 6.0, The Language Archive, Nijmegen, Netherlands), where a step was defined as the act of purposeful lifting a foot and placing it in a new location. Steps were not required to be part of a repeating pattern and did not include foot shuffling, changing of foot alignment via pivoting, or shifting of weight from one foot to the other. 

DATASETS:
The data is located in /mnt/ceph/users/fvillaescusa/AstroPilot/Aidan/data. In that folder there are 4 folders (Hip_25Hz, Hip_100Hz, Wrist_25Hz, Wrist_100Hz) and one file (metadata.csv).

Datasets are as follows:
1) "Wrist_100Hz": One Axivity AX3 accelerometer, recording at 100 Hz and +/- 8g on the dominant wrist within a silicone wristband, with axes aligned as prescribed by the manufacturer. <https://axivity.com/userguides/ax3/technical/#axis-alignment>
2) "Wrist_25Hz": One Axivity AX3 accelerometer, recording at 25 Hz and +/- 8g on the dominant wrist within a silicone wristband, with axes aligned as prescribed by the manufacturer. <https://axivity.com/userguides/ax3/technical/#axis-alignment>
3) "Hip_100Hz": One Axivity AX3 accelerometer, recording at 100 Hz and +/- 8g cliped at the beltline, laterally above the dominant leg, with the +X axis approximately aligned in the superior direction, and the positive Y axis aligned to face anteriorly.
4) "Hip_25Hz": One Axivity AX3 accelerometer, recording at 100 Hz and +/- 8g cliped at the beltline, laterally above the dominant leg, with the +X axis approximately aligned in the superior direction, and the positive Y axis aligned to face anteriorly.
5) Participant sex and age range are provided in metadata.csv

Inside each of these folders, there are 39 files, one for each participant. The files are called as PX_hip25.csv, for participant X (01, 02, 03, ...39) and hip25 is for the files inside Hip_25Hz.

The accelerometer data in each file has been resampled and calibrated using the Open Movement GUI software package. Within each CSV file, a step is annotated by a single "1" at the approximate time of heel strike. 


The primary purpose of this data collection is the development of step-counting algorithms, which, given just the raw accelerometer data, should be able to correctly estimate the number of steps. This is particularly useful to compare a variety of algorithms and machine learning models, currently used for this purpose. With the concurrent collection of data from 2 different locations, we could also observe how the performance of these step-counting algorithms compares between the wrist and the hip. Using the metadata file, we can further explore if there are noted differences in different age groups or sexes. 

Of particular interest to me is observing how step-counting algorithms are affected by the reduction in raw sampling frequency. While sampling at a lower frequency may cause the monitor to miss some high-frequency behaviour, the vast majority of human movement occurs at far lower frequencies than the monitor can observe, sampling at 100Hz. Sampling data at a lower frequency can allow for longer periods of monitoring and requires less computing power, which is ideal, as long as it does not cause a significant drop in model performance. 
