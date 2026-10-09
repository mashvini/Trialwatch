# Solution design: FairTrace (working name)

## In one sentence
A review tool for TrialWatch lawyers. It turns monitor notes and court documents into *potential* fair-trial issues, ties each one to the exact lines it comes from, tests it against the state's strongest counter-argument, and exports draft findings only after a lawyer approves them.

## Who uses it
- **TrialWatch lawyers and experts** who write fairness reports (main users).
- **Trial monitors**, who receive follow-up questions about facts their notes left out.

## Design principles
1. **Support the lawyer, never replace them.** No verdicts and no grades. The tool says "potential issue", never "violation".
2. **Every claim is traceable** to a numbered source line that a person can open and check.
3. **Plain code wherever possible.** The model is used for only three steps: extracting events, flagging issues, and the Devil's Advocate. Verification, matching, scoring and export are ordinary code.
4. **Works without the internet.** Mock mode for safe demos; local mode for confidential data.
5. **Lawyers own the legal content.** Rights, red flags, questions and examples live in YAML and prompt files they can edit, never in Python.

## Pipeline
```
Monitor notes / court documents
        │
 [1] Ingest ─────────── number every line (H03-L047) and paragraph (JDG-P034)
 [2] Redact ─────────── optional: real names → roles, before any model call
 [3] Extract events ─── who did what, at which hearing, citing line IDs           (model)
 [4] Flag issues ────── map events to the rights list                             (model)
        └── missing facts → questions for the monitor (Gap Finder)
 [5] Verify ─────────── do cited lines exist? does the quote match? banned words?
        │
        ├── [Copy-Through Detector] ── judgment vs police report / indictment     (no model) ── adds flags
        ▼
 [Devil's Advocate] ─── the state's best justification + does the record rebut it? (model)
 [7] Lawyer review ──── accept / reject / needs facts, every decision logged
 [8] Export ─────────── draft findings with footnotes, accepted issues only

 [ ] = switchable module (sidebar checkbox)
```

## Components and status in the starter kit
| Step | File | Uses the model? | Starter status | Task |
|---|---|---|---|---|
| Case loading | `fairtrace/ingest.py` → `load_case` | No | ✅ works | — |
| Line numbering | `fairtrace/ingest.py` → `number_hearing`, `split_paragraphs` | No | 🛠️ stub | T1 |
| Extract events | `fairtrace/extract.py` | Yes | 🛠️ stub | T2 |
| Flag potential issues | `fairtrace/flag.py` | Yes | 🛠️ stub | T3 |
| Verify | `fairtrace/verify.py` | No | 🛠️ stub | T4 |
| Review screen + audit log | `app.py`, `fairtrace/review.py` | No | ✅ log and buttons work; polish in T5 | T5 |
| Devil's Advocate | `fairtrace/analyzers/devils_advocate.py` | Yes | ✅ module wiring; 🛠️ `run` | T6 |
| Copy-Through Detector | `fairtrace/analyzers/copy_through.py` | No | ✅ module wiring; 🛠️ matching | T7 |
| Questions for the monitor | `app.py` tab | No | ✅ basic list; polish in T8 | T8 |
| Export | `fairtrace/export.py` | No | 🛠️ stub | T9 |
| Evaluation | `fairtrace/evaluate.py`, `eval/run_eval.py` | No | ✅ answer-key loading; 🛠️ scoring | T10 |
| Redaction | `fairtrace/redact.py` | No | 🛠️ stub | T11 |
| LLM adapter (mock / api / local) | `fairtrace/llm.py` | — | ✅ works | — |
| Module registry and cache | `fairtrace/analyzers/`, `fairtrace/cache.py` | — | ✅ works | — |

## Source IDs: the basis of every citation
- **Hearing notes:** `H03-L047` = hearing H03, line 47 of the notes file, counted physically, so anyone can open the file and find line 47. Blank lines and lines starting with `#` are skipped but still counted.
- **Documents:** `JDG-P034` = paragraph 34 of the judgment. Paragraphs are separated by blank lines; `#` lines are ignored. Prefixes come from `case.yaml`, for example `IND` (indictment), `POL` (police report), `JDG` (judgment), `BAIL` (bail decision).
- **Only code creates IDs.** The model may cite IDs but never invent them; `verify.py` rejects any citation that doesn't exist.
- Other IDs: events `E-H01-1`, flags `F-H01-1`, Copy-Through flags `F-CT-1`.

## Data contracts
Defined in `fairtrace/schemas.py`. Change them only with the whole team's agreement.

