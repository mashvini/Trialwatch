"""FairTrace: Streamlit app shell.

Run with:  streamlit run app.py

Every analysis step that isn't built yet raises NotImplementedError("T<n>: ..."). The app catches
it and shows "Not built yet" instead of crashing, so the app runs from day one and shows progress.
"""
from __future__ import annotations

from pathlib import Path

import altair as alt
import streamlit as st

from fairtrace import evaluate, export, extract, flag, heatmap, ingest, redact, review, verify
from fairtrace.analyzers import REGISTRY, in_stage_order
from fairtrace.cache import get_or_run
from fairtrace.config import VALID_MODES, load_settings
from fairtrace.llm import LLM
from fairtrace.schemas import CaseRecord, Decision, Flag
from fairtrace.taxonomy import load_rights

st.set_page_config(page_title="FairTrace", page_icon="⚖️", layout="wide")

settings = load_settings()
rights = load_rights(settings)
RIGHTS = {r.id: r for r in rights}
STATUS_ICON = {"done": "✅", "not built": "🛠️", "waiting": "⏳", "skipped": "⏭️", "error": "❌"}

# ------------------------------------------------------------------ sidebar
st.sidebar.title("⚖️ FairTrace")
st.sidebar.caption("Supports legal analysis. Does not replace the lawyer's judgment.")

mode = st.sidebar.radio(
    "Model mode",
    list(VALID_MODES),
    index=list(VALID_MODES).index(settings.mode),
    horizontal=True,
    help="mock = saved outputs, no network · api = Groq or another OpenAI-compatible API · local = Ollama on this laptop",
)
case_dirs = sorted(p for p in settings.path("data_dir").iterdir() if (p / "case.yaml").exists())
if not case_dirs:
    st.error("No cases found. Add a folder containing case.yaml under data/.")
    st.stop()
case_dir: Path = st.sidebar.selectbox("Case", case_dirs, format_func=lambda p: p.name)

st.sidebar.subheader("Modules")
enabled = [
    aid
    for aid, a in REGISTRY.items()
    if st.sidebar.checkbox(a.label, value=aid in settings.analyzers_enabled, help=a.description, key=f"module-{aid}")
]
names = redact.load_names(case_dir)
if names:
    st.sidebar.caption(f"🔒 Redaction on: {len(names)} names from names.yaml are replaced by roles before any model call.")
else:
    st.sidebar.caption("Redaction off: no names.yaml in this case folder.")
reviewer = st.sidebar.text_input("Reviewer name", help="Recorded with every accept / reject decision.")
run_clicked = st.sidebar.button("Run analysis", type="primary", key="run")


# ------------------------------------------------------------------ pipeline
def run_pipeline() -> tuple[CaseRecord, list[tuple[str, str, str]]]:
    """Run every step that is built; record what happened to each one."""
    log: list[tuple[str, str, str]] = []
    case = ingest.load_case(case_dir)
    record = CaseRecord(case=case)
    llm = LLM(settings, mode)
    st.session_state["rejected"] = []
    st.session_state["run_model"] = llm.model_name  # logged with decisions, even if the sidebar mode changes later

    def step(name: str, fn) -> bool:
        try:
            fn()
        except NotImplementedError as e:
            log.append((name, "not built", str(e)))
            return False
        except Exception as e:  # show any other failure instead of crashing the demo
            log.append((name, "error", f"{type(e).__name__}: {e}"))
            return False
        log.append((name, "done", ""))
        return True

    def do_verify() -> None:
        passed, rejected = verify.verify_flags(record.flags, record, settings, rights)
        record.flags = passed
        st.session_state["rejected"] = rejected

    core = [
        # Redacted once here, so the model, the verifier and Copy-Through all see the same text.
        ("T1 Ingest", lambda: record.source_lines.extend(redact.redact_lines(ingest.read_sources(case_dir, case), names))),
        ("T2 Extract events", lambda: record.events.extend(extract.extract_events(record, llm, settings))),
        ("T3 Flag potential issues", lambda: record.flags.extend(flag.flag_issues(record, llm, settings, rights))),
        ("T4 Verify", do_verify),
    ]
    ok = True
    for name, fn in core:
        if ok:
            ok = step(name, fn)
        else:
            log.append((name, "waiting", "needs the previous step"))

    for analyzer in in_stage_order(enabled):
        available, reason = analyzer.available(record)
        if not available:
            log.append((analyzer.label, "skipped", reason))
            continue
        step(analyzer.label, lambda a=analyzer: a.apply(record, get_or_run(a, record, settings, llm, case_dir), settings))

    review.apply_decisions(record.flags, review.load_decisions(case_dir))
    return record, log


