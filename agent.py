# agent.py
import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

# Load .env (OPENAI_API_KEY, etc.)
load_dotenv()

# Initialize OpenAI client (requires OPENAI_API_KEY in env)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def audit_contract(code: str, model: str = "gpt-4", temperature: float = 0.3,
                   max_tokens: int = 1800) -> str:
    """
    Analyze a Solidity smart contract for:
      1) Security vulnerabilities
      2) Gas optimization opportunities
      3) Code quality improvements

    Returns a structured audit report as markdown text.
    """
    prompt = f"""
You are a professional smart contract auditor with strong expertise in Solidity and blockchain security.

Analyze the following Solidity smart contract and produce a concise, structured markdown report with three sections:
1. **Security Vulnerabilities** (enumerate issues, include SWC IDs if relevant)
2. **Gas Optimization Opportunities**
3. **Code Quality Improvements**

For every issue, include:
- A short description
- Why it matters
- A concrete fix or code snippet (when helpful)

Prefer modern best practices for Solidity ^0.8.x:
- Checks-Effects-Interactions
- `call{{value: ...}}("")` with boolean check (do not recommend `.transfer` as a blanket fix)
- Consider `ReentrancyGuard` from OpenZeppelin where applicable
- Emit events for critical state changes

Smart Contract:
```solidity
{code}
```
"""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content.strip()
    except OpenAIError as e:
        return f"❌ Audit failed: {e}"
    except Exception as e:
        return f"❌ Unexpected error: {e}"


def explain_audit_simple(audit_text: str, audience: str = "beginner",
                         model: str = "gpt-4", temperature: float = 0.3,
                         max_tokens: int = 1200) -> str:
    """
    Rewrite an audit report in simpler language for non-experts.
    Keeps headings/bullets where possible and defines unavoidable terms briefly.
    """
    prompt = f"""
You are a helpful teacher explaining smart contract security to a {audience}.
Rewrite the following audit in clear, simple language:

Guidelines:
- Keep structure (headings / bullets) where it helps readability
- Avoid heavy jargon; define unavoidable terms briefly
- Be concise and friendly

Audit to simplify:
{audit_text}
"""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content.strip()
    except OpenAIError as e:
        return f"Could not generate simple explanation: {e}"
    except Exception as e:
        return f"Unexpected error while simplifying: {e}"
