# Sprint Templates

Status: reusable prompt and report templates for Vibe Signal agent work.

## One-Agent Sprint Prompt

```text
Run the <agent name> for Vibe Signal.

Goal:
<one scoped goal>

Branch:
codex/<scope>

Constraints:
- no raw private chats
- no unsafe relationship claims
- no legal/compliance overclaim
- no model-accuracy overclaim
- synthetic examples only unless otherwise approved
- human gates remain human

Tasks:
1. Inspect current repo state.
2. Make scoped changes.
3. Run agent-specific validation.
4. Document skipped checks with reasons.
5. Open a PR if GitHub auth is available.
```

## Multi-Agent Sprint Prompt

```text
Run the Controller Agent for Vibe Signal.

Coordinate these agents:
- <agent A>
- <agent B>
- <agent C>

Keep branch scopes isolated, preserve merge order, use synthetic examples only, and produce a final go/no-go report with validation evidence and manual gates.
```

## Final Report Shape

1. Branch name.
2. Commit hashes.
3. PR link.
4. Files changed.
5. Validation results.
6. Skipped validations and reasons.
7. Safety/privacy notes.
8. Static grep result if public copy changed.
9. Remaining manual gates.
10. Next three improvements.

## Reviewer Checklist

- Scope matches the selected agent.
- Required validation ran or was skipped with a clear reason.
- No raw private chats or private tester data.
- No unsafe relationship claims.
- Manual gates are not self-approved.
- Public copy is scanner-clean or allowlisted for a narrow safety reason.
