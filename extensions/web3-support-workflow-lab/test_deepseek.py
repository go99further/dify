#!/usr/bin/env python3
"""One-shot DeepSeek connectivity test without persisting the API key."""

import getpass
import json
import os
import sys
import urllib.error
import urllib.request


def main() -> int:
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not key:
        key = getpass.getpass("DeepSeek API key (input hidden): ").strip()
    if not key:
        print("No API key entered.", file=sys.stderr)
        return 2

    payload = json.dumps(
        {
            "model": "deepseek-v4-flash",
            "messages": [{"role": "user", "content": "Reply with exactly: DEEPSEEK_OK"}],
            "stream": False,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        # Do not print response bodies: providers may echo sensitive request data.
        print(f"DeepSeek HTTP error: {exc.code}", file=sys.stderr)
        return 1
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"DeepSeek connection error: {exc.reason if hasattr(exc, 'reason') else exc}", file=sys.stderr)
        return 1

    choices = result.get("choices") or []
    message = choices[0].get("message", {}) if choices else {}
    print(f"DeepSeek OK: model={result.get('model', 'unknown')}")
    print(f"Response: {message.get('content', '').strip()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
