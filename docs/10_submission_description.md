# Written description (draft for the submission form)

The rules ask for "a short written description of the tool and its intended use by TrialWatch". This is a draft of about 400 words. Team: edit freely, add the repository link and team name, and keep the evaluation sentence honest (it describes mock mode until a real-model run is recorded).

---

**FairTrace: from courtroom notes to traceable, lawyer-reviewed fair-trial findings**

*Track 2: Observation to Legal Evaluation*

TrialWatch lawyers know what happened in court but still have to work out what it means legally, across many pages of monitoring notes and court documents. FairTrace helps with that step. It turns monitor notes and court documents into **potential** fair-trial issues, organized by right under the ICCPR (Art. 14), for a lawyer to review. It never proposes verdicts or grades.

**How it works.** Code numbers every line of the notes and every paragraph of the documents. A language model is used in only three steps: it extracts courtroom events, maps them to potential issues, and argues the state's side. Every potential issue must cite numbered lines and quote one of them, and plain code checks this before a lawyer sees it. Anything that fails is shown, not hidden. Each issue comes with questions for the lawyer and the facts the notes leave out.

**Two modules that change the review.** The *Copy-Through Detector*, which uses no AI, finds passages where the judgment's own reasoning repeats the police report or indictment word for word. That is a lead for the reasoned-judgment and independence analysis. The *Devil's Advocate* writes the strongest justification the state could give for each issue and checks whether the record rebuts it. That anticipates the government replies that findings often receive, and counters confirmation bias.

**Intended use by TrialWatch.** A lawyer runs FairTrace on a laptop while preparing a fairness report. They review each potential issue: accept, reject, or ask the monitor for facts. Every decision is logged with the reviewer, model and prompt version. Monitors receive a checklist of follow-up questions grouped by hearing. The lawyer exports draft findings with footnoted sources, containing only accepted issues. The rights list and prompts are plain files the legal team edits. For confidential cases, FairTrace runs fully offline with a local model, and names can be replaced with roles before any model call.

**Status and evaluation.** It is a working prototype, demonstrated on a synthetic case. In mock mode, which replays saved outputs, it reproduces 6 of 6 expected issues with no false alarms, and every displayed citation is verified. Accuracy with a real model has not yet been measured. Measuring it on real TrialWatch notes is the next step, with the same scoring.

Open source (MIT). Repository: *[link]*. Team: *[name]*.
