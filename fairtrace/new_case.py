"""Create a case folder from uploaded files (the app's "Add a case" tab). Plain code, no model.

New cases are written under data/local/, which is git-ignored, so material uploaded in the app is
never committed by accident. The folder has the same format as data/demo_case/ (see data/README.md).
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

from .ingest import split_paragraphs
from .schemas import Case, DocType, DocumentRef, HearingRef

LOCAL_DIR = "local"                      # under data/: git-ignored
Kind = Literal["synthetic", "reconstructed", "confidential"]


class Upload(BaseModel):
    """One uploaded text file."""

    name: str
    text: str


class DocumentUpload(Upload):
    id: str                              # paragraph-ID prefix, e.g. "JDG"
    type: DocType
    reasoning_paragraphs: tuple[int, int] | None = None   # judgments only


class NewCase(BaseModel):
    title: str
    country: str
    kind: Kind
    source: str = ""                     # required when kind == "reconstructed"
    language: str = "en"
    charges: list[str] = []
    hearings: list[Upload]
    hearing_dates: list[str] = []        # optional, in hearing order
    documents: list[DocumentUpload] = []
    names: str = ""                      # optional names.yaml content ("Real Name: ROLE" per line)


def decode(data: bytes) -> str:
    """Uploaded bytes as text. UTF-8 only (a BOM is dropped); anything else is a visible error."""
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        raise ValueError("Files must be plain text in UTF-8. Re-save the file as UTF-8 and upload it again.") from e


def slugify(title: str) -> str:
    """'Philippines: Case of X' -> 'philippines_case_of_x' (letters, digits and _ only)."""
    slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
    return slug[:48] or "case"


def problems(new: NewCase) -> list[str]:
    """Everything wrong with the input, in plain words. Empty means it can be saved."""
    found = []
    if not new.title.strip():
        found.append("Give the case a title.")
    if not new.country.strip():
        found.append("Give the country.")
    if new.kind == "reconstructed" and not new.source.strip():
        found.append("A case reconstructed from public sources needs its source (a link or citation).")
    if not new.hearings:
        found.append("Upload at least one hearing file.")
    if any(not h.text.strip() for h in new.hearings + new.documents):
        found.append("One of the files is empty.")
    if len(new.hearing_dates) > len(new.hearings):
        found.append("There are more hearing dates than hearing files.")
    bad_dates = [d for d in new.hearing_dates if d and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d)]
    if bad_dates:
        found.append(f"Dates must look like 2026-03-02: {', '.join(bad_dates)}")
    ids = [d.id for d in new.documents]
    if any(not re.fullmatch(r"[A-Z]{2,5}", i) for i in ids):
        found.append("Document prefixes must be 2 to 5 capital letters, for example JDG or POL.")
    if len(set(ids)) != len(ids):
        found.append("Each document needs its own prefix.")
    for d in new.documents:
        if d.reasoning_paragraphs is None:
            continue
        first, last = d.reasoning_paragraphs
        count = len(split_paragraphs(DocumentRef(id=d.id, type=d.type, file="x"), d.text))
        if not 1 <= first <= last <= count:
            found.append(f"{d.name}: the reasoning range must be within paragraphs 1 to {count}.")
    if new.names.strip():
        try:
            parsed = yaml.safe_load(new.names)
        except yaml.YAMLError:
            parsed = None
        if not isinstance(parsed, dict):
            found.append('Names to redact must be one per line, like  "Maria Santos": DEFENDANT')
    return found


def to_case(new: NewCase, case_id: str) -> Case:
    """The case.yaml contents. Hearings are numbered H01, H02... in upload order."""
    hearings = [
        HearingRef(id=f"H{i:02d}", file=f"hearings/hearing_{i:02d}.txt", date=(new.hearing_dates[i - 1] or None) if i <= len(new.hearing_dates) else None)
        for i in range(1, len(new.hearings) + 1)
    ]
    documents = [
        DocumentRef(id=d.id, type=d.type, file=f"documents/{d.id.lower()}.txt", language=new.language, reasoning_paragraphs=d.reasoning_paragraphs)
        for d in new.documents
    ]
    provenance = f"Reconstructed from public sources: {new.source.strip()}" if new.kind == "reconstructed" else ""
    return Case(
        id=case_id, title=new.title.strip(), country=new.country.strip(), language=new.language,
        synthetic=new.kind == "synthetic", provenance=provenance,
        charges=[c.strip() for c in new.charges if c.strip()], hearings=hearings, documents=documents,
    )


def write_case(data_dir: Path, new: NewCase) -> Path:
    """Write the case under data/local/<slug>/ and return the folder. Never overwrites a case."""
    errors = problems(new)
    if errors:
        raise ValueError(" ".join(errors))
    root = Path(data_dir) / LOCAL_DIR
    slug, n = slugify(new.title), 2
    folder = root / slug
    while folder.exists():
        folder, n = root / f"{slug}_{n}", n + 1
    case = to_case(new, f"local_{folder.name}")
    (folder / "hearings").mkdir(parents=True)
    for ref, upload in zip(case.hearings, new.hearings):
        (folder / ref.file).write_text(upload.text, encoding="utf-8")
    if new.documents:
        (folder / "documents").mkdir()
    for ref, upload in zip(case.documents, new.documents):
        (folder / ref.file).write_text(upload.text, encoding="utf-8")
    if new.names.strip():
        (folder / "names.yaml").write_text(new.names, encoding="utf-8")
    header = f"# Added in the FairTrace app ({new.kind}). Stored under data/{LOCAL_DIR}/, which git ignores.\n"
    body = yaml.safe_dump(case.model_dump(mode="json", exclude_defaults=True), sort_keys=False, allow_unicode=True)
    (folder / "case.yaml").write_text(header + body, encoding="utf-8")
    return folder


def local_cases(data_dir: Path) -> list[Path]:
    """Case folders added in the app, in name order."""
    root = Path(data_dir) / LOCAL_DIR
    return sorted(p for p in root.iterdir() if (p / "case.yaml").exists()) if root.exists() else []
