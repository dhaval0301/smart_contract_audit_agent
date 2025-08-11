# main.py
import os
import json
import hashlib
import datetime
import smtplib
from email.message import EmailMessage

import streamlit as st
from dotenv import load_dotenv

from agent import audit_contract, explain_audit_simple

# -------------------------------------------------
# Setup
# -------------------------------------------------
load_dotenv()
st.set_page_config(page_title="Smart Contract Audit Agent", layout="centered")
st.title(" Smart Contract Audit Agent")

# -------------------------------------------------
# Session defaults
# -------------------------------------------------
for k, v in {
    "code_text": "",
    "report": "",
    "simple_report": "",
    "audit_done": False,
    "simple_done": False,
    "selected_history_id": "",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -------------------------------------------------
# Audit History helpers (JSON file)
# -------------------------------------------------
HISTORY_PATH = "audit_history.json"

def _now_iso():
    return datetime.datetime.now().isoformat(timespec="seconds")

def _code_hash(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()[:12]

def load_history():
    if not os.path.exists(HISTORY_PATH):
        return []
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_history(history):
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def infer_title_from_report(report: str) -> str:
    for line in (report or "").splitlines():
        line = line.strip("# ").strip()
        if line:
            return line[:60]
    return "Audit"

def add_history_entry(code: str, report: str, simple_report: str = ""):
    entry = {
        "id": _code_hash(code) + "-" + _now_iso().replace(":", ""),
        "timestamp": _now_iso(),
        "code_hash": _code_hash(code),
        "code": code,
        "report": report,
        "simple_report": simple_report or "",
        "title": infer_title_from_report(report),
    }
    history = load_history()
    history.insert(0, entry)  # newest first
    save_history(history)
    return entry

def delete_history_entry(entry_id: str):
    history = load_history()
    history = [e for e in history if e.get("id") != entry_id]
    save_history(history)

# -------------------------------------------------
# Email helper
# -------------------------------------------------
def send_email(body: str, to_email: str, subject: str) -> str:
    host = os.getenv("SMTP_HOST", "")
    port = int(os.getenv("SMTP_PORT", "587") or "587")
    user = os.getenv("SMTP_USER", "")
    pwd  = os.getenv("SMTP_PASS", "")

    if not all([host, port, user, pwd]):
        return "SMTP settings missing. Check .env (SMTP_HOST/PORT/USER/PASS)."

    try:
        msg = EmailMessage()
        msg["From"] = user
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)
        # Optional attachment
        msg.add_attachment(body.encode("utf-8"),
                           maintype="text", subtype="plain",
                           filename="audit_report.txt")
        with smtplib.SMTP(host, port) as s:
            s.starttls()
            s.login(user, pwd)
            s.send_message(msg)
        return "sent"
    except Exception as e:
        return f"Email error: {e}"

# -------------------------------------------------
# Sidebar: Audit History
# -------------------------------------------------
with st.sidebar:
    st.header(" Audit History")
    history = load_history()
    if not history:
        st.caption("No history yet. Run an audit to save it here.")
    else:
        labels = [
            f"{h['timestamp']} • {h.get('title','Audit')} • {h.get('code_hash','')}"
            for h in history
        ]
        idx = st.selectbox(
            "Previous audits",
            options=list(range(len(history))),
            format_func=lambda i: labels[i],
            key="history_select"
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button(" Load", use_container_width=True):
                entry = history[idx]
                st.session_state.code_text = entry.get("code","")
                st.session_state.report = entry.get("report","")
                st.session_state.simple_report = entry.get("simple_report","")
                st.session_state.audit_done = bool(st.session_state.report)
                st.session_state.simple_done = bool(st.session_state.simple_report)
                st.success("Loaded this audit into the editor.")
        with c2:
            if st.button(" Delete", use_container_width=True):
                delete_history_entry(history[idx].get("id",""))
                st.experimental_rerun()
        with c3:
            if st.button(" Clear All", use_container_width=True):
                if os.path.exists(HISTORY_PATH):
                    os.remove(HISTORY_PATH)
                st.experimental_rerun()

# -------------------------------------------------
# Input: upload or paste code
# -------------------------------------------------
st.write("Upload a `.sol` file *or* paste Solidity code.")
uploaded = st.file_uploader("Upload Solidity (.sol)", type=["sol"], key="uploader")

if uploaded is not None and not st.session_state.code_text:
    try:
        st.session_state.code_text = uploaded.read().decode("utf-8", errors="ignore")
    except Exception as e:
        st.error(f"Could not read file: {e}")

st.session_state.code_text = st.text_area(
    "…or paste code",
    value=st.session_state.code_text,
    height=220,
    placeholder="pragma solidity ^0.8.20;\ncontract Example { /* ... */ }",
    key="code_area",
)

# -------------------------------------------------
# Actions
# -------------------------------------------------
c1, c2, c3 = st.columns([1,1,1])
with c1:
    gen_clicked = st.button(" Generate Audit", key="btn_generate", use_container_width=True)
with c2:
    explain_clicked = st.button(" Explain Simply", key="btn_explain", use_container_width=True)
with c3:
    clear_clicked = st.button(" Clear", key="btn_clear", use_container_width=True)

# Clear state
if clear_clicked:
    st.session_state.code_text = ""
    st.session_state.report = ""
    st.session_state.simple_report = ""
    st.session_state.audit_done = False
    st.session_state.simple_done = False
    st.experimental_rerun()

# Generate audit
if gen_clicked:
    if not st.session_state.code_text or len(st.session_state.code_text.strip()) < 10:
        st.warning("Please upload or paste a Solidity contract.")
    else:
        with st.spinner("Auditing…"):
            st.session_state.report = audit_contract(st.session_state.code_text)
            st.session_state.audit_done = True
            st.session_state.simple_report = ""
            st.session_state.simple_done = False
        # Save to history
        add_history_entry(
            code=st.session_state.code_text,
            report=st.session_state.report,
            simple_report=st.session_state.simple_report or ""
        )

# Explain simply
if explain_clicked:
    if not st.session_state.audit_done or not st.session_state.report:
        st.info("Generate an audit first.")
    else:
        with st.spinner("Rewriting in simpler language…"):
            st.session_state.simple_report = explain_audit_simple(st.session_state.report)
            st.session_state.simple_done = True
        # Optionally also store simplified version as a separate history entry
        add_history_entry(
            code=st.session_state.code_text,
            report=st.session_state.report,
            simple_report=st.session_state.simple_report
        )

# -------------------------------------------------
# Output
# -------------------------------------------------
if st.session_state.audit_done and st.session_state.report:
    st.markdown("##  Audit Report")
    st.markdown(st.session_state.report)

if st.session_state.simple_done and st.session_state.simple_report:
    st.markdown("###  Simplified Explanation")
    st.markdown(st.session_state.simple_report)

# -------------------------------------------------
# Email form (stable via form submit)
# -------------------------------------------------
st.markdown("---")
st.markdown("###  Email this report")

with st.form(key="email_form", clear_on_submit=False):
    to_email = st.text_input("Recipient email")
    subject = st.text_input("Subject", value="Smart Contract Audit Report")
    version = st.selectbox(
        "Choose version",
        ["Original audit", "Simplified (if available)"],
        index=0,
    )
    submit_email = st.form_submit_button(" Send Email")

if submit_email:
    if not to_email:
        st.warning("Enter a recipient email.")
    else:
        body = st.session_state.report
        if version.startswith("Simplified") and st.session_state.simple_report:
            body = st.session_state.simple_report
        elif version.startswith("Simplified") and not st.session_state.simple_report:
            st.info("No simplified version generated yet — sending original instead.")

        status = send_email(body, to_email, subject)
        if status == "sent":
            st.success("Email sent ")
        else:
            st.error(status)

# -------------------------------------------------
# Save last audit to file (optional)
# -------------------------------------------------
if st.session_state.audit_done and st.session_state.report:
    try:
        os.makedirs("reports", exist_ok=True)
        with open("reports/audit_report.txt", "w", encoding="utf-8") as f:
            f.write(st.session_state.report)
    except Exception as e:
        st.warning(f"Couldn’t save report: {e}")
