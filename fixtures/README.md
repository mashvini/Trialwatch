# Fixtures

Saved model outputs used in **mock mode**: by tests, while building the UI, and as the demo safety net.

## Lookup order
`fixtures/mock/<prompt>.<key>.json`, then `fixtures/mock/<prompt>.json`.

| Prompt | Key | Files |
|---|---|---|
| `extract` | hearing id | `extract.H01.json`, `extract.H02.json` |
| `flag` | hearing id | `flag.H01.json`, `flag.H02.json` (no flags: the clean hearing) |
| `devils_advocate` | flag id | `devils_advocate.json` holds challenges for all flags; the module keeps the one whose `flag_id` matches |

## Two deliberate mistakes (to show the guardrails working)
1. **`F-H01-6` in `flag.H01.json`** quotes words that are not in its cited line (`H01-L011`). The verifier (T4) must reject it, and it should appear under "Rejected by the verifier".
2. **The challenge for `F-H01-4`** in `devils_advocate.json` claims "rebutted" but cites `H01-L099`, which doesn't exist. `verify_challenge` (T6) must drop the citation and downgrade the verdict to `not_addressed`.

Keep both when you replace these files with real outputs; they make the demo's guardrail moment reliable.

## Recording real outputs
Run with `FAIRTRACE_RECORD=1` in `api` or `local` mode. Outputs are saved to `fixtures/recorded/` (git-ignored) under the same names. Review them, then copy the good ones into `fixtures/mock/`.

All fixture content refers to the **synthetic** demo case in `data/demo_case/`.
