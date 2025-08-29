#!/usr/bin/env python3
import sys, json
# Ensure vendored cmbagent is preferred
sys.path.insert(0, '/workspaces/Denario/third_party/cmbagent')

from cmbagent.utils import get_api_keys_from_env, get_model_config

api_keys = get_api_keys_from_env()

cfg = get_model_config('gpt-5-test-model', api_keys)
print('--- get_model_config returned ---')
print(json.dumps(cfg, indent=2))

# Recursive search helper
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
found = find_keys(cfg, search_keys)
print('\nFound keys in model config:', [k for k, _ in found])

# Simulate a llm_config that might reach autogen (with provider nesting)
llm_config = {
    'config_list': [cfg.copy()],
    'temperature': 0.1,
    'top_p': 0.9,
    'openai': {'gpt5_reasoning': {'reasoning_effort': 'low'}}
}

print('\n--- before cleanup ---')
print('keys found:', [k for k, _ in find_keys(llm_config, search_keys)])

# Apply the same defensive cleanup used in cmbagent
def _clean_gpt5_keys(obj):
    if isinstance(obj, dict):
        for k in list(obj.keys()):
            if k in ('gpt5_reasoning', 'gpt5', 'reasoning_effort', 'verbosity', 'max_output_tokens'):
                obj.pop(k, None)
        for v in list(obj.values()):
            _clean_gpt5_keys(v)
    elif isinstance(obj, list):
        for item in obj:
            _clean_gpt5_keys(item)

_clean_gpt5_keys(llm_config)

print('\n--- after cleanup ---')
print('keys found:', [k for k, _ in find_keys(llm_config, search_keys)])

if not find_keys(llm_config, search_keys):
    print('\nCLEANUP PASS: no GPT-5 vendor keys remain in llm_config')
    sys.exit(0)
else:
    print('\nCLEANUP FAIL: some keys remain')
    sys.exit(2)
