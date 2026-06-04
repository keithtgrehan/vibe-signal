# Agentic Workflow Guide

Status: reusable workflow guide for Vibe Signal maintenance. This does not approve production launch, legal/privacy compliance, App Store release, or model quality.

## Daily Loop

1. Run `bash scripts/dev_check_all.sh` before broad changes.
2. Pick one agent from `docs/agents/` and keep the branch scoped to that agent's files.
3. Use synthetic examples only.
4. Run the agent-specific validation commands.
5. Summarize safety/privacy impact in the PR.

## Weekly Loop

1. Run bounded engine eval with `bash scripts/engine_eval_all.sh`.
2. Review UI/demo polish through the UI/UX or Web Growth agent.
3. Run safety/privacy/release gates with `bash scripts/dev_check_all.sh` and `bash scripts/closed_beta_gate_all.sh`.
4. Check deployment/TestFlight readiness with the Deployment and iOS agents.
5. Refresh README/recruiter packaging through the Recruiter Demo agent.
6. Prepare or review human labels only through the Human Labeling agent.

## Agent Selection

- Engine behavior or reports: Agent 3.
- Public copy or output claims: Safety Copy Guardrail Agent.
- Hosted web/deployment: Deployment Production Agent.
- Release status: Closed Beta Gate Agent.
- Repo packaging: Recruiter Demo Agent or Repo Maintenance Agent.
- Multi-branch work: Controller Agent first.

## Non-Negotiable Boundaries

- no raw private chats
- no unsafe relationship claims
- no legal/compliance overclaim
- no model-accuracy overclaim
- synthetic examples only unless otherwise approved
- human gates remain human

Agents can produce evidence and recommendations. They cannot approve legal/privacy status, real-device QA, human-reviewed labels, tester invites, App Store metadata, or public marketing claims.
