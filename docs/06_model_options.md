# Model options

Checked on 7 October 2026. Free tiers change often, and most providers now show exact limits only inside your account dashboard, so check there before relying on any number below.

## What we chose
| Use | Choice | Why |
|---|---|---|
| Live demo | **Groq** (`api` mode) | Fast; the free daily limit comfortably covers a hackathon; serves open-weight models |
| Confidential data / offline | **Ollama** (`local` mode) | Nothing leaves the laptop. If you run an open-weight model locally, it can be the same family the demo uses |
| Safety net | **Mock mode** | Saved outputs; no network needed |
| Backup API | Gemini free tier, **public data only** | Free-tier content may be used to improve Google's products |

**The pitch to judges:** "Our demo runs an open-weight model through Groq. TrialWatch could run the same kind of model on its own machine, so confidential trial data never leaves its control. Switching is a config setting."

## Free cloud APIs
| Provider | What's free | Limits | Watch out for |
|---|---|---|---|
| **Groq** | Open-weight models such as gpt-oss-120b and Qwen models | Sample limits for text models: 30 requests/min, 1,000 requests/day, 8,000 tokens/min, 200,000 tokens/day | Limits apply **per organization, not per user**, so sharing one key doesn't add capacity. Each teammate should create their own account |
| **Google Gemini** (AI Studio) | Flash and Flash-Lite models, embeddings and Gemma. Pro models are paid-only | Google stopped publishing free-tier limits in December 2025; they're shown per project in AI Studio and are lower than before | **Free-tier content is used to improve Google's products**, and outside the EU, UK and Switzerland human reviewers may read prompts and responses. Apps serving users in the EU, UK or Switzerland must use the paid tier |
| **OpenRouter** | Models whose name ends in `:free` | 20 requests/min and **50 requests/day** until you've bought $10 of credits in total | Fine for testing, too tight for demo day |
| Mistral, Cohere | Free tiers exist | Shown only in your dashboard | Check the data terms first |
| GitHub Models | Free, rate-limited access for prototyping | Varies by model | Not verified; check before relying on it |

**One full demo run is about 20 model calls** (2 per hearing plus 1 per flag), far below these daily limits.

## Columbia's own AI tools
- **AI Toolkit** (formerly CHAT): Columbia's secure AI platform with a choice of models. It is approved for PII and RHI data under the University's data classification policy. Every user gets a free daily allocation of $0.15: enough to test prompts, not to run the tool.
- **ChatGPT Edu, Gemini and NotebookLM:** chat tools in a "walled garden" where user data isn't used to train vendor models. Good for prompt testing; they're chat interfaces, not APIs our code can call.
- **API access is gated:** for example, the Business School lists an OpenAI API key as an approved tool, and other AI tools need pre-approval. That won't come through by Friday.

## Local models on a Mac M4
Check your memory under Apple menu → About This Mac. The model must fit in the shared memory alongside macOS and your other apps. Sizes are for the standard compressed (4-bit) versions.

| Mac memory | Best fit | Approx. size in memory | Notes |
|---|---|---|---|
| **16 GB** | **Gemma 4 12B** | ~7 GB | The sweet spot: good quality with room left for your editor and browser |
| 16 GB, lighter option | Gemma 4 E4B | ~6 GB | Faster, but weaker at legal reasoning |
| **24 GB** | **Gemma 4 26B A4B** | ~16 GB | A large model that is fast because it uses only about 4B parameters per token |
| 24–32 GB | gpt-oss-20b | ~13–14 GB | The smaller sibling of the model on Groq |
| 32 GB+ | Gemma 4 31B | ~19 GB | Highest quality of these; slower |

**Warning for 16 GB Macs:** gpt-oss-20b runs only at reduced quality. It needs heavy compression that still takes about 13 GB, more than the roughly 11.5 GB actually usable. Expect it to be slow, with a safe context limit of only about 4K tokens. Skip it unless you have 24 GB or more.

**Long documents cost memory.** The longer the text you send, the more memory the model needs. That is why the pipeline sends one hearing at a time.

## Setup
**Groq (api mode)**
1. Create an account and an API key in the Groq console.
2. Put `GROQ_API_KEY=...` in `.env` (copy from `.env.example`).
3. In `config.yaml`, set `providers.api.model` to a model ID from the console's model list.
4. Select `api` in the sidebar, or set `FAIRTRACE_MODE=api`.

**Ollama (local mode)**
1. Install the Mac app from ollama.com.
2. Run `ollama pull <model tag>`, choosing a tag from ollama.com/library that fits your memory.
3. In `config.yaml`, set `providers.local.model` to that tag.
4. Select `local` in the sidebar. Ollama serves an OpenAI-compatible API at `http://localhost:11434/v1`, so no code changes are needed.

**Saving real outputs for the demo:** run once with `FAIRTRACE_RECORD=1`. Outputs land in `fixtures/recorded/`; copy the good ones into `fixtures/mock/`.

## Sources
- [BenchLM: Free LLM API tiers](https://benchlm.ai/md/free-tier.md)
- [BenchLM: Groq free tier](https://benchlm.ai/md/free-tier/groq.md)
- [AgentDeals: Gemini API pricing changes](https://agentdeals.dev/gemini-api-pricing-changes)
- [Novita: Free LLM API comparison 2026](https://blogs.novita.ai/free-llm-api-comparison-2026/)
- [Jacar: Gemma 4 locally, which size fits](https://jacar.es/en/gemma-4-locally-with-ollama/)
- [WillItRunAI: GPT-OSS 20B on M4 16GB](https://willitrunai.com/de/can-run/gpt-oss-20b-on-m4-16gb)
- [Columbia CUIT: AI Toolkit](https://www.cuit.columbia.edu/aitoolkit)
- [Columbia: AI Resources](https://ai.columbia.edu/content/AI-Resources)
- [Columbia Business School: AI in Research](https://business.columbia.edu/research-resources/ai-in-research)
