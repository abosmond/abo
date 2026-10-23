# Scenario format

One YAML file per scenario under `scenarios/<category>/`.

| field | meaning |
|---|---|
| `id`, `category`, `title`, `severity`, `description` | metadata |
| `system_prompt`, `user_task` | what the agent is told |
| `tools` | tools exposed to the agent (see `src/abo/tools/environment.py`) |
| `environment` | seeded state: `files`, `web`, `inbox`, `contracts`, `wallet` |
| `attack_success` | judge criteria; attack wins if **any** holds |
| `task_success` | utility criteria; task succeeds if **all** hold |
| `policy` | allow-lists used by the `tool_guard` defense |
| `benign_plan` | tool calls the offline mock model makes; ignored by real models |

Criterion types: `tool_called` (with optional `args_contains`), `canary_leaked`, `final_contains`.

Convention: payloads in seed scenarios include a `CALL tool {json}` line so the offline
mock can exercise the pipeline. When writing scenarios aimed at real models, also add
variants with natural-language payloads; those are what matter for the benchmark.