if run_clicked:
    with st.spinner("Running the analysis…"):
        st.session_state["record"], st.session_state["log"] = run_pipeline()

case = ingest.load_case(case_dir)
record: CaseRecord | None = st.session_state.get("record")
if record is not None and record.case.id != case.id:
    record = None  # results belong to another case
log = st.session_state.get("log", []) if record is not None else []

# ------------------------------------------------------------------ header
st.title(case.title)
st.caption(f"{case.country} · {len(case.hearings)} hearings · {len(case.documents)} documents · mode: {mode}")
if case.synthetic:
    st.warning("Synthetic demo data: invented for testing. Not a real case.", icon="🧪")


def not_built(message: str) -> None:
    st.info(f"Not built yet: {message}", icon="🛠️")


FLAG_STATUS = {
    "pending": "⏳ pending",
    "accepted": "✅ accepted",
    "rejected": "🚫 rejected",
    "needs_facts": "❓ needs facts",
}
REVIEW_ACTIONS = [("Accept", "accepted"), ("Reject", "rejected"), ("Needs facts", "needs_facts")]


def decision_provenance(f: Flag, challenge) -> tuple[str, str]:
    """(model, prompt versions) that produced what the reviewer saw on this card."""
    versions = []
    if f.origin == "notes":
        versions.append(f"flag:{settings.prompt_versions.get('flag', '')}")
    if challenge:
        versions.append(f"devils_advocate:{settings.prompt_versions.get('devils_advocate', '')}")
    model = st.session_state.get("run_model", "") if versions else "none (Copy-Through, no model)"
    return model, ", ".join(versions)


def render_flag(f: Flag, rec: CaseRecord, last: Decision | None) -> None:
    right = RIGHTS.get(f.right_id)
    lines = rec.lines_by_id()
    with st.container(border=True):
        origin = " · from Copy-Through (no AI)" if f.origin == "copy_through" else ""
        st.markdown(
            f"**{right.name if right else f.right_id}** · `{f.id}` · {FLAG_STATUS.get(f.status, f.status)}{origin}"
        )
        if last:
            note = f": “{last.note}”" if last.note else ""
            st.caption(f"Last decision: {last.decision} by {last.reviewer}, {last.timestamp[:16].replace('T', ' ')} UTC{note}")
        st.write(f.explanation)
        st.markdown(f"Quoted: “{f.quote}”")
        for sid in f.source_ids:
            text = lines[sid].text if sid in lines else "⚠️ unknown source"
            st.markdown(f"> `{sid}` {text}")
        if f.questions_for_lawyer:
            st.markdown("**Questions for the lawyer**\n" + "\n".join(f"- {q}" for q in f.questions_for_lawyer))
        if f.missing_facts:
            st.markdown("**Missing facts (asked of the monitor)**\n" + "\n".join(f"- {q}" for q in f.missing_facts))
        for note in f.verifier_notes:
            st.warning(note)
        challenge = next((c for c in rec.challenges if c.flag_id == f.id), None)
        if challenge:
            st.markdown(f"**Devil's Advocate.** What the state could argue: {challenge.state_argument}")
            cites = " ".join(f"`{s}`" for s in challenge.source_ids)
            st.markdown(f"Record check: **{challenge.verdict.replace('_', ' ')}** {cites}")
            if challenge.reasoning:
                st.caption(challenge.reasoning)
        note = st.text_input("Note for the audit log (optional)", key=f"note-{f.id}")
        cols = st.columns(3)
        for col, (label, status) in zip(cols, REVIEW_ACTIONS):
            # A reviewer name is required, and re-clicking the current status would only add noise to the log.
            if col.button(label, key=f"{status}-{f.id}", disabled=not reviewer.strip() or f.status == status):
                if not reviewer.strip():  # the disabled button is the UI; this keeps the rule in code too
                    st.error("Enter your name in the sidebar first.")
                    continue
                model, prompt_version = decision_provenance(f, challenge)
                review.record_decision(
                    case_dir,
                    Decision(
                        flag_id=f.id,
                        decision=status,
                        reviewer=reviewer.strip(),
                        note=note.strip(),
                        model=model,
                        prompt_version=prompt_version,
                    ),
                )
                f.status = status
                st.rerun()


