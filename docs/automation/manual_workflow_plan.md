# Manual Workflow Plan

Status: manual automation guide for Vibe Signal.

## Production Smoke

Run after deploy or when debugging hosted backend flow:

```bash
bash scripts/prod_smoke_all.sh https://vibe-signal.onrender.com
```

This uses synthetic payloads only and verifies bounded metadata endpoints. By default, the wrapper passes the current `git rev-parse HEAD` value into deployed-version verification. If the script is run outside a git checkout, it still runs but deployed-version proof may remain `unverified`.

Production smoke success is not the same as deployed commit proof. The deployed backend must expose a safe `/api/status.git_commit` value that matches the expected SHA for deploy status to be `current`.

## Closed-Beta Gate

Run for release-candidate review:

```bash
bash scripts/closed_beta_gate_all.sh
```

The wrapper verifies deployed metadata directly and passes `current`, `stale`, or `unverified` into the closed-beta gate report. It does not treat production smoke success alone as deployed-version proof.

By default, wrapper-generated reports are written under ignored automation output paths such as `reports/automation/latest/`. To intentionally refresh tracked gate evidence, run:

```bash
WRITE_REPORT=1 bash scripts/closed_beta_gate_all.sh
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
