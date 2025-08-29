#!/usr/bin/env python3
import sys
# Prefer vendored cmbagent
sys.path.insert(0, '/workspaces/Denario/third_party/cmbagent')

from cmbagent.cmbagent import CMBAgent
from cmbagent.utils import get_api_keys_from_env

api_keys = get_api_keys_from_env()

print('Using API keys (masked):', {k: (v is not None) for k, v in api_keys.items()})

try:
    cmb = CMBAgent(
        agent_list=['engineer'],
        agent_llm_configs={'engineer': {'model': 'gpt-5-test-model'}},
        api_keys=api_keys,
        clear_work_dir=False,
        skip_rag_agents=True,
        verbose=False,
    )
    print('CMBAgent instantiated successfully')
    # Print the agent llm_config for engineer
    for a in cmb.agents:
        print('Agent:', a.name)
        try:
            print('  model:', a.llm_config['config_list'][0].get('model'))
        except Exception:
            print('  (no accessible llm_config)')
    sys.exit(0)
except Exception as e:
    import traceback
    traceback.print_exc()
    print('\nInstantiation failed:', e)
    sys.exit(2)