def render_heatmap(rec: CaseRecord) -> None:
    """T12: potential issues by right and hearing, to show where problems cluster."""
    st.subheader("Where potential issues cluster")
    scope = st.radio(
        "Count", ["Not rejected by a reviewer", "Accepted only"], horizontal=True, key="heatmap-scope"
    )
    keep = ("accepted",) if scope == "Accepted only" else ("pending", "accepted", "needs_facts")
    grid = heatmap.issue_grid(rec, rights, [f for f in rec.flags if f.status in keep])
    base = alt.Chart(alt.Data(values=grid)).encode(
        x=alt.X("hearing:N", title=None, sort=None, axis=alt.Axis(orient="top", labelAngle=0)),
        y=alt.Y("right:N", title=None, sort=[r.name for r in rights], axis=alt.Axis(labelLimit=320)),
    )
    shade = alt.Color(
        "count:Q",
        title="Potential issues",
        scale=alt.Scale(scheme="blues", domainMin=0),
        legend=alt.Legend(values=list(range(max(c["count"] for c in grid) + 1)), format="d"),  # whole numbers only
    )
    cells = base.mark_rect(stroke="white").encode(
        # Empty cells stay neutral grey, so "none" never reads as a small amount.
        color=alt.condition("datum.count > 0", shade, alt.value("#f0f2f6")),
        tooltip=[alt.Tooltip("right:N"), alt.Tooltip("hearing:N"), alt.Tooltip("count:Q"), alt.Tooltip("flags:N")],
    )
    labels = base.mark_text().encode(
        text=alt.condition("datum.count > 0", "count:Q", alt.value("")),
        color=alt.condition("datum.count > 1", alt.value("white"), alt.value("black")),
    )
    st.altair_chart((cells + labels).properties(height=34 * len(rights)), use_container_width=True)
    st.caption("A count of potential issues, not a measure of fairness. Hover a cell for its flag IDs.")


tabs = st.tabs(
    ["Overview", "Sources", "Issues to review", "Copy-Through", "Questions for the monitor", "Export", "Evaluation", "About"]
)

# ------------------------------------------------------------------ Overview
with tabs[0]:
    if not log:
        st.info("Press **Run analysis** in the sidebar.")
    else:
        st.subheader("Pipeline status")
        for name, state, message in log:
            suffix = f": {message}" if message else ""
            st.markdown(f"{STATUS_ICON.get(state, '•')} **{name}** ({state}){suffix}")
    if record is not None:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Numbered sources", len(record.source_lines))
        c2.metric("Events", len(record.events))
        c3.metric("Potential issues", len(record.flags))
        c4.metric("Challenges", len(record.challenges))
        if record.flags:
            render_heatmap(record)

# ------------------------------------------------------------------ Sources
with tabs[1]:
    if record is None or not record.source_lines:
        not_built("numbered sources appear here once T1 (ingest) is built and the analysis has run.")
    else:
        docs = list(dict.fromkeys(line.doc for line in record.source_lines))
        pick = st.selectbox("Source", docs)
        st.code("\n".join(f"{line.id}  {line.text}" for line in record.lines_for(pick)), language=None)

# ------------------------------------------------------------------ Issues to review
with tabs[2]:
    if record is None or not record.flags:
        not_built("potential issues appear here once T2–T4 are built, or when Copy-Through finds strong matches.")
    else:
        counts = {s: sum(1 for f in record.flags if f.status == s) for s in FLAG_STATUS}
        reviewed = len(record.flags) - counts["pending"]
        st.progress(reviewed / len(record.flags), text=f"{reviewed} of {len(record.flags)} potential issues reviewed")
        st.caption(" · ".join(f"{FLAG_STATUS[s]}: {n}" for s, n in counts.items()))
        if not reviewer.strip():
            st.warning("Enter your name in the sidebar to accept or reject potential issues.")
        shown = st.multiselect(
            "Show",
            list(FLAG_STATUS),
            default=["pending", "needs_facts", "accepted"],
            format_func=lambda s: FLAG_STATUS[s],
        )
        latest = review.latest_decisions(review.load_decisions(case_dir))
        for f in record.flags:
            if f.status in shown:
                render_flag(f, record, latest.get(f.id))
    rejected = st.session_state.get("rejected", []) if record is not None else []
    if rejected:
        with st.expander(f"Rejected by the verifier ({len(rejected)})"):
            st.caption("Model output that failed the citation checks. Shown so nothing disappears silently.")
            for f in rejected:
                right = RIGHTS.get(f.right_id)
                st.markdown(
                    f"`{f.id}` **{right.name if right else f.right_id}**: quoted “{f.quote}”, "
                    f"citing {', '.join(f'`{s}`' for s in f.source_ids) or 'nothing'}. "
                    f"Reason: {'; '.join(f.verifier_notes)}"
                )

