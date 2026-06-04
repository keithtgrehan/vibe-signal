# UI Minimal Redesign Research Agents

## Agent 1 - UX Clarity Researcher

### UX thesis

Vibe Signal should be understood as a calm message-reading aid: it shows what the wording is doing, then helps the user choose a clearer next step without guessing what anyone feels.

### Single clearest user problem

Users get stuck between over-reading and under-reacting when a message feels unclear. Vibe Signal helps them slow down, look at the exact words, and decide what to ask next.

### Current confusion or cognitive load

- The first screen splits attention across goals, modes, context, style, multiple demos, trust chips, and long boundary sections.
- The UI reads like an internal dashboard because it exposes configuration before the user sees value.
- Safety language is correct but repeated in too many places, making the product feel defensive instead of useful.
- The result area is visually secondary until the user has navigated several controls.

### What users should see first, second, and third

1. A plain promise: see what a message is doing without guessing feelings.
2. One safe synthetic example with a clear demo button.
3. A result card ordered by what stands out, evidence, possible meaning, safer reply, and limits.

### What to remove

- Goal selector.
- Context selector.
- Analysis style selector.
- Comparison mode from the first-screen flow.
- Multiple primary demo cards.
- Large can/cannot boundary panels.
- Trust-chip wall.
- Repeated legalistic safety explanations.

### What to keep

- Synthetic demo first.
- Permission checkbox before analyzing pasted text.
- Evidence before interpretation.
- Short limits beside the result.
- Metadata-only feedback behavior.
- Existing backend analyze and feedback contracts.

### New first-screen hierarchy

1. Sticky nav with logo, Demo, How it works, Privacy, and Run demo.
2. Hero promise, short explanation, two CTAs, and one trust line.
3. Demo/result two-column workspace with the result as the visual center.

### One-sentence user journey

Land, understand the promise, run one synthetic demo, see an evidence-first result, read a short limit, then choose whether to analyze their own permitted text.

## Agent 2 - UI Minimalism Researcher

### UI thesis

Use the existing navy, slate, and amber palette, but turn the page into a single product flow: hero, demo/result, simple analyzer, three-step explanation, and a compact trust footer.

### Layout rules

- One primary action per section.
- No nested cards inside cards.
- Result card stays visually dominant.
- Use larger whitespace and fewer borders.
- Keep amber for the primary action only.
- Use green/red only for functional success and error states.
- Keep tap targets at least 44px.

### Component simplification list

- Replace three demo cards with one featured demo and a collapsed example disclosure.
- Replace evidence table with a compact evidence list.
- Remove mode segmented control; demo and analyze become separate sections.
- Remove goal/context/style controls from the landing page.
- Keep feedback controls in a small metadata-only block after the result, not inside every evidence row.
- Collapse optional examples rather than showing a chip wall.

### Desktop structure

- Sticky nav.
- Hero in one clean viewport with the demo/result section visible below the fold.
- Two-column demo/result section: demo card left, result card right.
- Analyze section below the demo/result area.
- How it works in three compact columns.
- Single-line trust footer.

### Mobile structure

- Sticky nav wraps cleanly without horizontal overflow.
- Hero stacks with CTAs under copy.
- Demo card appears before result.
- Result sections stack in the fixed order.
- Analyze textarea, consent, and button remain full width.

## Agent 3 - Human Copy and Emotional Pull Researcher

### Copy thesis

Use the relief of slowing down as the emotional hook: "Stop guessing. Look at the wording." Keep the product inviting by naming uncertainty without fear, shame, jealousy, urgency, or relationship-truth claims.

### Hero copy options

- "See what a message is doing - without guessing what someone feels."
- "When a message feels unclear, look at the words before you reply."
- "Get a calmer read before you send the next text."

### CTA options

- "Run a demo"
- "Analyze text"
- "See the example"
- "Try your text"

### Result-card copy

- Title: "What stands out"
- Evidence label: "The exact words that triggered it"
- Interpretation label: "What it could mean"
- Safer reply label: "Safer reply"
- Limits label: "What it can’t know"

### Microcopy for consent, limits, and safer reply

- Consent: "I have permission to analyze this text."
- Helper: "Avoid sensitive, legal, medical, workplace, or third-party private content unless you have the right to use it."
- Limits: "This does not tell you what they feel or intend."
- Safer reply: "You stay in control of the reply. Edit before sending."
- Demo privacy: "No private chats stored for this demo."

### Blocked phrases list

- "Find out what they really think."
- "Know if they like you."
- "Catch them lying."
- "Decode their secret feelings."
- "Make them reply."
- "Win them back."
- "Don’t get played."
- "Use this before it is too late."

## Agent 4 - Safe Persuasion / Legal Boundary Researcher

### Safe persuasion thesis

The strongest safe promise is: Vibe Signal helps users understand how wording may land, where ambiguity or pressure appears, and what clearer reply options exist.

### Allowed language

- "This sounds vague."
- "This puts pressure on timing."
- "This avoids the direct ask."
- "This reply gives no clear next step."
- "This may land heavier than intended."
- "This has a repair opening."
- "This gives you room to ask directly."
- "The wording creates ambiguity."
- "The message asks for a response without giving much room."
- "A clearer next step would reduce friction."

### Blocked language

- Claims that the product knows intent, feelings, truthfulness, health labels, cheating, attraction, or outcomes.
- Claims that the product can make someone reply or help a user get what they want from another person.
- Claims of legal compliance or legal, medical, therapeutic, or diagnostic advice.

### Result interpretation boundaries

- Interpretation must follow quoted evidence.
- "What it could mean" must stay conditional and observable.
- The limit must be visible in the result card.
- Reply suggestions must reduce pressure and preserve user agency.

### Final recommendation

Make the product promise bolder in usefulness, not in inference. Say it helps users stop guessing and inspect wording; never say it reveals what another person thinks, feels, hides, or will do.
