# Responsible AI

Worth **20 of 100 points**, and it also feeds Human Rights Impact (30) and Feasibility (25). Judges will ask about it during Q&A, so everyone on the team should know this page.

## Principles
1. **The tool supports the lawyer; it never replaces them.** It raises *potential* issues and questions. Verdicts and grades stay with the expert.
2. **Every claim is checkable.** Each flag cites numbered source lines, and code checks those citations.
3. **Plain code wherever possible.** The model is used for 3 steps only; verification, matching, scoring and export are deterministic.
4. **Sensitive data stays under TrialWatch's control.** Local mode and redaction exist for real cases. The demo uses only public or synthetic data.
5. **Be honest about limits.** We measure accuracy and show it, including misses and false alarms.

## Risks and how we handle them
| Risk | What could go wrong | What we do | Where in the code |
|---|---|---|---|
| Invented facts or citations | The model claims something the notes don't say | Only code creates source IDs; the verifier checks that every cited ID exists and that the quote matches; failures go to a visible "Rejected by the verifier" panel | `ingest.py`, `verify.py`, `test_spec_verify.py` |
| Over-reliance (automation bias) | Lawyers accept flags without reading the record | "Potential issue" wording; source lines shown next to every flag; nothing exported without an explicit accept; audit log of every decision | `app.py`, `review.py`, `export.py` |
| Missed issues | Silence from the tool is read as "the trial was fair" | The UI says the tool is not a checklist replacement; evaluation reports what was missed; the Gap Finder asks for missing facts | `evaluate.py`, Questions tab |
| Confirmation bias | Findings only argue one side | The Devil's Advocate writes the state's strongest case for every flag and checks it against the record | `analyzers/devils_advocate.py` |
| Confidentiality and data leaks | Sensitive trial data sent to a commercial API, kept by a free tier, or used for training | Demo uses public or synthetic data only; local mode for real data; redaction map; `.env` and `names.yaml` are git-ignored; never put real data on a free tier | `llm.py`, `redact.py`, `.gitignore` |
| Bias across legal systems and languages | The model may reason better about some legal systems than others; translation distorts meaning | Lawyers write the rights list and examples; documents are compared only in their original language; limitations stated in the README | `taxonomy/`, `copy_through.py` |
| Copy-Through false alarms | Legitimate quoting (for example, of the charges) is flagged | Only the court's own reasoning section raises flags; the shared text is shown; the lawyer decides | `copy_through.py` |
| Devil's Advocate misread | A hypothetical state argument is read as a fact | It is labeled "what the state could argue"; a verdict needs a valid citation or is downgraded | `verify.verify_challenge` |
| Grade anchoring | The tool's output nudges the expert's grade | The tool never proposes a grade | Design rule |
| Harm to people in the record | Defendants, witnesses or monitors exposed if data leaks | Redaction, minimal data, synthetic demo data, local files only | `redact.py` |
| Security of stored data | Case files on laptops | Local storage only; no cloud database; encryption at rest is future work | — |

## What we commit to in the code
- [x] No model output is used before Pydantic validation (`llm.py`)
- [x] No model-generated flag reaches the review screen without passing `verify_flags`. Copy-Through flags (no model, template text) are added after the verify step; a test shows they pass it
- [x] No Devil's Advocate verdict without a valid citation (`verify_challenge`)
- [x] No export without an explicit lawyer decision
- [x] Every decision logged with reviewer, model and prompt version
- [x] Temperature 0, versioned prompts
- [x] Mock mode always works

## Limitations to state openly
- The tool only sees what monitors wrote down; it cannot judge what isn't in the record.
- Accuracy was measured on a small, partly synthetic test set; real performance needs testing on real TrialWatch cases.
- Translation quality and non-English documents are not yet handled well.
- The rights list covers 8 rights; freedom-of-expression analysis (Art. 19) is future work.
- Copy-Through shows textual overlap, not whether the overlap was improper.

## AI-assisted development disclosure (for the README)
> Parts of this project, including code, documentation and prompts, were drafted with AI assistants (such as Claude). The team reviewed, tested and is responsible for everything submitted.

## Judge Q&A prep
**"How do you stop it hallucinating?"**
The model never creates source IDs; ingest does. Every flag must cite existing lines and quote one exactly, and code checks this. Failures are shown, not hidden. Three of our steps don't use a model at all.

**"What if it misses a violation?"**
It will sometimes. That is why it supports the expert rather than replacing them, why we report what it missed on our test set, and why it asks the monitor for facts the notes lack.

**"Where does the data go? Could TrialWatch use it with confidential files?"**
For the demo, only public or synthetic data reaches the API. For real cases, TrialWatch switches to local mode: the model runs on their own machine and nothing leaves it. A redaction step also replaces names with roles before any model call.

**"Isn't the Devil's Advocate helping governments?"**
It does the opposite: it anticipates the state's reply before publication, so findings are harder to dismiss. Its arguments are clearly labeled as hypothetical and never appear as findings.

**"How would TrialWatch actually run this?"**
On a laptop: Python plus one command. No servers or database. It can run with a local model for confidential cases. The rights list and prompts are plain files their lawyers can edit.

**"How do you know it works?"**
On our synthetic demo case, in mock mode, it caught 6 of 6 expected issues, with 0 false alarms on the hearing that had no problems, and every displayed citation was verified. The planted bad citation was rejected. Be clear that mock mode replays saved outputs: these numbers show that the checks and scoring work, not how accurate a model is. Real-model accuracy is the next measurement, on notes the tool hasn't seen. (If a recorded `api` or `local` run is scored before the demo, quote that instead, with the model name.)

**"What about bias?"**
Lawyers own the legal categories and examples, outputs are compared only in their original language, the Devil's Advocate counters one-sided analysis, and we publish our limitations.

**"Why not just use ChatGPT?"**
Traceability and control: numbered sources, verified citations, an audit trail, a structured review flow, and the option to run entirely offline.
