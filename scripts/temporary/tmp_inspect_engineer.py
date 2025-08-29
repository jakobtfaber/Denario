#!/usr/bin/env python3
import sys, json
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

    eng = None
    for a in cmb.agents:
        if a.name == 'engineer':
            eng = a
            break

    if eng is None:
        print('Engineer agent not found among instantiated agents: ', [a.name for a in cmb.agents])
        sys.exit(2)

    print('\n--- engineer.llm_config (first config dict) ---')
    try:
        first = eng.llm_config['config_list'][0]
        print(json.dumps(first, indent=2))
    except Exception as e:
        print('Could not access eng.llm_config:', e)

    print('\n--- engineer._gpt5_reasoning attribute (if present) ---')
    g = getattr(eng, '_gpt5_reasoning', None)
    print(json.dumps(g, indent=2) if g is not None else 'None')

    # Also show whether gpt5 keys exist anywhere inside the llm_config
    def find_keys(obj, keys):
        found = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in keys:
                    found.append((k, v))
                found.extend(find_keys(v, keys))
        elif isinstance(obj, list):
            for item in obj:
                found.extend(find_keys(item, keys))
        return found

    search_keys = ['gpt5_reasoning', 'gpt5', 'reasoning_effort', 'verbosity', 'max_output_tokens']
    found = find_keys(eng.llm_config, search_keys)
    print('\n--- Any GPT-5 keys found inside engineer.llm_config? ---')
    print([k for k, _ in found])

    print('\nInspection complete')
    sys.exit(0)

except Exception as e:
    import traceback
    traceback.print_exc()
    print('\nInstantiation/inspection failed:', e)
    sys.exit(3)
