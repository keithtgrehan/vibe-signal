# Vibe Signal Agent Library

Status: reusable automation and Codex prompt library for closed-beta maintenance. This is not a production launch, legal/privacy approval, App Store approval, or model-quality claim.

These agents make repeated Vibe Signal work easier to assign, review, and validate. They are prompts and operating checklists only. Human gates remain human, especially legal/privacy approval, real-device QA, human-reviewed labels, tester invites, App Store metadata, and public marketing claims.

## Safety Defaults

Every agent must preserve:

- no raw private chats
- no unsafe relationship claims
- no legal/compliance overclaim
- no model-accuracy overclaim
- synthetic examples only unless explicitly approved
- human gates remain human
- no cheating detection, hidden-intent claims, attraction prediction, lie detection, diagnosis, attachment-style or neurotype inference, therapy framing, manipulation tactics, fake compliance claims, user/tester training data, or raw message storage

## Available Agents

Use `python scripts/print_agent_prompt.py --list` to list prompt keys.

| Key | File | Use |
| --- | --- | --- |
| `controller` | `controller_agent.md` | Coordinate multi-agent sprints and final go/no-go reports. |
| `product_ethics` | `agent_1_product_psychology_ethics.md` | Review motivation, cognitive load, trust calibration, and anti-dark-pattern choices. |
| `dataset_rights` | `agent_2_dataset_rights_gate.md` | Guard dataset registry, source rights, and fail-closed training paths. |
| `engine_eval` | `agent_3_nlp_engine_eval.md` | Run synthetic cue regression, hard negatives, metrics, and review-packet work. |
| `safe_output_ux` | `agent_4_trust_explainability_safe_output_ux.md` | Improve evidence-first UX, cannot-infer blocks, and safe repair suggestions. |
| `ios_testflight` | `agent_5_ios_testflight_launch.md` | Prepare iOS/TestFlight metadata, QA, and App Store-sensitive copy. |
| `web_growth` | `agent_6_web_growth_landing_page.md` | Improve hosted web clarity and synthetic demo conversion without dark patterns. |
| `competitive_research` | `agent_7_competitive_category_research.md` | Maintain category map and safe positioning research. |
| `implementation_planner` | `agent_8_codex_implementation_planner.md` | Convert research into PR sequence, acceptance criteria, and validation commands. |
| `deployment` | `deployment_production_agent.md` | Verify Render/Vercel envs, CORS, smoke tests, and deploy metadata. |
| `safety_copy` | `safety_copy_guardrail_agent.md` | Run public-copy, no-raw, and safety blocker reviews. |
| `recruiter_demo` | `recruiter_demo_agent.md` | Keep README, repo tour, summaries, and demo path honest. |
| `human_labeling` | `human_labeling_agent.md` | Prepare reviewer packets, label templates, and adjudication workflow. |
| `closed_beta_gate` | `closed_beta_gate_agent.md` | Run release gates and document tester-invite blockers. |
| `ui_ux` | `ui_ux_product_design_agent.md` | Review first-10-seconds UX, mobile hierarchy, accessibility, and result cards. |
| `repo_maintenance` | `repo_maintenance_agent.md` | Keep root, generated artifacts, commands, and dependency notes tidy. |

## Local Commands

```bash
python scripts/print_agent_prompt.py --list
python scripts/print_agent_prompt.py controller
bash scripts/agent_control_room_check.sh
```

## Review Rule

Agent output can recommend, draft, or validate. It must not claim a manual gate has passed unless a named human owner supplied evidence.
