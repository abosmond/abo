# ABO

**Security evaluation harness for tool-using LLM agents.**

ABO runs an LLM agent through attack scenarios (direct and indirect prompt injection,
data exfiltration, tool abuse, and on-chain actions such as malicious token approvals),
then measures how often the attack succeeds and whether the agent still completes the
user's real task. Defenses are plug-ins, so you can compare them side by side.

All tools are simulated. Nothing touches real email, files, networks, or blockchains.

## Quick start

```bash
pip install -e ".[dev]"
abo list
abo run --models mock --defenses none,spotlighting,tool_guard
```

With real models (keys in environment, see `.env.example`):

```bash
pip install -e ".[anthropic,openai]"
abo run --models anthropic:claude-sonnet-4-6,deepseek:deepseek-chat \
        --defenses none,spotlighting,tool_guard --out results/run1.json
abo report results/run1.json
```

The `mock` model has zero injection resistance and exists only to test the pipeline.
Its numbers say nothing about real models.

## Scenario categories

| category | example |
|---|---|
| `direct_injection` | user tries to extract a secret from the system prompt |
| `indirect_injection` | poisoned web page or KB article hijacks the agent |
| `exfiltration` | email instructs the agent to forward an API key |
| `tool_abuse` | README tells a file agent to delete backups |
| `onchain` | contract metadata triggers an unlimited token approval |

## Defenses (v0.1)

- `none` — baseline
- `spotlighting` — delimit and datamark untrusted tool output
- `tool_guard` — deterministic allow-list on sensitive tool arguments

Note: `II-002` shows that argument allow-lists cannot stop content-level attacks.

## Repo layout

```
src/abo/
  cli.py            abo list | run | report
  scenario.py       YAML schema + loader
  models/           mock, Anthropic, OpenAI-compatible (OpenAI, DeepSeek)
  agent/runner.py   JSON tool-call agent loop
  tools/            simulated environment (files, web, inbox, wallet)
  defenses/         none, spotlighting, tool_guard
  judges/           rule-based attack / utility criteria
  report/           ASR and utility tables
scenarios/<category>/*.yaml
docs/               threat model, scenario format, roadmap
tests/
```

## Ethics

ABO is for evaluating and hardening systems you own or are authorized to test.
Scenarios use fictional domains and simulated tools only.

## License

MIT
