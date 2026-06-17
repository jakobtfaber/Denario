#!/usr/bin/env bash
set -euo pipefail

# Simple verifier for Denario idea pipeline wiring, run inside docker compose service.
# Usage:
#   bash ./verify_idea_pipeline.sh            # defaults to service 'denario-plus'
#   bash ./verify_idea_pipeline.sh denario    # use base service instead

SERVICE="${1:-denario-plus}"
COMPOSE="docker compose -f compose.yml -f compose.plus.override.yml"

echo "[1/3] Checking Denario.get_idea signature in service: ${SERVICE}"
${COMPOSE} exec "${SERVICE}" sh -lc "python - <<'PY'
import inspect
import denario.denario as D
print('Signature:', inspect.signature(D.Denario.get_idea))
PY"

printf "\n[2/3] Showing module path and get_idea source head\n"
${COMPOSE} exec "${SERVICE}" sh -lc "python - <<'PY'
import denario, inspect
import denario.denario as D
print('denario module:', denario.__file__)
src = inspect.getsource(D.Denario.get_idea)
print('get_idea head:\n' + src[:300])
PY"

printf "\n[3/3] Running safe stubbed pipeline (no network / no cost)\n"
${COMPOSE} exec "${SERVICE}" sh -lc "python - <<'PY'
from denario.denario import Denario
from denario.idea import cmbagent

orig = cmbagent.planning_and_control

def stub(desc, **kwargs):
    keys = ('planner_model','plan_reviewer_model')
    print('STUB OK:', {k: kwargs.get(k) for k in keys})
    return {'chat_history':[{'name':'idea_maker_nest','content':'Project Idea: stubbed'}]}

cmbagent.planning_and_control = stub

import tempfile
with tempfile.TemporaryDirectory() as tmpdir:
    d = Denario(project_dir=tmpdir, clear_project_dir=True)
d.set_data_description('Test data description')
d.get_idea(
    idea_maker_model='gpt-5-mini',
    idea_hater_model='gpt-5-mini',
    planner_model='gpt-5-mini',
    plan_reviewer_model='gpt-5-mini',
)
print('PIPELINE OK')

# restore
cmbagent.planning_and_control = orig
PY"

printf "\nAll checks completed.\n"

