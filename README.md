# FairTrace (working name)

**From courtroom notes to traceable, lawyer-reviewed fair-trial findings.**

Built for TrialWatch (Human Rights Institute, Columbia Law School) at the FairTrial & AI Hackathon, October 2026. Track 2: Observation to Legal Evaluation.

> **Status: working prototype.** Every pipeline step and both modules are built and run end to end in mock mode on a synthetic demo case. The prompts have not yet been evaluated with a real model; see [Results](#results).
>
> **The tool supports legal analysis. It does not replace the lawyer's judgment.**

## What it does
- **Numbers every line** of monitor notes and every paragraph of court documents, so each claim can be checked.
- **Flags potential fair-trial issues** (for example, the right to examine witnesses), each citing the exact lines it relies on.
- **Verifies every model citation in code** (the line exists, the quote matches it) and shows anything that fails, instead of hiding it.
- **Copy-Through Detector** (switchable module, no AI): finds judgment passages copied word for word from the police report or indictment, focusing on the court's own reasoning.
- **Devil's Advocate** (switchable module): writes the strongest justification the state could give for each issue, then checks whether the record rebuts it.
- **Asks the monitor** for missing facts while the hearing is fresh, as a downloadable checklist grouped by hearing.
- **Lawyer review:** accept, reject or "needs facts", with every decision logged (reviewer, optional note, model and prompt versions).
- **Exports draft findings** with footnotes, using accepted issues only.
- **Shows where issues cluster** in a hearings × rights heatmap.
- **Redacts names** (optional): a `names.yaml` map replaces names with roles before any model call.

## Intended use by TrialWatch
TrialWatch lawyers and experts use FairTrace while preparing a fairness report: it organizes the monitoring record by right, surfaces potential issues with their evidence, and stress-tests each one before it reaches the report. Monitors receive targeted follow-up questions. It runs on a laptop with no servers or database, and for confidential cases it can run entirely offline with a local model.

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add API keys only if you use api mode
pytest                      # 64 tests
streamlit run app.py        # opens the app in mock mode
```
On Windows, activate with `.venv\Scripts\activate` and copy with `copy .env.example .env`.

## Using it
1. In the sidebar: pick the mode and the case, tick the modules, enter your name, press **Run analysis**.
2. **Sources**: every hearing line and document paragraph with its ID (`H01-L012`, `JDG-P003`).
3. **Issues to review**: each potential issue with its cited lines, questions for the lawyer, missing facts and the Devil's Advocate. Accept, reject or mark "needs facts"; each decision goes to `data/<case>/audit_log.jsonl`. Output that failed verification is listed under "Rejected by the verifier".
4. **Copy-Through**: judgment passages that repeat the police report or indictment, with coverage figures.
5. **Questions for the monitor**: grouped by hearing; download as a checklist.
6. **Export**: draft findings in Markdown, accepted issues only.
7. **Evaluation**: scores against the case's answer key.

Command line: `python -m eval.run_eval data/demo_case mock` scores a case without the app.

A new case is a folder under `data/` with a `case.yaml`, one text file per hearing and the court documents; see [data/README.md](data/README.md).

## Model modes
| Mode | What it does | Setup |
|---|---|---|
| `mock` | Uses saved outputs from `fixtures/mock/`; no network | Nothing |
| `api` | Any OpenAI-compatible API (default: Groq) | `GROQ_API_KEY` in `.env`; model ID in `config.yaml` |
| `local` | Ollama on this machine; nothing leaves the laptop | Install Ollama, pull a model, set its tag in `config.yaml` |

Choose the mode in the sidebar or with `FAIRTRACE_MODE` in `.env`. See [docs/06_model_options.md](docs/06_model_options.md).

## Results
On the synthetic demo case **in mock mode**: 6 of 6 expected potential issues caught (one more, which needs judgment analysis the tool doesn't do, is excluded), 0 false alarms on the hearing with no problems, 100% of displayed citations verified, and the planted bad citation rejected.

**What this does and doesn't show.** Mock mode replays the saved outputs in `fixtures/mock/` (prepared for the demo, with two deliberate mistakes) instead of calling a model, so these figures show that the deterministic parts (numbering, verification, Copy-Through, scoring, export) work as designed. They are **not** a measure of model accuracy. That needs a recorded run with a real model (`FAIRTRACE_RECORD=1` in `api` or `local` mode) on notes the tool hasn't seen, scored the same way.

## Limitations
- The tool only sees what monitors wrote down; it cannot judge what isn't in the record.
- No accuracy figures with a real model yet (see Results); the demo case is small and synthetic.
- Translation and non-English documents are not handled well yet. Copy-Through needs words separated by spaces, so languages such as Thai need a word segmenter first.
- The rights list covers 8 fair-trial rights and is a draft for the law team to review; freedom-of-expression analysis (ICCPR Art. 19) is future work.
- Copy-Through shows textual overlap, not whether the overlap was improper.
- Redaction only catches the names listed in `names.yaml`.
- Copy-Through flags are added after the verify step; they use no model and template text, and a test shows they pass it.

## Project structure
```
app.py                  Streamlit app
config.yaml             settings (no secrets)
fairtrace/              the package: ingest, redact, extract, flag, verify, review, export, heatmap, evaluate, llm, analyzers/
prompts/                versioned prompt files (lawyers can edit)
taxonomy/               rights list and worked examples (lawyers own these)
data/demo_case/         synthetic demo case (invented; not a real case)
fixtures/mock/          saved model outputs for mock mode
eval/                   evaluation and pre-submission check scripts
tests/                  spec tests for every task, plus app smoke tests
docs/                   rules, design, plan, decisions, responsible AI, demo script
```

## Responsible AI
Every potential issue cites numbered source lines, and code verifies those citations. The model is used in only three steps. Nothing is exported without a lawyer's decision, every decision is logged, and the tool never proposes verdicts or grades. Confidential cases can run on a local model with names redacted. Full details and limitations: [docs/07_responsible_ai.md](docs/07_responsible_ai.md).

## Data sources
- `data/demo_case/`: **synthetic**, invented for testing. Not a real case, and no real people.
- `taxonomy/rights.yaml`: drafted from public sources: the ICCPR (Art. 9 and 14) and UN Human Rights Committee General Comment No. 32.
- Background reading, not included in the repository: TrialWatch's public fairness reports, such as Thailand: Pan Thalufah (June 2025), listed in [docs/02_track2_brief.md](docs/02_track2_brief.md).
- No other datasets are used. Add any you use, with its licence or terms and attribution.

## AI assistance disclosure
The analysis code (tasks T1–T13 in [docs/04_build_plan.md](docs/04_build_plan.md)) was written with Claude Code (Anthropic's Claude Opus 5.5) during the hackathon, against the spec tests and docstrings in the starter kit, with each task committed separately. Parts of the documentation and the draft prompts were also drafted with AI assistants. The team is responsible for everything submitted. *(Team: confirm, and add what you reviewed and any other tools you used.)*

FairTrace itself calls a language model in three steps (extracting events, flagging potential issues, the Devil's Advocate). The model and prompt version are logged with every review decision.

## Team
*Names and roles.*

## License
MIT. See [LICENSE](LICENSE). *(Team to confirm before submission.)*
