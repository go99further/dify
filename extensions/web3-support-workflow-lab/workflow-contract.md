# Workflow Contract

The Dify workflow must preserve these boundaries when it is imported:

1. Normalize the query before routing.
2. Route security-sensitive requests before retrieval or tool calls.
3. Route product requests to `get_product_status` only after schema validation.
4. Route risk requests to `get_risk_notice` and return the source notice.
5. Route investment requests and ambiguous requests to human handoff.
6. Treat tool errors and timeouts as explicit outcomes, never as fabricated answers.
7. Preserve a run correlation id across API, worker, node, and tool events.

The JSONL cases are the contract. Any Dify workflow change must replay the
same cases and report the expected/actual outcome pair.
