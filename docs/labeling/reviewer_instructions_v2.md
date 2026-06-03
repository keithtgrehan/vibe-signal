# Reviewer Instructions V2

Status: instructions for future human review of the synthetic review packet. The current packet is not human reviewed.

1. Review only the visible synthetic conversation text.
2. Mark a cue present only when the evidence text directly supports it.
3. Use `low_signal_flag` when the text is too short or context-light.
4. Use `unsafe_wording_flag` when an output or suggested label would imply a blocked inference.
5. Do not label hidden intent, cheating, attraction, deception certainty, diagnosis, neurotype, attachment style, true emotion, or relationship outcome.
6. Treat bootstrap expected cues as suggestions only.
7. Add notes when a false positive appears to come from overlapping cue families.
8. Do not add real chats, tester messages, screenshots, names, phone numbers, addresses, or external dataset text.
