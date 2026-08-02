#!/usr/bin/env python3
"""Deterministic, read-only tool server for Dify workflow integration tests."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


PRODUCTS = {
    "wallet": {
        "name": "wallet",
        "status": "read-only-demo",
        "source": "local-fixture",
        "notice": "Never share a seed phrase or private key.",
    },
    "stablecoin": {
        "name": "stablecoin",
        "status": "read-only-demo",
        "source": "local-fixture",
        "notice": "Verify the official contract address before using a token.",
    },
}

RISKS = {
    "phishing": "Do not open unsolicited links or connect a wallet from a DM.",
    "private_key": "Support will never request a private key or seed phrase.",
    "investment": "This service does not provide investment advice.",
}


def response_payload(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class ToolHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        if parsed.path == "/healthz":
            response_payload(self, 200, {"ok": True})
            return
        if parsed.path == "/product-status":
            product = query.get("product", [""])[0].strip().lower()
            if product not in PRODUCTS:
                response_payload(self, 404, {"error": "PRODUCT_NOT_FOUND"})
                return
            response_payload(self, 200, PRODUCTS[product])
            return
        if parsed.path == "/risk-notice":
            topic = query.get("topic", [""])[0].strip().lower()
            if topic not in RISKS:
                response_payload(self, 400, {"error": "RISK_TOPIC_REQUIRED"})
                return
            response_payload(self, 200, {"topic": topic, "notice": RISKS[topic]})
            return
        response_payload(self, 404, {"error": "NOT_FOUND"})

    def log_message(self, format: str, *args: object) -> None:
        return


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8787), ToolHandler)
    print("web3 support tool server listening on http://127.0.0.1:8787")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
