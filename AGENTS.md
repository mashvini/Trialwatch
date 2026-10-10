# AGENTS.md: handoff guide for AI coding assistants and developers

## Context
FairTrace is our Track 2 entry for the FairTrial & AI Hackathon (TrialWatch, Columbia Law School, 9–10 October 2026). It helps TrialWatch lawyers turn trial-monitoring notes and court documents into **potential** fair-trial issues. Each issue cites the exact source lines it relies on, can be challenged by a Devil's Advocate module, and reaches the export only after a lawyer approves it.

- Full context: [docs/README.md](docs/README.md)
- Design (read before coding): [docs/03_solution_design.md](docs/03_solution_design.md)
- Tasks and schedule: [docs/04_build_plan.md](docs/04_build_plan.md)
- Responsible AI (judged at 20 points): [docs/07_responsible_ai.md](docs/07_responsible_ai.md)

## Non-negotiable rules
1. **The model never creates source IDs or facts.** IDs come from `fairtrace/ingest.py` only. Every model output that cites IDs goes through `fairtrace/verify.py`.
2. **Validate every model output** with the Pydantic models in `fairtrace/schemas.py`. `llm.py` retries invalid JSON once; after that, fail visibly. Never swallow errors silently.
3. **Wording:** outputs say "potential issue". Never "violation", "violated" or "guilty". The tool never proposes verdicts or grades.
4. **Legal content lives in `taxonomy/*.yaml` and `prompts/*.md`**, never hard-coded in Python. Lawyers edit those files.
5. **Nothing is exported** unless a lawyer set its status to `accepted`.
6. **Mock mode must always work.** It is the demo safety net. After any change, run `pytest` and the app in mock mode.
7. **Never commit** `.env`, real case data, or `names.yaml`. Demo data must be public or synthetic, and labeled.
8. Temperature 0. Log the model name and prompt version with every decision.
9. Keep dependencies minimal (`requirements.txt`). Ask the team before adding heavy ones.
10. **Prefer plain code over the model** for anything deterministic: verification, matching, scoring, export.

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
pytest
streamlit run app.py
```

## Repo map
| Path | Purpose | Status |
|---|---|---|
| `app.py` | Streamlit shell: sidebar, pipeline runner, tabs, review screen (T5), questions for the monitor (T8) | ✅ |
| `config.yaml` | Mode, providers, thresholds, enabled modules, paths | ✅ |
| `fairtrace/config.py` | Loads `config.yaml` and `.env` | ✅ |
| `fairtrace/schemas.py` | Data contracts (change only with team agreement) | ✅ |
| `fairtrace/llm.py` | Model adapter: mock / api / local, JSON parsing, retry, recording | ✅ |
| `fairtrace/prompts.py` | Loads prompt files, fills `{{placeholders}}`, formats numbered lines | ✅ |
| `fairtrace/taxonomy.py` | Loads the rights list and worked examples | ✅ |
| `fairtrace/ingest.py` | `load_case`, `number_hearing`, `split_paragraphs` | ✅ T1 |
| `fairtrace/extract.py` | Notes → events (model); keeps only citations to the hearing's own lines | ✅ T2 |
| `fairtrace/flag.py` | Events → potential issues (model) | ✅ T3 |
| `fairtrace/verify.py` | Citation and wording checks (no model) | ✅ T4, T6 |
| `fairtrace/review.py` | Audit log of decisions, latest decision per flag | ✅ |
| `fairtrace/analyzers/base.py` | Module interface | ✅ |
| `fairtrace/analyzers/__init__.py` | `REGISTRY` and stage ordering | ✅ |
| `fairtrace/analyzers/copy_through.py` | Copy-Through Detector: matching, coverage, `F-CT` flags | ✅ T7 |
| `fairtrace/analyzers/devils_advocate.py` | Devil's Advocate: one call per flag, checked by `verify_challenge` | ✅ T6 |
| `fairtrace/cache.py` | Caches module results so toggling never repeats model calls | ✅ |
| `fairtrace/heatmap.py` | Hearings × rights grid of potential issues, shown on the Overview tab | ✅ T12 |
| `fairtrace/export.py` | Draft findings in Markdown (T9); questions for the monitor and their checklist (T8) | ✅ T9 |
| `fairtrace/evaluate.py` | Answer-key loading and scoring | ✅ T10 |
| `fairtrace/redact.py` | `load_names`, `redact`, `restore`, `redact_lines` (applied right after ingest) | ✅ T11 |
| `prompts/` | `extract_v1.md`, `flag_v1.md`, `devils_advocate_v1.md` (drafts) | Law team reviews |
| `taxonomy/` | `rights.yaml` (8 rights, draft), `worked_examples.yaml` (draft) | Law team reviews |
| `data/demo_case/` | Synthetic case: 2 hearings, 3 documents, answer key | ✅ |
| `data/philippines_cumpio/` | Real case reconstructed from a public TrialWatch article (`provenance` in `case.yaml`): 4 thematic sessions, no documents, answer key; fixtures in `fixtures/mock/cumpio_reconstructed/` | ✅ |
| `fixtures/mock/` | Saved outputs for mock mode (see `fixtures/README.md`) | ✅ |
| `tests/` | `test_skeleton.py`, `test_app_smoke.py`, `test_monitor_questions.py`, `test_redaction_wiring.py`, `test_heatmap.py`; `test_spec_*.py` define each task | ✅ |

## How stubs and spec tests work
- Each stub raises `NotImplementedError("T<n>: ...")`. The app catches it and shows "Not built yet", so the app always runs.
- `tests/test_spec_*.py` describe the expected behavior of each task. They **skip automatically** while the stub raises `NotImplementedError` and **start running as soon as it's built**.
- A task is done when its spec tests pass, the whole suite passes, and the app works in mock mode.
- Before handoff, the spec tests and fixtures were checked against throwaway reference implementations (not included), so every spec is achievable as written.

**What a finished build shows in mock mode** (demo case, all modules ticked):
- Pipeline status: every step ✅
- 6 potential issues: 5 from the notes plus `F-CT-1` from Copy-Through
- 1 rejected by the verifier: `F-H01-6`
- 6 Devil's Advocate challenges; the one for `F-H01-4` shows "(Verdict downgraded: no valid citation.)"
- Copy-Through coverage: roughly 50–60% overall and within the reasoning section
- Evaluation: 6 of 6 expected issues caught, 0 false alarms, 100% citations verified

## Task list (details in docs/04_build_plan.md)
| ID | Task | Main file | Spec tests |
|---|---|---|---|
| T1 | Number hearing lines and document paragraphs | `ingest.py` | `test_spec_ingest.py` |
| T2 | Extract events, one call per hearing | `extract.py` | `test_spec_extract_flag.py` |
| T3 | Flag potential issues, one call per hearing | `flag.py` | `test_spec_extract_flag.py` |
| T4 | Verify flags | `verify.py` | `test_spec_verify.py` |
| T5 | Review screen polish | `app.py` | manual |
| T6 | Devil's Advocate + `verify_challenge` | `analyzers/devils_advocate.py`, `verify.py` | `test_spec_devils_advocate.py`, `test_spec_verify.py` |
| T7 | Copy-Through Detector | `analyzers/copy_through.py` | `test_spec_copy_through.py` |
| T8 | Questions for the monitor (polish, download) | `app.py` | manual |
| T9 | Export | `export.py` | `test_spec_export.py` |
| T10 | Evaluation | `evaluate.py` | `test_spec_evaluate.py` |
| T11 | Redaction | `redact.py` | `test_spec_redact.py` |
| T12 | Hearings × rights heatmap (stretch) | `app.py` | manual |
| T13 | Ship: README, license, fixtures, video | — | checklist in the build plan |

Each stub's docstring contains its exact spec. Read it before writing code.

## Mock fixtures
- Lookup order: `fixtures/mock/<case_id>/<prompt>.<key>.json`, `fixtures/mock/<case_id>/<prompt>.json`, then the same two names directly under `fixtures/mock/` (the shared folder the demo case uses). A new case gets its own folder, so its `H01` never replays another case's outputs.
- Keys: the hearing ID for `extract` and `flag` (for example `flag.H01.json`); the flag ID for `devils_advocate`. The shared `devils_advocate.json` holds challenges for all flags, so filter by `flag_id`.
- The fixtures contain **two deliberate mistakes** to demonstrate the guardrails: flag `F-H01-6` quotes text that isn't in its cited line (T4 must reject it), and the challenge for `F-H01-4` cites a line that doesn't exist (T6 must downgrade it).
- To record real outputs: set `FAIRTRACE_RECORD=1`; files land in `fixtures/recorded/<case_id>/`. Copy good ones into `fixtures/mock/<case_id>/` (the demo case's live directly in `fixtures/mock/`).

## Conventions
- Python 3.11+, type hints, short functions with docstrings that say what and why.
- One hearing per model call; one flag per Devil's Advocate call.
- IDs: lines `H01-L012`, paragraphs `JDG-P003`, events `E-H01-1`, flags `F-H01-1`, Copy-Through flags `F-CT-1`.
- Small commits whose message names the task, for example `T3: flag prompt and parser`.
- Keep the README and docs in step with behavior changes.
