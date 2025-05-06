import os
os.environ["CMBAGENT_DEBUG"] = "false"
os.environ["ASTROPILOT_DISABLE_DISPLAY"] = "false"
from astropilot import AstroPilot

params = {}

astro_pilot = AstroPilot(params)
astro_pilot.get_paper()