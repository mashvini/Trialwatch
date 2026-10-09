# Decisions and open questions

## Decided (7 October 2026)
| Decision | Detail |
|---|---|
| Track | **Track 2: Observation to Legal Evaluation** |
| Concept | Core pipeline (notes → potential issues with source lines → lawyer review → export) plus two **switchable modules**: the Copy-Through Detector and the Devil's Advocate. Gap Finder questions come from the same flag step |
| Stack | Python, Streamlit, `openai` client against any OpenAI-compatible endpoint, Pydantic, `rapidfuzz`, JSON files for storage |
| Model approach (default) | Groq for the live demo, Ollama for local/confidential mode, mock mode as the safety net |
| AI coding assistants | Allowed in our reading of the rules; disclosed in the README |

## Pending decisions
| Decision | Options | Default | Decide by | Final decision | Owner |
|---|---|---|---|---|---|
| Model choice | Groq model / Gemini backup / local model | Groq + Ollama + mock | Thu 9 PM | | |
| Data source | Organizer data / synthetic from Pan Thalufah / both | Synthetic | Thu 9 PM | | |
| Pre-building code | Allowed / not allowed | Skeleton only | Organizers' reply | | |
| Rights list | Draft in `taxonomy/rights.yaml` | Law teammate reviews | Thu night | | |
| Team roles | — | Coder / law / presenter | Thu 9 PM | | |
| Who builds Copy-Through | Second coder Friday / coder Saturday | Second coder | Thu 9 PM | | |
| License | MIT / Apache-2.0 | MIT | Fri | | |
| Project name | FairTrace (working) / other | FairTrace | Fri | | |

## Questions sent to the organizers
Send to **mad2345@columbia.edu**, CC **mjl2241@columbia.edu**.

> **Subject:** FairTrial & AI Hackathon – Track 2 team questions
>
> Hi Marian,
>
> I'm [Your Name], Team Lead for [Team Name]. We're registering for Track 2 (Observation to Legal Evaluation) and have a few quick questions before the build days:
>
> 1. Preparation before Oct 9: may we set up a repository skeleton, data schema and test prompts in advance, or should all code be written during the event itself?
> 2. AI coding assistants: we plan to use AI tools (e.g., Claude, Copilot) to help write code, and will disclose this in our README. Is that acceptable?
> 3. Model access: will teams receive any API credits or compute for running AI models, or should we arrange our own?
> 4. Sample monitoring data: Track 2 starts from trial monitors' notes. Are there anonymized or sample monitor notes we could work with, or should we build from public materials such as the published fairness reports?
> 5. India Defamation Dataset: we'd be interested in using it if access can be arranged in time. I've copied the dataset contact (mjl2241@columbia.edu). Please let us know what the NDA process involves.
>
> Thank you for organizing this, and we look forward to Friday.
>
> Best regards,
> [Your Name]
> [Team Name] – Track 2
> [UNI / Phone]

| Question | Sent | Answer |
|---|---|---|
| 1. Pre-building | [ ] | |
| 2. AI coding assistants | [ ] | |
| 3. API credits | [ ] | |
| 4. Sample notes | [ ] | |
| 5. India dataset / NDA | [ ] | |

## Technical issues for team discussion
The coder's checklist for the team meeting:
1. **Model and money:** API or local or both; who pays and the cap; which model; keys in `.env`, never in GitHub; whose laptop can run a local model.
2. **Data (the biggest risk):** who writes the test notes and by when; who writes the answer key; plain text or PDF; English only or translated material; public or synthetic data only, attributed in the README.
3. **Legal framework:** law teammates own the rights list. Without it the model invents its own categories.
4. **Scope:** the must-have demo flow; what counts as a stretch goal; feature freeze at 13:00 Saturday.
5. **Stack:** Streamlit, JSON storage; the demo runs locally in case the Wi-Fi fails; repo owner, license and branch workflow.
6. **Responsible AI built in:** source citations required; "potential issue" wording; the audit log; optional redaction.
7. **Demo safety:** saved results, a backup video, and who presents and who answers ethics questions.
8. **Division of labor:** non-coders own the test notes, answer key, rights list, prompt testing, slides and written description.

**The one thing to leave the meeting with:** test notes and the rights list by Thursday night.

## Decision log
| Date | Decision | Why | Who |
|---|---|---|---|
| 7 Oct | Track 2 | Matches our skills; clear deliverable | Team |
| 7 Oct | Both signature features as switchable modules | Copy-Through matches the organizers' own example; Devil's Advocate is novel and serves the ethics criterion; the module design makes either one safe to cut | Coder |
| | | | |
