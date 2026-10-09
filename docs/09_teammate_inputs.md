# Inputs needed from the law team

The tool is only as good as the legal content and test data behind it. Everything here is plain text or YAML, so no coding is needed.

## Needed by Thursday night
| Item | File | Owner | Status |
|---|---|---|---|
| Review the rights list | `taxonomy/rights.yaml` | | [ ] |
| Sample notes for 3–4 hearings, including one clean hearing | `data/<case>/hearings/*.txt` | | [ ] |
| Answer key for those notes | `data/<case>/answer_key.yaml` | | [ ] |
| 2 worked examples | `taxonomy/worked_examples.yaml` | | [ ] |
| (If possible) a judgment plus an indictment or police report in the same language | `data/<case>/documents/*.txt` | | [ ] |

The synthetic demo case in `data/demo_case/` shows every format. Copy that folder, rename it, and replace the contents.

## 1. Sample monitor notes
**Format:** one plain-text file per hearing. Lines starting with `#` are comments (not cited). Every other line gets a number, so keep **one observation per line**.

```
# Hearing H01 | 2026-03-02 | Monitor M1 | Proceedings in English

09:58 Defense counsel stood to cross-examine witness 1. Judge said the questions were "not necessary" and did not allow them.
10:00 Defense counsel objected. Judge noted the objection and moved on.
```

**Rules:**
- **Write observations, not conclusions.** The tool has to find the issue; if the notes already name it, the test proves nothing.
  - Good: "Judge did not allow the defense to cross-examine witness 1."
  - Bad: "Judge violated the right to examine witnesses."
- Write what a monitor could actually see or hear: who did what, when, and what was said.
- Leave some facts out on purpose (for example, no reason given for an absence). The tool should ask about them.
- **Include one hearing where nothing goes wrong.** Any flag there is a false alarm, which tests the tool's restraint.
- Base the notes on a public case, such as the Pan Thalufah report, or invent them. Never use real confidential notes. Label invented material as synthetic in the `#` header.

List each hearing in `case.yaml`:
```yaml
hearings:
  - {id: H01, date: "2026-03-02", file: hearings/hearing_01.txt}
```

## 2. Rights list review (`taxonomy/rights.yaml`)
The draft covers 8 rights: 6 a monitor can observe in court, and 2 that need the judgment text. For each entry, check:
- **basis:** the right article and General Comment.
- **red_flags:** concrete things a monitor might write down. These drive what the tool looks for.
- **key_questions:** what the lawyer must answer. These appear on every flag.
- **regional_references:** add European, Inter-American or African case law where it helps.
- Change `status: draft` to `status: reviewed` when done.

**Never rename an `id`** once tests or the answer key use it. Add a new entry instead.

## 3. Worked examples (`taxonomy/worked_examples.yaml`)
Two examples teach the model the expected style. Each has: the observation (with its line ID), the potential issue (`right_id` and explanation in "potential issue" language), the questions for the lawyer, and the missing facts. Replace the two drafts with examples you're happy to defend.

## 4. Answer key (`data/<case>/answer_key.yaml`)
```yaml
case_id: demo_synthetic
expected:
  - id: A1
    right_id: examine_witnesses
    source_ids: [H01-L012]
    note: Defense stopped from cross-examining the police investigator.
  - id: A7
    right_id: reasoned_judgment
    source_ids: [JDG-P004]
    note: Defense argument dismissed without reasons.
    detectable_by_mvp: false      # needs analysis we haven't built
clean_hearings: [H02]
```
- **Matching rule:** an expected issue counts as caught if any flag has the same `right_id` and cites at least one of the same lines.
- **Line IDs:** `H01-L012` = hearing H01, line 12 of the file, counting every line including blank and `#` lines. Paragraph IDs: `JDG-P004` = the 4th paragraph of the judgment (paragraphs are separated by blank lines).
- Mark issues our tool can't detect yet with `detectable_by_mvp: false`, so they don't count against recall but stay visible.

## 5. Copy-Through test documents (optional)
- Put each document in `documents/` as plain text, one paragraph per block, blank lines between paragraphs.
- All documents in the **same language**, never a translation against an original.
- In `case.yaml`, mark which paragraphs of the judgment are the court's **own reasoning**:
  ```yaml
  documents:
    - {id: POL, type: police_report, file: documents/police_report.txt}
    - {id: JDG, type: judgment, file: documents/judgment.txt, reasoning_paragraphs: [3, 4]}
  ```
- Good public source: Philippine Supreme Court decisions (in English). They usually quote the charge sheet in full, which tests that legitimate quoting is *not* flagged.

## 6. Prompt review
The model's instructions are in `prompts/*.md`. You can edit the wording freely, but:
- keep the `## System` and `## User` headings;
- keep placeholders like `{{lines}}` exactly as they are;
- keep the JSON shape described at the end of the system section.

Test changes by pasting a prompt and sample notes into a chat tool before Friday.