| Model | Purpose | Key fields |
|---|---|---|
| `Case`, `HearingRef`, `DocumentRef` | Case definition from `case.yaml` | hearings, documents, `reasoning_paragraphs` for judgments |
| `SourceLine` | One numbered line or paragraph | `id`, `doc`, `text` |
| `Event` | A factual courtroom event | `actor`, `action`, `source_ids` |
| `Flag` | A potential issue | `right_id`, `source_ids`, `quote`, `explanation`, `questions_for_lawyer`, `missing_facts`, `status`, `origin` |
| `Challenge` | Devil's Advocate result | `state_argument`, `verdict` (rebutted / not_addressed / supported), `source_ids` |
| `CopyMatch`, `CopyReport` | Copy-Through results | `judgment_id`, `source_id`, `shared_words`, `in_reasoning`, coverage figures |
| `Decision` | One audit-log entry | `flag_id`, `decision`, `reviewer`, `model`, `prompt_version`, `timestamp` |
| `CaseRecord` | Everything known about a case in a session | lines, events, flags, challenges, copy report |

## Case folder format
```
data/<case_id>/
├── case.yaml                 # metadata, hearing list, document list
├── hearings/hearing_01.txt   # one plain-text file per hearing
├── documents/*.txt           # indictment, police report, judgment (plain text, same language)
├── answer_key.yaml           # expected issues, for evaluation
├── names.yaml                # optional redaction map (git-ignored)
├── .cache/                   # module results (created at runtime, git-ignored)
└── audit_log.jsonl           # review decisions (created at runtime, git-ignored)
```

## Switchable modules (analyzers)
Both signature features are **modules** behind one interface (`fairtrace/analyzers/base.py`):

| Attribute / method | Meaning |
|---|---|
| `id`, `label`, `description` | Names shown in the sidebar |
| `stage` | 1 = produces flags (Copy-Through); 2 = challenges flags (Devil's Advocate). Modules run in stage order |
| `uses_model` | Whether the module calls the LLM |
| `available(record)` | Returns `(ok, reason)`. The app shows the reason when a module can't run, for example "Needs a judgment" |
| `run(record, settings, llm)` | Does the work and returns a result model |
| `apply(record, result, settings)` | Merges the result into the record (adds flags or challenges) |
| `cache_inputs`, `params` | What the cache key is built from, so toggling a module never repeats model calls |

- **Registry:** `fairtrace/analyzers/__init__.py` → `REGISTRY`. Defaults come from `config.yaml` → `analyzers.enabled`; the sidebar checkboxes override them per session.
- **Checkboxes, not either/or.** The modules look at different evidence and work together. For a strict switch, change `st.checkbox` to `st.radio` in `app.py`.
- **Safe to cut:** if a module isn't ready by the feature freeze, untick it and the app still works.
- **Adding a module:** subclass `Analyzer`, add it to `REGISTRY`, and add a renderer in `app.py`.

## Copy-Through Detector (no model)
**Question it answers:** did the court's reasoning come from the police report or indictment, word for word? This is a signal for the reasoned-judgment and independence findings in reports like Pan Thalufah.

**Algorithm** (thresholds in `config.yaml` → `copy_through`):
1. Take the judgment's paragraphs and the paragraphs of every indictment and police report.
2. Normalize each paragraph: lowercase, punctuation → spaces, split into words.
3. For each judgment paragraph, pre-select the 3 most similar source paragraphs with `rapidfuzz.process.extract` (`fuzz.token_set_ratio`).
4. Find shared runs with `difflib.SequenceMatcher(None, source_words, judgment_words, autojunk=False).get_matching_blocks()`. Keep runs of at least **8 consecutive words** (`min_shared_words`).
5. Emit one `CopyMatch` per (judgment paragraph, source paragraph) pair, with the longest run's words as `shared_text`, the paragraph similarity, and `in_reasoning` (whether the paragraph is inside the judgment's `reasoning_paragraphs` from `case.yaml`).
6. **Coverage:** the share of judgment words inside any kept run, overall and within the reasoning section.
7. **Flags:** only matches *inside the reasoning section* with at least **25 shared words** (`flag_min_shared_words`) become flags (`F-CT-1`, …), mapped to `copy_through.right_id` (default `reasoned_judgment`). The explanation is a fixed template, so nothing can be invented.

**Why section-aware?** Quoting the charges in the case summary is normal. Copying the police's conclusions into the court's own reasoning is the warning sign.

**Language:** compare only documents in the same language, never a translation against an original. Word matching needs spaces between words, which Thai doesn't use; for Thai, use a word segmenter such as PyThaiNLP or compare character sequences.

**What it can't tell you:** whether the copying was improper. It is a lead for the lawyer, not a finding.

## Devil's Advocate (model)
**Question it answers:** what is the strongest justification the state could give for this, and does our record answer it?
1. For each flag that isn't rejected, one model call with the flag, the right's entry and the relevant numbered lines (prompt: `prompts/devils_advocate_v1.md`).
2. The model writes `state_argument` (allowed to be hypothetical) and a `verdict`:
   - `rebutted`: a cited line contradicts the justification
   - `supported`: a cited line backs it (the lawyer should weigh this)
   - `not_addressed`: the record is silent, which becomes a fact to gather
