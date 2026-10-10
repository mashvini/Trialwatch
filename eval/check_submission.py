"""Pre-submission checks (T13): run before making the repository public and before submitting.

Usage:  python -m eval.check_submission

FAIL = must fix before submitting (exit code 1). TODO = team input still missing (shown, not fatal).
Checks the whole git history, not just the current files: a secret that was ever committed stays
public once the repository is.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from eval.run_eval import score
from fairtrace import ingest

ROOT = Path(__file__).resolve().parent.parent
DEMO = ROOT / "data" / "demo_case"

# Paths that must never be committed (AGENTS.md rule 7 and .gitignore).
FORBIDDEN_PATH = re.compile(r"(^|/)(\.env|names\.yaml|audit_log\.jsonl)$|(^|/)\.cache/|^fixtures/recorded/|^exports/|^data/local/")
# Common API key shapes: Groq, OpenAI-style, Google. A filled-in "KEY=value" line is caught too.
# Values are plain token characters, so this pattern and its test don't match themselves.
SECRET = re.compile(r"gsk_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{30,}|_API_KEY=[A-Za-z0-9_-]{8,}")
SELF_FILES = ("eval/check_submission.py", "tests/test_check_submission.py")
# Placeholders the team still has to replace, by file.
PLACEHOLDERS = {
    "LICENSE": ["[Team Name]"],
    "README.md": ["*Names and roles.*", "*(Team"],
}
# What the demo case must reproduce in mock mode (AGENTS.md, "What a finished build shows").
EXPECTED_DEMO = {"recall": 1.0, "false_alarms": 0, "citation_rate": 1.0, "rejected_by_verifier": ["F-H01-6"]}


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True).stdout


def check_forbidden_paths() -> list[str]:
    """No secrets file, redaction map, audit log or cache, now or in any past commit."""
    ever = set(git("log", "--all", "--name-only", "--pretty=format:").split()) | set(git("ls-files").split())
    return [f"committed at some point: {p}" for p in sorted(ever) if FORBIDDEN_PATH.search(p)]


def check_secrets() -> list[str]:
    """No API key in any committed line, in any commit."""
    # The checker and its test hold sample patterns and fake values on purpose, so they are skipped.
    log = git("log", "--all", "-p", "--no-color", "--", ".", *(f":(exclude){p}" for p in SELF_FILES))
    added = [line[1:] for line in log.splitlines() if line.startswith("+")]
    return [f"possible secret in history: {line.strip()[:12]}..." for line in added if SECRET.search(line)]


def check_case_labels() -> list[str]:
    """Every case is either synthetic or reconstructed from cited public sources, and every file says so.

    A case with neither label could be real case material, which must never be committed.
    """
    problems = []
    for case_yaml in sorted((ROOT / "data").glob("*/case.yaml")):
        case = ingest.load_case(case_yaml.parent)
        label = "SYNTHETIC" if case.synthetic else "RECONSTRUCTED" if case.provenance else None
        folder = case_yaml.parent.relative_to(ROOT).as_posix()
        if label is None:
            problems.append(f"{folder}: neither synthetic nor a provenance; real case data must not be committed")
            continue
        problems += [
            f"no {label} label: {p.relative_to(ROOT).as_posix()}"
            for p in sorted(case_yaml.parent.rglob("*"))
            if p.is_file() and p.suffix in (".txt", ".yaml") and label not in p.read_text(encoding="utf-8").upper()
        ]
    return problems


def check_demo_numbers() -> list[str]:
    """The mock-mode demo still reproduces the numbers the slides and README quote."""
    result = score(DEMO, "mock") or {}
    return [f"demo {k}: expected {v}, got {result.get(k)}" for k, v in EXPECTED_DEMO.items() if result.get(k) != v]


def check_placeholders() -> list[str]:
    return [
        f"{name}: replace {marker!r}"
        for name, markers in PLACEHOLDERS.items()
        for marker in markers
        if marker in (ROOT / name).read_text(encoding="utf-8")
    ]


def main() -> int:
    failed = False
    checks = [
        ("No secrets file, redaction map or runtime data in git history", check_forbidden_paths, "FAIL"),
        ("No API keys in git history", check_secrets, "FAIL"),
        ("Every case labeled synthetic or reconstructed", check_case_labels, "FAIL"),
        ("Mock demo reproduces its numbers", check_demo_numbers, "FAIL"),
        ("Team placeholders filled in", check_placeholders, "TODO"),
    ]
    for title, check, level in checks:
        problems = check()
        print(f"{'PASS' if not problems else level:4}  {title}")
        for problem in problems:
            print(f"      - {problem}")
        failed = failed or (bool(problems) and level == "FAIL")
    print("\nNot checked here: the GitHub repository is public, the backup video, the slides,")
    print("and a recorded run with a real model (see docs/04_build_plan.md, submission checklist).")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
