import os
os.environ["CMBAGENT_DEBUG"] = "false"
os.environ["ASTROPILOT_DISABLE_DISPLAY"] = "false"
from denario import Denario

params = {}

den = Denario(params)
den.get_paper()