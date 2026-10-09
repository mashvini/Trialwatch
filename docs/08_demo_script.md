# Demo script (about 12 minutes)

Aim for 12 minutes so there's room within the 10–15 minute slot. Rehearse twice on Saturday (14:30–15:15).

## Before going on stage
- [ ] Mode set to **mock** (saved real outputs) unless the API has been stable all day
- [ ] Demo case selected; reviewer name filled in; all modules unticked (you'll switch them on during the demo)
- [ ] Browser zoom at about 125% so the back row can read it
- [ ] Backup video open in another tab
- [ ] Evaluation numbers filled in on the slide

## Flow
| Time | Who | What to show | What to say |
|---|---|---|---|
| 0:00–1:30 | Presenter | Slide: the problem | Lawyers know what happened in court but must work out what it means legally, across piles of notes. The organizers' own rule: the tool supports the lawyer's judgment, it doesn't replace it |
| 1:30–2:30 | Presenter | Slide: the pipeline | One sentence on what FairTrace does; point out the three steps that use AI and the rest that is plain code |
| 2:30–3:30 | Coder | **Sources** tab | Every line is numbered by code, not by the AI. These numbers are how every claim gets checked |
| 3:30–5:30 | Coder | Run analysis → **Issues to review** | A potential issue with the right to examine witnesses, its source line, the questions for the lawyer, and the missing facts. Accept one; reject one. Mention the audit log |
| 5:30–6:00 | Coder | **Rejected by the verifier** panel | The guardrail at work: a citation that didn't check out was stopped |
| 6:00–7:30 | Coder | Tick **Copy-Through** | Paragraph 3 of the judgment repeats the police report word for word, inside the court's own reasoning. The quoted charges in paragraph 1 are *not* flagged: quoting the charges is normal |
| 7:30–9:00 | Coder | Tick **Devil's Advocate** | On the Copy-Through flag: the state could argue the court was only summarizing; the record rebuts that, because the passage is in the reasoning section. On another flag the record is silent, so it becomes a question for the monitor |
| 9:00–9:45 | Coder | **Questions for the monitor**, then **Export** | Questions grouped by hearing; draft findings with footnotes, accepted issues only |
| 9:45–10:45 | Presenter | **Evaluation** tab / slide | Caught [X] of [Y] expected issues, [Z] false alarms on the clean hearing, every citation verified |
| 10:45–12:00 | Presenter | Slide: responsible AI and deployment | Local mode for confidential data; lawyers edit the rights list; limitations; next steps |

## If something breaks
- API error → switch the sidebar to `mock` and run again (results are saved).
- App won't start → play the backup video and narrate over it.
- Laptop failure → slides plus the video on a teammate's laptop.

## Q&A
See the prepared answers in [07_responsible_ai.md](07_responsible_ai.md#judge-qa-prep). Decide in advance who answers technical questions and who answers legal and ethics questions.
