# Build plan

All times are New York time (ET). India (IST) is 9 hours 30 minutes ahead.

## Before Friday

### Close the open decisions
If a decision is still open at its deadline, the default applies. Record final choices in [05_decisions_and_open_questions.md](05_decisions_and_open_questions.md).

| Pending decision | Decide by | Default if still open |
|---|---|---|
| API, local, or both | Thu 9 PM | Groq for the demo, with Ollama as a config option and mock mode as the safety net |
| Data source (organizers' reply) | Thu 9 PM | Synthetic monitor notes written from the Pan Thalufah report |
| Can code be written before the event? | Thu 9 PM | Only this starter skeleton; analysis logic from Friday |
| Rights list and answer key | Thu night | Law teammate drafts them; finished Friday morning |
| Team roles | Thu 9 PM | Coder (you), law teammate (legal content), presenter (docs and slides) |
| Who builds Copy-Through | Thu 9 PM | A second person on Friday afternoon if available; otherwise the coder on Saturday morning |

### Inputs needed from teammates by Thursday night
Details and templates: [09_teammate_inputs.md](09_teammate_inputs.md).
- `taxonomy/rights.yaml` reviewed (the draft covers 8 rights)
- Sample notes for 3–4 hearings, including **one hearing with no problems**
- `answer_key.yaml` for those notes
- 2 worked examples (`taxonomy/worked_examples.yaml`)
- If possible, a judgment and an indictment or police report in the same language, for Copy-Through

### Coder prep checklist
- [ ] Unzip the starter, then run `pytest` and `streamlit run app.py` (mock mode)
- [ ] Create a Groq account; put the key in `.env`; set `providers.api.model` in `config.yaml`
- [ ] Install Ollama and pull a model that fits your Mac (see [06_model_options.md](06_model_options.md)); set `providers.local.model`
- [ ] Each teammate creates their own Groq account (limits apply per account)
- [ ] Create the GitHub repo (public at submission time) and push the starter
- [ ] Read [../AGENTS.md](../AGENTS.md) and the task board below

## Two-day schedule

### Friday: build the core
| Time | You (code) | Second coder / law teammate | Presenter / docs |
|---|---|---|---|
| 10:00–11:30 | Registration and launch. **Listen for new information** (data, credits, rules) | Same | Same |
| 11:30–12:00 | **Decision meeting over lunch** (15 min): confirm every default | | |
| 12:00–13:00 | **T1** ingest; check mock mode end to end | Finish the test notes and rights list | README outline, license, ethics notes |
| **13:00** | **Mentor 1:** Is the problem right? Is the rights list right? What does a lawyer want to see? | | |
| 13:30–16:00 | **T2** extract, **T3** flag, **T4** verify | **T7** Copy-Through (if a second coder), or test prompts in a chat tool and write the answer key | Slide structure, written description |
| **16:00 checkpoint** | **One complete run on the demo notes, every flag with verified sources** | | |
| **16:00** | **Mentor 2:** show the first run, get feedback on the flags | | |
| 16:30–17:00 | Turn the feedback into a fix list | | |
| Evening (max 3 hrs) | **T6** Devil's Advocate, **T5** review polish, **T10** evaluation, record real outputs as fixtures | Check flags, refine prompts and examples | Draft slides |

### Saturday: finish and demo
| Time | You (code) | Team |
|---|---|---|
| 10:00–11:00 | **T9** export, accuracy numbers on screen; **T7** Copy-Through if not done | Finish slides and the ethics section |
| **11:00** | **Mentor 3:** full demo rehearsal; practice ethics and feasibility answers | |
| 11:30–13:00 | Fixes and polish; **T8**, **T11**, **T12** only if time allows | Revise slides from mentor feedback |
| **13:00** | **FEATURE FREEZE. No new features after this point** | |
| 13:00–14:30 | **T13** ship: README, license, saved demo results, backup video | Finish the written description |
| 14:30–15:15 | Two full timed rehearsals, aiming for about 12 minutes | |
| **15:15** | **Submit**, 15 minutes before the 3:30 PM deadline | |

## Build phases
| Phase | When | Build | Done when |
|---|---|---|---|
| 0. Prep | Thu | Starter skeleton (this kit), accounts, models, teammate inputs | `pytest` passes; the app runs in mock mode |
| 1. Skeleton live | Fri 12:00–13:00 | T1 | The Sources tab shows numbered lines for the demo case |
| 2. Core | Fri 13:30–16:00 | T2, T3, T4 | **16:00: a full run where every flag has verified sources** |
| 3. Signature + review | Fri evening | T5, T6, T10, plus T7 if a second coder built it | A lawyer can review every flag and see the state's counter-argument |
| 4. Finish | Sat 10:00–13:00 | T7 (if not done), T8, T9, stretch goals | **13:00 feature freeze** |
| 5. Ship | Sat 13:00–15:15 | T13 | **15:15 submitted** |

## Task board
Each task is done when its spec tests pass (`tests/test_spec_*.py` start running automatically once the stub is built), the full test suite passes, and the app runs in mock mode.

| ID | Task | Files | When | Depends on | Done when |
|---|---|---|---|---|---|
| T1 | Number hearing lines and document paragraphs | `fairtrace/ingest.py` | Fri 12:00 | — | `test_spec_ingest.py` passes; Sources tab shows lines |
| T2 | Extract events (one call per hearing) | `fairtrace/extract.py`, `prompts/extract_v1.md` | Fri 13:30 | T1 | `test_spec_extract_flag.py::test_extract*` passes; api run returns valid events |
| T3 | Flag potential issues | `fairtrace/flag.py`, `prompts/flag_v1.md` | Fri 14:30 | T2 | Mock run: 6 flags for H01 (one deliberately bad, which T4 must reject), none for H02 |
| T4 | Verify flags | `fairtrace/verify.py` (`verify_flags`, `banned_words_in`) | Fri 15:00 | T1 | `test_spec_verify.py` passes |
| T5 | Review screen polish | `app.py` | Fri evening | T3, T4 | Decisions land in `audit_log.jsonl`; statuses survive a re-run |
| T6 | Devil's Advocate | `fairtrace/analyzers/devils_advocate.py`, `verify.verify_challenge`, `prompts/devils_advocate_v1.md` | Fri evening | T3 | `test_spec_devils_advocate.py` passes; challenge shows in each card |
| T7 | Copy-Through Detector | `fairtrace/analyzers/copy_through.py` | Fri afternoon (second coder) or Sat 10:00 | T1 | `test_spec_copy_through.py` passes; tab shows matches and coverage |
| T8 | Questions for the monitor (polish, export as a checklist) | `app.py` | Sat | T3 | Questions grouped by hearing; downloadable |
| T9 | Export draft findings | `fairtrace/export.py` | Sat 10:00 | T5 | `test_spec_export.py` passes; download works |
| T10 | Evaluation | `fairtrace/evaluate.py`, `eval/run_eval.py` | Fri evening | T3 | `test_spec_evaluate.py` passes; Evaluation tab shows numbers |
| T11 | Redaction | `fairtrace/redact.py` + calls in extract and flag | Sat (stretch) | T1 | `test_spec_redact.py` passes |
| T12 | Hearings × rights heatmap | `app.py` | Sat (stretch) | T3 | Grid of flag counts by hearing and right |
| T13 | Ship | README, LICENSE, description, fixtures, video | Sat 13:00 | all | Submission checklist below is complete |

Law-team tasks running alongside: review `rights.yaml`; write test notes, the answer key and worked examples; test and refine the prompt files in a chat tool.

## Checkpoint rules
- **Behind at 16:00 Friday?** Merge extract and flag into one model call that works directly on the numbered lines. You lose the event list, but the core flow survives.
- **13:00 Saturday is a hard feature freeze.** After that, only fixes, demo prep and docs.
- **A module isn't solid at the freeze?** Untick it in `config.yaml` → `analyzers.enabled`. The app works without it.

## Cut list
Cut from the top down:
1. Hearings × rights heatmap (T12)
2. Redaction (T11); describe it as a next step instead
3. Export formatting beyond plain Markdown
4. Copy-Through (T7); keep it in the slides as designed but not shown

**Never cut:** source citations for every flag · the verifier · the lawyer's accept/reject step · the accuracy check against the answer key · mock mode.

## If things go wrong
| Problem | Fix |
|---|---|
| The API fails or runs out of credits | Switch the sidebar to `mock` (saved real outputs), or to `local` |
| The organizers' data arrives late | Keep using the synthetic notes; mention real data as the next step |
| The model's flags are poor | Narrow to fewer rights, improve the worked examples, and show the accuracy honestly |
| The venue Wi-Fi drops | Mock or local mode, or play the backup video |
| A teammate is missing | Follow the cut list; the presenter can run the demo in mock mode |

## Submission checklist (by 15:15 Saturday)
Run `python -m eval.check_submission` first: it checks the git history for secrets and runtime data, the synthetic labels and the demo numbers, and lists placeholders still to fill.

- [ ] GitHub repository is public, and its link is submitted
- [ ] `LICENSE` present (MIT proposed; team to confirm) and named in the README. Present and named; replace `[Team Name]` with the copyright holder
- [ ] README: what it does, intended use by TrialWatch, setup (3 commands), modes, data sources with licenses, AI-assistance disclosure, limitations, team. Everything except the team section and the team's confirmation of the AI disclosure
- [ ] Short written description submitted. Draft in [10_submission_description.md](10_submission_description.md)
- [x] No secrets, real case data or `names.yaml` in the repo, including `git log` (checked by `eval.check_submission`; re-run before making the repo public)
- [x] Demo case labeled as synthetic wherever it appears (checked by `eval.check_submission`)
- [ ] Real model outputs saved to `fixtures/mock/` so the demo works offline
- [ ] Backup video recorded
- [ ] Slides include the responsible-AI section and the evaluation numbers
