# Verifly for n8n

[`n8n-nodes-verifly`](https://www.npmjs.com/package/n8n-nodes-verifly) is a
community node that lets any n8n workflow verify email addresses — gate signups
coming in from a webhook, clean a list before a send, or enrich rows in a
spreadsheet.

## Install

In n8n: **Settings → Community Nodes → Install**, enter:

```
n8n-nodes-verifly
```

(Self-hosted alternative: `npm install n8n-nodes-verifly` in your n8n custom
nodes folder, then restart.)

## Credentials

Add a **Verifly API** credential (type `veriflyApi`) and paste your key
(`vf_...`). Get one free:

```bash
curl -X POST https://verifly.email/api/v1/autonomous/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"a-strong-password"}'
```

## The node

One **Verifly** node with three resources:

| Resource | Operations |
|---|---|
| **Email** | **Verify** a single address — returns the verdict, reason, confidence, recommendation and `did_you_mean`. |
| **Bulk Job** | **Submit** a list as an async job, **Get Status**, **Get Results**. |
| **Account** | **Get Profile** (account + remaining credits), **Get Usage** (per day/week/month). |

The most common setup: a Webhook/Trigger → **Verifly: Email → Verify** → an
**IF** node that routes on `recommendation === "safe_to_send"`.

## Sample workflow — gate signups from a webhook

Import [`workflow.json`](workflow.json) (**Workflows → Import from File**) or copy
the JSON below. It:

1. exposes a webhook that accepts `{ "email": "..." }`,
2. verifies the address with Verifly,
3. branches: `safe_to_send` → accept path, anything else → reject path.

Set the **Verifly API** credential on the Verifly node after importing.

```json
{
  "name": "Verifly - gate signup",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "signup",
        "responseMode": "lastNode",
        "options": {}
      },
      "id": "a1",
      "name": "Signup Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [260, 300]
    },
    {
      "parameters": {
        "resource": "email",
        "operation": "verify",
        "email": "={{ $json.body.email }}"
      },
      "id": "b2",
      "name": "Verifly Verify",
      "type": "n8n-nodes-verifly.verifly",
      "typeVersion": 1,
      "position": [520, 300],
      "credentials": {
        "veriflyApi": { "id": "1", "name": "Verifly API" }
      }
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.recommendation }}",
              "operation": "equals",
              "value2": "safe_to_send"
            }
          ]
        }
      },
      "id": "c3",
      "name": "Safe to send?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [780, 300]
    },
    {
      "parameters": {},
      "id": "d4",
      "name": "Accept signup",
      "type": "n8n-nodes-base.noOp",
      "typeVersion": 1,
      "position": [1040, 200]
    },
    {
      "parameters": {},
      "id": "e5",
      "name": "Reject signup",
      "type": "n8n-nodes-base.noOp",
      "typeVersion": 1,
      "position": [1040, 400]
    }
  ],
  "connections": {
    "Signup Webhook": { "main": [[{ "node": "Verifly Verify", "type": "main", "index": 0 }]] },
    "Verifly Verify": { "main": [[{ "node": "Safe to send?", "type": "main", "index": 0 }]] },
    "Safe to send?": {
      "main": [
        [{ "node": "Accept signup", "type": "main", "index": 0 }],
        [{ "node": "Reject signup", "type": "main", "index": 0 }]
      ]
    }
  }
}
```
