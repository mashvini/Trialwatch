# Case data

One folder per case. The app lists every folder that contains a `case.yaml`.

```
data/<case_id>/
├── case.yaml          metadata, hearing list, document list (reasoning_paragraphs for judgments)
├── hearings/*.txt     one file per hearing; one observation per line; "#" lines are comments
├── documents/*.txt    plain text, paragraphs separated by blank lines, all in the same language
├── answer_key.yaml    expected issues, for evaluation
└── names.yaml         optional redaction map (git-ignored; see demo_case/names.example.yaml)
```

| Folder | What it is |
| --- | --- |
| `demo_case/` | **Synthetic**: invented for testing, not a real case. The default case in the app |
| `philippines_cumpio/` | **Reconstructed from public reporting**: the case of journalist Frenchie Mae Cumpio and human rights defender Mariel Domequil, as described in a public [TrialWatch article](https://hri.law.columbia.edu/trialwatch-five-questions-court-deciding-case-journalist-frenchie-mae-cumpio-and-human-rights). The article groups the record by theme, so each "hearing" is a theme; people are named by role; every line paraphrases the article. Not real monitoring notes or court records. The court ruled in January 2026, after the article; that ruling and the judgment (not public) are not included |

A case built from public material sets `provenance` in `case.yaml` and starts every file with a `RECONSTRUCTED` label; an invented one sets `synthetic: true` and a `SYNTHETIC` label. `python -m eval.check_submission` fails on a case folder with neither.

**Never commit real confidential case data.** Use public or synthetic material, labeled as such.
How to write test notes and answer keys: [../docs/09_teammate_inputs.md](../docs/09_teammate_inputs.md).
