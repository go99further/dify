"""Deterministic workflow contract used before a real Dify API run."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).parent
CASES = [json.loads(line) for line in (ROOT / "cases.jsonl").read_text().splitlines()]
MOCKS = json.loads((ROOT / "mock_llm_responses.json").read_text())


def rewrite(query: str) -> str:
    normalized = re.sub(r"\s+", " ", query.strip().lower())
    if normalized == "wallet?":
        return "wallet product status"
    return normalized


def route(query: str) -> str:
    text = rewrite(query)
    if any(token in text for token in ("private key", "seed phrase", "system prompt", "ignore all")):
        return "security_refusal"
    if any(token in text for token in ("phishing", "dm", "link")):
        return "risk_notice"
    if any(token in text for token in ("go up", "price", "invest", "token")):
        return "human_handoff"
    if any(token in text for token in ("wallet", "stablecoin", "product")):
        return "product_info"
    return "human_handoff"


def execute(case: dict) -> dict:
    intent = route(case["query"])
    if intent not in MOCKS:
        return {"intent": intent, "outcome": "handoff"}
    if intent == "security_refusal":
        text = rewrite(case["query"])
        outcome = "refuse_private_key" if any(token in text for token in ("private key", "seed phrase")) else "refuse_policy"
        return {"intent": intent, "outcome": outcome}
    if intent == "human_handoff":
        text = rewrite(case["query"])
        outcome = "no_investment_advice" if any(token in text for token in ("go up", "price", "invest", "token")) else "handoff"
        return {"intent": intent, "outcome": outcome}
    text = rewrite(case["query"])
    if "timeout" in text:
        return {"intent": intent, "outcome": "tool_timeout", "error": "TIMEOUT"}
    if intent == "risk_notice":
        return {"intent": intent, "outcome": "tool_risk_notice"}
    if "unknown-product" in text:
        return {"intent": intent, "outcome": "tool_product_not_found", "error": "PRODUCT_NOT_FOUND"}
    return {"intent": intent, "outcome": "rewrite_then_tool" if text == "wallet product status" else "tool_product_status"}