3. **Guardrail** (`verify.verify_challenge`): unknown line IDs are dropped. If a `rebutted` or `supported` verdict has no valid citation left, it is downgraded to `not_addressed` and the downgrade is noted.
4. The challenge is shown inside the flag's card and carried into the export.

**Why:** UN complaints routinely receive government replies, so findings get pushback. This tests every finding against that pushback before publication, and actively counters confirmation bias.

## Gap Finder (questions for the monitor)
Every flag carries `missing_facts`, and every `not_addressed` challenge points to one too. The "Questions for the monitor" tab groups them by hearing so the monitor can answer while the hearing is fresh. It asks rather than asserts, so the risk of invented facts is close to zero.

## Verify rules (`fairtrace/verify.py`, no model)
**Hard failures → rejected** (shown in a separate "Rejected by the verifier" panel, never silently dropped):
- `right_id` not in `taxonomy/rights.yaml`
- no `source_ids`, or any ID that doesn't exist in the record
- the `quote` doesn't match a cited line: `rapidfuzz.fuzz.partial_ratio(quote, line, processor=rapidfuzz.utils.default_process) < verify.quote_match_threshold` (default 90)

**Soft warnings → kept, with a note:**
- the explanation contains a banned word (`verify.banned_words`, for example "violation" or "guilty")

## Lawyer review and audit log
- Statuses: `pending` → `accepted` / `rejected` / `needs_facts`.
- Each click appends a `Decision` to `data/<case>/audit_log.jsonl` with the reviewer's name, model and prompt version. The latest decision per flag wins.
- A reviewer name is required before any decision.

## Export (`fairtrace/export.py`)
Markdown draft findings:
- a header that says it is an AI-assisted draft reviewed by the named reviewer, with potential issues only;
- one section per right, in `rights.yaml` order, containing **accepted flags only**;
- for each flag: the explanation, plus the Devil's Advocate argument and verdict if one exists;
- footnotes quoting every cited line;
- a final section listing open questions for the monitor.

Word export via `python-docx` is a stretch goal.

## Redaction (`fairtrace/redact.py`)
`data/<case>/names.yaml` maps real names to roles (`"Maria Santos": DEFENDANT`). Text is redacted before any model call; names are restored only in the export, and only if the lawyer chooses. Matching is whole-word, case-insensitive, longest name first. **Limitation:** it only catches names you list.

## Model modes (`fairtrace/llm.py`)
| Mode | What it does | When |
|---|---|---|
| `mock` | Returns saved JSON from `fixtures/mock/` | Building the UI, tests, demo safety net |
| `api` | Any OpenAI-compatible API (default: Groq) | Live demo on public or synthetic data |
| `local` | Ollama on the laptop (`http://localhost:11434/v1`) | Confidential data; offline |

- Mock lookup: `fixtures/mock/<prompt>.<key>.json`, then `<prompt>.json`. The key is the hearing ID for extract and flag, and the flag ID for the Devil's Advocate.
- `FAIRTRACE_RECORD=1` saves real outputs to `fixtures/recorded/`; copy good ones into `fixtures/mock/` for the demo.
- Temperature 0, JSON output, one retry on invalid JSON, then a visible error. One hearing per call keeps context small enough for local models.

## Evaluation (`fairtrace/evaluate.py`)
- **Test case:** notes written as *observations, not conclusions*, plus at least one hearing with no problems.
- **Answer key** (`answer_key.yaml`): expected issues with `right_id` and `source_ids`; `clean_hearings` lists hearings where any flag counts as a false alarm.
- **Matching rule:** an expected issue is caught if any flag has the same `right_id` and shares at least one source ID.
- **Metrics shown in the app:** issues caught (recall over items the MVP can detect), false alarms on clean hearings, total flags, and the citation verification rate.

## User interface
- **Sidebar:** model mode, case, module checkboxes, reviewer name, Run analysis.
- **Tabs:** Overview (pipeline status) · Sources (numbered lines) · Issues to review (cards with sources, questions, Devil's Advocate, accept/reject) · Copy-Through · Questions for the monitor · Export · Evaluation · About.
- Stubs show "Not built yet: T<n>" instead of crashing, so the app runs from day one.

## Out of scope for the hackathon (future work)
From our brainstorm, roughly in order of value:
- **Evidence Engagement Map:** did the judgment address each piece of defense evidence?
- **Elements-of-Offence Checker:** does the judgment reason about each element, such as intent?
- **Speech Restriction Test Builder:** the ICCPR Art. 19(3) three-part test, plus the Rabat Plan's six factors for incitement-type charges.
- **Statute Red-Flag Library:** what UN bodies and courts have said about the specific law charged.
- **Legal Test Walkthrough:** each right as its legal test, step by step.
- **Contradiction Finder:** monitor notes vs court minutes vs media reports.
- **Translation-Risk Highlighter.**
- **Detention & Delay Clock.**
- **Case Benchmarking** against the Pressing Charges dataset (license to be checked).
- **Hearings × rights heatmap** (a stretch goal in T12).
