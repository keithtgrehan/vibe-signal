# Manual Workflow Plan

Status: manual automation guide for Vibe Signal.

## Production Smoke

Run after deploy or when debugging hosted backend flow:

```bash
bash scripts/prod_smoke_all.sh https://vibe-signal.onrender.com
```

This uses synthetic payloads only and verifies bounded metadata endpoints. It does not run the full 10k suite against production.

## Closed-Beta Gate

Run for release-candidate review:

```bash
DEPLOY_STATUS=current bash scripts/closed_beta_gate_all.sh
```

The result is evidence for a human decision. It does not approve tester invites.

## Full Engine Evaluation

Run manually when engine reports need refreshing:

```bash
ENGINE_EVAL_MESSAGES=10000 ENGINE_EVAL_SPLITS=dev=6000,hard_negative=2000,heldout=1000,red_team=1000 bash scripts/engine_eval_all.sh
```

Reports are bootstrap-only synthetic regression evidence pending human-reviewed labels.

## Agent Prompt Use

```bash
python scripts/print_agent_prompt.py --list
python scripts/print_agent_prompt.py engine_eval
```

Copy the printed prompt into Codex and keep the branch scoped to that agent.

## Safety Rules

Do not paste private chats into scripts, docs, issues, PRs, screenshots, or logs. Do not claim legal/privacy approval, App Store approval, production launch, or real-world NLP accuracy from automation output.
