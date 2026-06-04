# Simple UI Information Architecture

Date: 2026-06-04

## Target Structure

1. Header
2. Hero
3. Goal selector
4. Main mode panel
5. Result panel / preview
6. Short How it works
7. Small Can / Cannot boundary
8. Footer/legal links

## Above The Fold

The first viewport should show:

- Product one-liner.
- Short synthetic-or-permissioned subcopy.
- Goal selector.
- Demo Mode / Analyze Text segmented control.
- Active interaction panel.
- Result preview or current result.

## Main Workspace

Desktop:

- Left column: goal, mode, context/style, demo cards or analyze form.
- Right column: result preview/result artifact.

Mobile:

- One-column guided flow.
- Goal first, mode second, active panel third, result fourth.
- Result panel is not sticky on mobile.

## Keep

- Synthetic demos.
- Consent gate for private text.
- Evidence-first result.
- Cannot-infer boundary.
- Metadata-only feedback.
- Legal/privacy footer access.

## Remove Or Collapse

- Excessive landing sections.
- Repeated safety copy.
- More than three visible demo cards by default.
- Dense FAQ above the fold.
- Excessive headings.
- Repeated borders around nested card stacks.

## Backend Boundary

Goal, context, and analysis style stay client-side only. They may adjust UI wording and suggested next-step copy, but they must not change backend inference or add fields to `/api/analyze`.
