

# Smart Contract Audit Agent

## Overview

The **Smart Contract Audit Agent** is a practice project that demonstrates how Agentic AI can assist in auditing Solidity smart contracts.
It analyzes contracts for security vulnerabilities, gas optimization opportunities, and code quality improvements.
The project also supports generating beginner-friendly explanations and exporting audit reports via email, with audit history management.

**Note:** This tool is intended for learning and experimentation purposes only. It is **not** production-ready and should not be relied upon for real-world security audits.

---

## Features

* **Security Analysis** – Detects common vulnerabilities such as reentrancy attacks.
* **Gas Optimization** – Identifies unnecessary or inefficient operations.
* **Code Quality Checks** – Suggests improvements for maintainability and clarity.
* **Beginner Mode** – Explains audit results in simplified language.
* **Report Export** – Email audit results directly from the app.
* **Audit History** – Store and view past audits.

---

## Tech Stack

* **Python 3.10+**
* **Streamlit** – For the web interface
* **OpenAI GPT-4 API** – For AI-powered analysis
* **SMTP (Email)** – For sending reports via email

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/dhaval0301/smart_contract_audit_agent.git
cd smart-contract-audit-agent
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate   # On Windows use: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root with the following keys:

```env
OPENAI_API_KEY=your_openai_api_key
EMAIL_ADDRESS=your_email@example.com
EMAIL_PASSWORD=your_email_password_or_app_specific_password
SMTP_SERVER=smtp.yourprovider.com
SMTP_PORT=587
```

### 5. Run the app

```bash
streamlit run main.py
```

---

## How It Works

1. **Upload** a Solidity contract file (`.sol`).
2. The AI agent analyzes the code:

   * Identifies security risks.
   * Suggests gas optimization strategies.
   * Recommends code quality improvements.
3. Choose output mode:

   * **Detailed audit report**
   * **Beginner-friendly explanation**
4. Optionally email the report and store it in audit history.

---

## Limitations

* The AI model’s recommendations should be reviewed by a qualified security auditor.
* This project is intended for educational purposes only.
* Some suggestions may be incomplete or require adaptation to the contract context.




