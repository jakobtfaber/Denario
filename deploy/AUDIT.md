### Denario-Docker Audit: Bugs, Shortfalls, and Gaps

Last updated: <!-- keep updated when changes are made -->

#### Critical bugs
- **DenarioApp README malformed volume mount**: `-v $(pwd).env/app/.env` is invalid. Should be `-v $(pwd)/.env:/app/.env`.
- **Port mapping mismatch (plus variant)**: Docs imply 7861/8081; `compose.plus.override.yml` maps 7871/8091.
- **Missing `.env.example`**: Root README instructs `cp -n .env.example .env`, but file does not exist.
- **Healthcheck depends on unset `PORT`**: Dockerfile `HEALTHCHECK` uses `http://localhost:$PORT/_stcore/health`, but compose does not set `PORT`; yields `http://localhost:/_stcore/health` and failing health checks.

#### Functional shortfalls / robustness gaps
- **No tests**: No unit/integration tests for proxy, scripts, or boot paths.
- **Cache sizing not configurable**: `SimpleTTLCache` hardcodes `maxsize=1024`; only TTL is effectively configurable.
- **Limited cache coverage**: Only non-streaming `chat/completions` and `embeddings` POSTs cached; no GET cache or invalidation hooks.
- **No CORS configuration**: Cross-origin browser clients to `:8080` may fail.
- **Token estimation scope**: TPM enforcement estimates only for `chat/completions`; embeddings/others count as 0 tokens.
- **Weak model→encoding mapping**: Heuristic/substrings in `tokenizer.py` can mis-estimate tokens for newer/unknown models.
- **Retry policy tuning limited**: Only `UPSTREAM_RETRY_ATTEMPTS`; no max backoff/jitter/per-status controls.
- **Healthcheck minimal**: `/healthz` lacks cache stats, concurrency usage, tokens used/window reset, etc.
- **Missing runtime dependency (Pillow)**: `DenarioApp/src/denario_app/components.py` imports `PIL.Image`, but `DenarioApp/pyproject.toml` does not declare `pillow`; runtime import may fail.
- **Model object vs name inconsistency**: In `components.py`, `idea_comp`/`results_comp` pass `models[... ]` objects, but `method_comp` passes raw strings (`planner_model`, `plan_reviewer_model`, `method_generator_model`). This inconsistency may break `den.get_method(...)` if it expects model objects.
- **Plots rendering gap**: UI expects plots under `project_dir/input_files/plots`, but no guarantee upstream agents write them there; no explicit empty-state guidance or user help.

#### Reliability and UX issues
- **App path resolution brittleness (`start.sh`)**: Variable naming confusion and surprising selection when multiple copies exist.
- **Default model remapping surprises**: `MODEL_ALIAS_PREFIXES='{"gpt-":"gpt-5-mini"}'` silently remaps any `gpt-*` (hard to diagnose).
- **Timeout coupling**: JSON timeout capped by `TIMEOUT_STREAM_SECONDS`, causing unexpected 504s if stream timeout reduced.
- **Script fragility and blocking**: `verify_idea_pipeline.sh`/`diagnose_autogen.sh` assume services are running and can hang on `compose exec`; no timeouts or readiness checks; hard-coded to `compose.plus.override.yml`.
- **Proxy cache key misses auth/base**: Cache key excludes headers and base URL; responses fetched against different upstreams or auth contexts could collide. Consider including `settings.upstream_base_url` and a non-secret auth identity hash.
- **Token count underestimation**: `count_chat_message_tokens` ignores tool_calls and other fields; can under-budget TPM, defeating fallback logic in edge cases.
- **Proxy readiness race**: `start.sh` waits only 0.5s after starting the proxy; first requests can hit a not-yet-ready proxy in slower environments.
- **Silent model injection shim**: `sitecustomize.py` injects `gpt-5-mini` into `denario.models` when absent. While convenient, it can create surprising UI defaults and make debugging model selection harder.

#### Documentation inconsistencies/typos
- **Wrong ports in docs (plus variant)**: See above mismatch.
- **Typos**: "HugginFace"/"Huggin Face" appear; should be "Hugging Face".
- **Product naming**: Repo consistently says Denario; if target name differs, it’s not reflected.
- **Repo hygiene drift**: Docs mention `.dockerignore` and `.gitignore` contents, but these files are not present at the root.

#### Security and config hygiene
- **No `.env.example` template**: Harder secure onboarding; encourages ad-hoc env handling.
- **Proxy auth header pass-through risks**: Forwarding client Authorization when `OPENAI_API_KEY` unset is fine, but risks/behavior undocumented.
- **Log redaction**: Proxy logs selected request keys; future changes might log sensitive fields without redaction.

#### Performance notes
- **Single-process in-memory cache**: No shared state across instances; scaling multiplies rate budgets and fragments cache.
- **Token estimation fallback**: Without `tiktoken`, char/4 heuristic can be very inaccurate for TPM gating.
- **Compose bind-mount/version skew**: Bind-mounting `./DenarioApp` while also pip-installing DenarioApp can cause version skew between source and installed package.

---

### Suggested remediation backlog (initial)
- Add `.env.example` and fix README/port docs; align compose plus ports to docs or vice versa.
- Make cache `maxsize` configurable and expose CORS toggle (env based).
- Extend TPM estimation to embeddings and add endpoint-aware budgeting hooks.
- Expand `/healthz` with cache stats, concurrency, token window usage; consider `/metrics`.
- Harden `start.sh` path resolution; print deterministic selection.
- Add basic tests (proxy request normalization, aliasing, rate limits, cache HIT/MISS, timeouts).
- Improve tokenizer mapping, or allow specifying encoding via env/model-registry.
- Expand retry/backoff configuration (base delay, max delay, jitter, status-class policies).
- Add `pillow` dependency to DenarioApp; add import checks on boot with actionable errors.
- Normalize model parameters across components (`models[...]` vs string) and document expected types for `Denario` API.
- Add readiness checks and timeouts in scripts; allow selecting compose files/services via flags.
- Include base URL and a hashed auth identity in cache key (avoid secrets); optionally namespace cache per-upstream.
- Add `.dockerignore` and `.gitignore` per docs to reduce build context and keep hygiene.

---

### Targeted micro-tests and checks (proposed)
- Import checks inside container:
  - `python -c "import PIL, streamlit_pdf_viewer; print('OK')"` → validate missing `pillow`.
  - `python -c "from denario_app import app as A; print('app ok')"` → module load.
- Proxy behavior:
  - POST `/v1/chat/completions` with large `max_tokens` to trigger fallback; verify model switch and 200 vs 429.
  - Same body, different `OPENAI_BASE_URL`; verify cache namespacing prevents cross-upstream HITs after change.
  - Send `temperature: null` and `logprobs` to ensure sanitization.
- Script safety:
  - Run `verify_idea_pipeline.sh` against stopped services; ensure it fails fast with clear message (after adding readiness guards).
- UI flows:
  - Exercise `idea_comp` fast/slow and `method_comp` to confirm model param types and address mismatches.

