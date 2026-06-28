# Verifly Examples

Runnable, real examples for [**Verifly**](https://verifly.email) — agent-native email verification.

[![PyPI](https://img.shields.io/pypi/v/verifly-email?label=pypi%20verifly-email)](https://pypi.org/project/verifly-email/)
[![npm](https://img.shields.io/npm/v/verifly-email?label=npm%20verifly-email)](https://www.npmjs.com/package/verifly-email)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Verifly tells you whether an email address is real **before** you send to it or
let someone sign up with it. Every endpoint returns a clear verdict
(`deliverable` / `undeliverable` / `risky` / `unknown`), the reason, a
confidence score, a `did_you_mean` correction for typos, and a
`safe_to_send` / `do_not_send` recommendation.

It is built for **AI agents and automation**, not just dashboards: an agent can
self-register its own key (100 free credits, no captcha, no card), call the
REST API, use the official Python/Node SDKs, or connect to the hosted
**MCP server** and get 15 tools. Drop-in integrations exist for LangChain,
LlamaIndex, and n8n.

## What you'd use it for

- **Stop fake signups in an agent loop** — verify the address before creating the
  account; reject anything that isn't `safe_to_send`.
- **Clean a lead list before a campaign** — drop typos, dead domains, and
  disposable addresses so you don't burn sender reputation on bounces.
- **Fix typos at the point of entry** — `test@gmial.com` comes back with
  `did_you_mean: test@gmail.com`.
- **Give an LLM agent a verification tool** — so it can decide, on its own,
  whether an address is worth emailing.

## 30-second quickstart

**1. Get a free API key** (an agent can do this itself — no human, no captcha):

```bash
curl -X POST https://verifly.email/api/v1/autonomous/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"a-strong-password"}'
```

Response (the `api_key.key` is shown exactly once — save it):

```json
{
  "success": true,
  "account": { "email": "you@example.com", "credits": 100 },
  "api_key": { "key": "vf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" }
}
```

**2. Verify an address** with one HTTP call:

```bash
export VERIFLY_API_KEY=vf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

curl "https://verifly.email/api/v1/verify?email=test@gmial.com" \
  -H "Authorization: Bearer $VERIFLY_API_KEY"
```

Real JSON response:

```json
{
  "success": true,
  "email": "test@gmial.com",
  "result": "undeliverable",
  "reason": "Invalid email: bad_domain",
  "confidence": 90,
  "recommendation": "do_not_send",
  "did_you_mean": "test@gmail.com",
  "details": {
    "syntax_valid": true,
    "domain_exists": true,
    "mx_records": true,
    "smtp_valid": false,
    "is_disposable": false,
    "is_role_account": true,
    "is_catch_all": false,
    "is_free_provider": false,
    "provider": "gmial.com"
  },
  "credits": { "used": 1, "remaining": 99 }
}
```

That's the whole product: send an address, get a decision back.

## Examples index

Every file below was run against the live API; observed output is pasted in
comments. All read the key from the `VERIFLY_API_KEY` environment variable —
no keys are committed.

| Example | What it shows |
|---|---|
| [`python/raw_api.py`](python/raw_api.py) | Single + async bulk verify with only `requests`. |
| [`python/sdk_example.py`](python/sdk_example.py) | The [`verifly-email`](https://pypi.org/project/verifly-email/) PyPI SDK: verify, batch, signup gate. |
| [`python/langchain_agent.py`](python/langchain_agent.py) | [`langchain-verifly`](https://pypi.org/project/langchain-verifly/) `VeriflyEmailVerifier` tool in a tool-calling LLM loop. |
| [`python/llamaindex_tool.py`](python/llamaindex_tool.py) | [`llama-index-tools-verifly`](https://pypi.org/project/llama-index-tools-verifly/) `VeriflyToolSpec` for a LlamaIndex agent. |
| [`node/raw_api.js`](node/raw_api.js) | Single verify with built-in `fetch` (Node 18+). |
| [`node/sdk_example.js`](node/sdk_example.js) | The [`verifly-email`](https://www.npmjs.com/package/verifly-email) npm SDK. |
| [`mcp/README.md`](mcp/README.md) | Add the hosted MCP server to Claude Desktop / Cursor / Windsurf (15 tools). |
| [`n8n/README.md`](n8n/README.md) | The [`n8n-nodes-verifly`](https://www.npmjs.com/package/n8n-nodes-verifly) community node + a sample workflow. |

### Run the Python examples

```bash
pip install -r requirements.txt
export VERIFLY_API_KEY=vf_...
python python/raw_api.py
```

### Run the Node examples

```bash
cd node && npm install
export VERIFLY_API_KEY=vf_...
node raw_api.js
```

## API reference

- Base URL: `https://verifly.email`
- Single verify: `GET /api/v1/verify?email=...` (header `Authorization: Bearer <KEY>`)
- Batch verify (sync): `POST /api/v1/verify/batch` — `{"emails": [...]}`
- Bulk verify (async): `POST /api/v1/verify/bulk` → poll `GET /api/v1/jobs/{id}` → `GET /api/v1/jobs/{id}/results`
- Self-register: `POST /api/v1/autonomous/register` — `{"email","password"}`
- Credits / usage / account: `GET /api/v1/credits`, `/usage`, `/account`
- Full OpenAPI spec: [`https://verifly.email/openapi.json`](https://verifly.email/openapi.json)
- Hosted MCP: [`https://verifly.email/mcp`](https://verifly.email/mcp) (Streamable-HTTP, Bearer auth, 15 tools)

## License

MIT — see [LICENSE](LICENSE).
