# Web3 Support Workflow Lab

This extension is the personal implementation layer around the upstream Dify
checkout. It is deliberately read-only: it never handles private keys, signs
transactions, places orders, or gives investment advice.

## Scope

- explicit intent routing: `product_info`, `risk_notice`, `security_refusal`, `human_handoff`;
- query normalization before retrieval/tool selection;
- two deterministic read-only tools exposed through an OpenAPI contract;
- replayable cases and fixed mock responses for workflow contract tests;
- failure categories for invalid tool input, tool failure, timeout, and policy violation.

The `tool_server` uses only the Python standard library so the contract tests
can run before Docker or a model provider is available. Dify can import
`tool_server/openapi.yaml` after the local service is started.

## Run the local contract tests

```bash
python3 -m unittest discover -s tests -v
```

## Start the mock tool service

```bash
python3 tool_server/server.py
```

The service listens on `127.0.0.1:8787`. It implements:

- `GET /product-status?product=...`
- `GET /risk-notice?topic=...`
- `GET /healthz`

## Test DeepSeek without saving the key

After revoking any key that was exposed in chat and creating a new one, run:

```bash
python3 test_deepseek.py
```

The key is entered through a hidden prompt and is not written to this
checkout, `.env`, shell history, or test output. The test uses
`https://api.deepseek.com` and `deepseek-v4-flash`.

## Dify integration after Docker is available

1. Import `tool_server/openapi.yaml` as a custom tool.
2. Build the workflow described in `workflow-contract.md`.
3. Run the same JSONL cases through Dify's workflow API.
4. Compare Dify run events with the local contract-test results.

No production claim is made until the Dify workflow and the end-to-end replay
have been executed and recorded.