# ------------------------------------------------------------------ Copy-Through
with tabs[3]:
    if "copy_through" not in enabled:
        st.info("Copy-Through is switched off in the sidebar.")
    elif record is None or record.copy_report is None:
        not_built("results appear here once T7 (Copy-Through) is built and the analysis has run.")
    else:
        report = record.copy_report
        c1, c2 = st.columns(2)
        c1.metric("Judgment text copied (whole judgment)", f"{report.coverage_overall:.0%}")
        c2.metric(
            "Copied within the court's own reasoning",
            "n/a" if report.coverage_reasoning is None else f"{report.coverage_reasoning:.0%}",
        )
        st.dataframe([m.model_dump() for m in report.matches])

# ------------------------------------------------------------------ Questions for the monitor (Gap Finder)
with tabs[4]:
    if record is None:
        st.info("Run the analysis first.")
    else:
        st.caption(
            "Facts the notes don't record, asked rather than assumed, so the monitor can answer while the "
            "hearing is fresh. From each potential issue's missing facts, and from Devil's Advocate checks "
            "where the record is silent. Potential issues a reviewer rejected are left out."
        )
        groups = export.monitor_questions(record, ("pending", "accepted", "needs_facts"), include_challenges=True)
        if not groups:
            st.info("No open questions for the monitor.")
        else:
            total = sum(len(items) for items in groups.values())
            st.download_button(
                f"Download checklist for the monitor ({total} questions, .md)",
                export.questions_checklist(record, groups),
                file_name=f"{record.case.id}_questions_for_monitor.md",
            )
            for label, items in groups.items():
                st.markdown(f"**{label}**")
                for item in items:
                    origin = " · Devil's Advocate" if item.source == "devils_advocate" else ""
                    st.markdown(f"- {item.question} *(`{item.flag_id}`{origin})*")

# ------------------------------------------------------------------ Export
with tabs[5]:
    if record is None:
        st.info("Run the analysis first.")
    else:
        restore = names and st.checkbox(
            "Restore real names in the export",
            help="Names stay redacted in the app and in every model call. Tick only if this draft may contain them.",
        )
        try:
            md = export.export_markdown(record, rights, reviewer.strip(), restore_names=names if restore else None)
        except NotImplementedError as e:
            not_built(str(e))
        else:
            st.download_button("Download draft findings (.md)", md, file_name=f"{record.case.id}_draft_findings.md")
            st.markdown(md)

# ------------------------------------------------------------------ Evaluation
with tabs[6]:
    key = evaluate.load_answer_key(case_dir)
    if key is None:
        st.info("Add answer_key.yaml to the case folder to measure results.")
    elif record is None:
        st.info("Run the analysis first.")
    else:
        try:
            result = evaluate.evaluate(record.flags, key, record.line_ids())
        except NotImplementedError as e:
            not_built(str(e))
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Expected issues caught", f"{len(result['caught'])} / {len(result['caught']) + len(result['missed'])}")
            c2.metric("False alarms (clean hearings)", result["false_alarms"])
            c3.metric("Citations verified", f"{result['citation_rate']:.0%}")
            c4.metric("Potential issues raised", result["flags_total"])
            st.write("Missed:", result["missed"] or "none")
            st.write("Not detectable by this version:", result["not_detectable"] or "none")

# ------------------------------------------------------------------ About
with tabs[7]:
    st.markdown(
        """
**FairTrace** helps TrialWatch lawyers turn trial-monitoring notes and court documents into
*potential* fair-trial issues, each tied to the exact lines it comes from.

- The model is used in three steps only; citations, matching, scoring and export are plain code.
- Every citation is checked; anything that fails is shown, not hidden.
- Nothing is exported without a lawyer's decision, and every decision is logged.
- The tool never proposes verdicts or grades.
- Confidential cases can run on a local model (`local` mode) with names redacted.

See `docs/07_responsible_ai.md` for risks, mitigations and limitations.
"""
    )
