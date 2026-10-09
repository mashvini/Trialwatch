# Track 2 brief: Observation to Legal Evaluation

## The problem in one paragraph
Track 2 covers the step after a trial has been monitored: turning observations into a legal analysis of one case. The organizers call this step a bottleneck. TrialWatch lawyers review large volumes of monitoring notes and court documents to identify possible violations of international human rights law and to spot patterns. The question is how technology can help surface potential violations, organize information in legally meaningful ways, and support consistent application of international fair-trial standards. The rules give one example: tools that compare language across indictments and judgments, such as how alleged facts are framed and how courts reason through legal issues in criminal trials of journalists.

## Inputs and expected output (from the packet)
- **Inputs:** raw trial-monitoring notes and other documents from one trial: indictments, court judgments, bail hearing decisions, evidence documents.
- **Output:** an analysis of that specific case under domestic, regional and international human rights law.

## What the organizers said at the preparation session
**Problem:** "We may know what happened, but lawyers still have to determine what it means legally." TrialWatch lawyers often review large volumes of monitoring material to identify possible violations and to apply international fair-trial standards consistently.

**Example observation:** "The judge refused to allow the defense to question a prosecution witness."

The legal questions are different:
- Was the restriction justified?
- Did it undermine equality of arms?
- Did it violate the right to examine witnesses?
- Was the court's reasoning sufficient?
- Has this happened elsewhere in the same case?

**What could a tool do?**
- Structure monitor notes
- Surface potential violations of rights
- Link facts to legal standards
- Compare indictments and judgments
- Identify contradictions or missing information
- Compare recurring procedural issues across cases

**Important:** the tool supports legal analysis. It does not replace the lawyer's judgment.

## How a TrialWatch fairness report is built (example: Pan Thalufah, June 2025)
Summarized from the published report. Check the PDF before quoting it anywhere.

- **Monitoring:** monitors attended every hearing in person and transcribed the proceedings in the local language.
- **Assessment:** an expert reviewed the court documents, the monitors' notes and the written judgment, assessed the trial's fairness and assigned a grade. This trial received a **D**.
- **Report structure:** about the author → about TrialWatch → executive summary → political and legal context → case history → methodology → legal analysis → conclusion and grade.
- **Law applied:**
  - International: ICCPR Articles 14 (fair trial), 15 (legality), 19 (expression) and 21 (assembly), with UN Human Rights Committee interpretations and European and Inter-American case law.
  - Domestic: Thai Constitution sections 29, 34 and 54; Criminal Code section 116 (sedition); Computer-Related Crimes Act section 14(3); Criminal Procedure Code section 227.
- **Main findings:**
  - *Presumption of innocence:* the burden of proof was shifted to the defendant, and evidence in her favor (an IP address) was ignored.
  - *Independence:* the court accepted police conclusions without assessing them independently.
  - *Reasoned judgment:* the court did not explain how the evidence proved guilt or met the sedition law's intent requirement.
  - *Freedom of expression and assembly:* posts about peaceful protest were criminalized under vague, overbroad laws without showing direct incitement to violence.
  - *Legality:* the sedition and computer-crime provisions were too vague to give fair notice.
  - *Proportionality:* a two-year prison sentence was excessive.

## What this means for our tool
- **The grade is the expert's call.** Our tool never proposes a grade or a verdict.
- **Several findings come from the judgment, not the hearing notes.** That is why we compare judgments with police reports and indictments (the Copy-Through Detector) and list deeper judgment analysis as the next step.
- **Monitors work in the local language.** Translation can shift legal meaning, so documents are compared only in their original language.
- **Every finding rests on specific facts.** So every potential issue the tool raises must cite the exact lines it relies on.

## Resources from the packet
| Resource | What it is | Link |
|---|---|---|
| TrialWatch India Defamation Dataset | 300 SLAPP and defamation cases with judge findings. Not public; an NDA is likely | mjl2241@columbia.edu |
| Pressing Charges | 423 criminal cases against 427 journalists in India (2012–2022): charges, state, arrest, detention, outcomes, judges' reasoning | https://pressing-charges.com/ |
| Fairness Report: Thailand, Pan Thalufah (June 2025) | Full fair-trial and free-expression assessment. The best model of a Track 2 output | https://hri.law.columbia.edu/sites/default/files/publications/Fairness%20Report_Thailand-Pan%20Thalufah%20June%202025-2.pdf |
| Fairness Report: Thailand (August 2020) | How TrialWatch structures its legal findings | https://hri.law.columbia.edu/sites/default/files/publications/otf-fairness-report-july-2020.pdf |
| Fairness Report: Turkey (August 2020) | The trial of Tuna Altınel | https://hri.law.columbia.edu/sites/default/files/publications/fairness_report_on_the_trial_of_tuna_altinel_in_turkey.pdf |
| Supreme Court of the Philippines | Decisions and resolutions, in English | https://sc.judiciary.gov.ph/decisions/ |
| ZimLII | Zimbabwe judgments, legislation and gazettes | https://zimlii.org/ |
| Thai Supreme Court decisions | Selected decisions in English | https://www.thailawonline.com/supreme-court-decisions/ |
| UN Special Procedures communications | Named cases raised with governments, with government replies where they exist | https://spcommreports.ohchr.org/Tmsearch/TMDocuments |
| HUDOC | European Court of Human Rights case law (Article 6, fair trial) | https://hudoc.echr.coe.int/eng |
| Inter-American Court of Human Rights | Judgments; HURIDOCS also built SUMMA, a searchable database of them | https://jurisprudencia.corteidh.or.cr/en/ |
| African Court on Human and Peoples' Rights | Judgments, mirrored on AfricanLII | https://africanlii.org/en/judgments/AfCHPR/ |
| UN Working Group on Arbitrary Detention | Opinions on individual detention cases | https://wgad-opinions.ohchr.org/ |
| UN Human Rights Committee | Individual communications | https://www.ohchr.org/en/treaty-bodies/ccpr/individual-communications |
| HURIDOCS Uwazi | Open-source human rights documentation platform | https://huridocs.org/technology/uwazi/ |
| TrialWatch training course | The training monitors take; the rubric a legal tool should encode | https://trialwatchtraining.org/ |
| TrialWatch: Our Trials | Public case pages by category | https://cfj.org/trialwatch/trials/ |

## Priority countries (from the Track 1 note)
Philippines, Uganda, Indonesia, Zimbabwe, Thailand, Georgia, Azerbaijan, Turkey, South Africa. Useful when choosing realistic test cases.
