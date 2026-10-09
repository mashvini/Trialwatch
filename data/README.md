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

`demo_case/` is **synthetic**: invented for testing, not a real case.

**Never commit real confidential case data.** Use public or synthetic material, labeled as such.
How to write test notes and answer keys: [../docs/09_teammate_inputs.md](../docs/09_teammate_inputs.md).
