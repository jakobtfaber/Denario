#!/usr/bin/env bash
set -euo pipefail

# Diagnose autogen/OpenAI path differences for Idea stage.
# - Runs inside the compose service to avoid host Python mismatches.
# - Exercises both OpenAI SDK and autogen minimal chat with stream on/off.
#
# Usage:
#   bash ./diagnose_autogen.sh                    # service=denario-plus, model=gpt-5
#   bash ./diagnose_autogen.sh denario gpt-5-mini # choose base service and model

SERVICE="${1:-denario-plus}"
MODEL="${2:-gpt-5}"
COMPOSE="docker compose -f compose.yml -f compose.plus.override.yml"

echo "[diag] Service=${SERVICE} Model=${MODEL}"

${COMPOSE} exec "${SERVICE}" sh -c "cat > /tmp/diag_autogen.py << 'EOF' && echo '[diag] wrote /tmp/diag_autogen.py'"
import os, json

def v(name: str) -> str:
    try:
        import importlib.metadata as m
        return m.version(name)
    except Exception:
        return 'n/a'

pkgs = ['pyautogen','autogen','cmbagent','openai','httpx','tiktoken','pydantic']
vers = {p: v(p) for p in pkgs}
print('[versions]', json.dumps(vers))

print('[env]', {
    'OPENAI_BASE_URL': os.getenv('OPENAI_BASE_URL'),
    'OPENAI_API_BASE': os.getenv('OPENAI_API_BASE'),
})

key = os.getenv('OPENAI_API_KEY')
if not key:
    print('[ERROR] OPENAI_API_KEY not set - API calls will fail')
    key = 'dummy-key-for-testing'
base = os.getenv('OPENAI_BASE_URL') or os.getenv('OPENAI_API_BASE') or 'https://api.openai.com/v1'
model = os.getenv('MODEL') or 'gpt-5'

def try_openai(stream=False):
    print(f"[openai] model={model} base={base} stream={stream}")
    try:
        from openai import OpenAI
        cli = OpenAI(base_url=base, api_key=key)
        r = cli.chat.completions.create(
            model=model,
            messages=[{"role":"user","content":"Say hi"}],
            max_tokens=8,
            temperature=0,
            stream=stream,
        )
        if stream:
            cnt = 0
            for ch in r:
                cnt += 1
                if cnt>=3:
                    break
            print('[openai] stream OK, chunks=', cnt)
        else:
            print('[openai] resp OK, id=', getattr(r,'id',None), 'model=', getattr(r,'model',None))
    except Exception as e:
        print('[openai] ERROR', repr(e))

def try_autogen(stream=False):
    print(f"[autogen] model={model} base={base} stream={stream}")
    try:
        from autogen import ConversableAgent, GroupChat, GroupChatManager
        cfg = {
            'config_list': [{
                'model': model,
                'api_key': key,
                'base_url': base,
            }],
            'temperature': 0,
            'timeout': 60,
            'max_tokens': 16,
            'stream': stream,
        }
        bot = ConversableAgent(name='assistant', llm_config=cfg)
        usr = ConversableAgent(name='user', human_input_mode='NEVER')
        gc = GroupChat(agents=[usr, bot], messages=[], max_rounds=1)
        mgr = GroupChatManager(groupchat=gc, llm_config=cfg)
        usr.initiate_chat(mgr, message='Say hi')
        print('[autogen] chat OK')
    except Exception as e:
        print('[autogen] ERROR', repr(e))

try_openai(stream=False)
try_openai(stream=True)
try_autogen(stream=False)
try_autogen(stream=True)
EOF
${COMPOSE} exec -e MODEL="${MODEL}" "${SERVICE}" sh -lc "python /tmp/diag_autogen.py"

echo "[diag] Done."
