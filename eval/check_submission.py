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

ROOT = Path(__file__).resolve().parent.parent
DEMO = ROOT / "data" / "demo_case"

# Paths that must never be committed (AGENTS.md rule 7 and .gitignore).
FORBIDDEN_PATH = re.compile(r"(^|/)(\.env|names\.yaml|audit_log\.jsonl)$|(^|/)\.cache/|^fixtures/recorded/|^exports/")
# Common API key shapes: Groq, OpenAI-style, Google. A filled-in "KEY=value" line is caught too.
SECRET = re.compile(r"gsk_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{30,}|_API_KEY=\S{8,}")
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
    added = [line[1:] for line in git("log", "--all", "-p", "--no-color").splitlines() if line.startswith("+")]
    return [f"possible secret in history: {line.strip()[:12]}…" for line in added if SECRET.search(line)]


def check_synthetic_labels() -> list[str]:
    """Every demo file says it is synthetic, and case.yaml marks it so the app labels it."""
    problems = [
        f"no SYNTHETIC label: {p.relative_to(ROOT).as_posix()}"
        for p in sorted(DEMO.rglob("*"))
        if p.is_file() and p.suffix in (".txt", ".yaml") and "SYNTHETIC" not in p.read_text(encoding="utf-8").upper()
    ]
    if "synthetic: true" not in (DEMO / "case.yaml").read_text(encoding="utf-8"):
        problems.append("data/demo_case/case.yaml: synthetic is not true")
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
        ("Demo data labeled synthetic", check_synthetic_labels, "FAIL"),
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
