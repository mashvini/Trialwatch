# FairTrace (working name)

**From courtroom notes to traceable, lawyer-reviewed fair-trial findings.**

Built for TrialWatch (Human Rights Institute, Columbia Law School) at the FairTrial & AI Hackathon, October 2026. Track 2: Observation to Legal Evaluation.

> **Status: starter skeleton.** The plumbing works (configuration, model adapter, module system, audit log, app shell). The analysis steps are documented stubs to be built during the hackathon; see [AGENTS.md](AGENTS.md) and [docs/04_build_plan.md](docs/04_build_plan.md).
>
> **The tool supports legal analysis. It does not replace the lawyer's judgment.**

## What it does
- **Numbers every line** of monitor notes and every paragraph of court documents, so each claim can be checked.
- **Flags potential fair-trial issues** (for example, the right to examine witnesses), each citing the exact lines it relies on.
- **Verifies every citation in code** and shows anything that fails, instead of hiding it.
- **Copy-Through Detector** (switchable module, no AI): finds judgment passages copied word for word from the police report or indictment, focusing on the court's own reasoning.
- **Devil's Advocate** (switchable module): writes the strongest justification the state could give for each issue, then checks whether the record rebuts it.
- **Asks the monitor** for missing facts while the hearing is fresh.
- **Lawyer review:** accept, reject or "needs facts", with every decision logged.
- **Exports draft findings** with footnotes, using accepted issues only.

## Intended use by TrialWatch
TrialWatch lawyers and experts use FairTrace while preparing a fairness report: it organizes the monitoring record by right, surfaces potential issues with their evidence, and stress-tests each one before it reaches the report. Monitors receive targeted follow-up questions. It runs on a laptop with no servers or database, and for confidential cases it can run entirely offline with a local model.

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add API keys only if you use api mode
pytest                      # skeleton tests pass; spec tests skip until each task is built
streamlit run app.py        # opens the app in mock mode
```

## Model modes
| Mode | What it does | Setup |
|---|---|---|
| `mock` | Uses saved outputs from `fixtures/mock/`; no network | Nothing |
| `api` | Any OpenAI-compatible API (default: Groq) | `GROQ_API_KEY` in `.env`; model ID in `config.yaml` |
| `local` | Ollama on this machine; nothing leaves the laptop | Install Ollama, pull a model, set its tag in `config.yaml` |

Choose the mode in the sidebar or with `FAIRTRACE_MODE` in `.env`. See [docs/06_model_options.md](docs/06_model_options.md).

## Project structure
```
app.py                  Streamlit app
config.yaml             settings (no secrets)
fairtrace/              the package: ingest, extract, flag, verify, review, export, evaluate, llm, analyzers/
prompts/                versioned prompt files (lawyers can edit)
taxonomy/               rights list and worked examples (lawyers own these)
data/demo_case/         synthetic demo case (invented; not a real case)
fixtures/mock/          saved model outputs for mock mode
eval/                   evaluation script
tests/                  skeleton tests and spec tests
docs/                   rules, design, plan, decisions, responsible AI, demo script
```

## Responsible AI
Every potential issue cites numbered source lines, and code verifies those citations. The model is used in only three steps. Nothing is exported without a lawyer's decision, every decision is logged, and the tool never proposes verdicts or grades. Confidential cases can run on a local model with names redacted. Full details and limitations: [docs/07_responsible_ai.md](docs/07_responsible_ai.md).

## Data sources
- `data/demo_case/`: **synthetic**, invented for testing. Not a real case.
- *Add every dataset you use, with its license or terms and attribution.*

## AI assistance disclosure
Parts of this project, including code, documentation and prompts, were drafted with AI assistants (such as Claude). The team reviewed, tested and is responsible for everything submitted. *(Team: edit to match what you actually used.)*

## Team
*Names and roles.*

## License
MIT. See [LICENSE](LICENSE). *(Team to confirm before submission.)*
