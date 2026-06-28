# Verifly MCP server

Verifly speaks the [Model Context Protocol](https://modelcontextprotocol.io), so
any MCP-capable client (Claude Desktop, Cursor, Windsurf, Claude Code, your own
agent) can verify email without you writing HTTP code. The agent gets 15 tools
and uses them on its own.

There are two ways to connect: the **hosted** server (recommended — nothing to
install) or a **local** stdio server via `npx`.

## Get a key first

```bash
curl -X POST https://verifly.email/api/v1/autonomous/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"a-strong-password"}'
```

Save the `api_key.key` (`vf_...`). All configs below use it as a Bearer token.

## Option A — hosted server (Streamable-HTTP)

Endpoint: `https://verifly.email/mcp` · Auth: `Authorization: Bearer vf_...`

### Claude Desktop

`claude_desktop_config.json`
(macOS: `~/Library/Application Support/Claude/`, Windows: `%APPDATA%\Claude\`):

```json
{
  "mcpServers": {
    "verifly": {
      "type": "http",
      "url": "https://verifly.email/mcp",
      "headers": { "Authorization": "Bearer vf_your_api_key" }
    }
  }
}
```

### Cursor

`~/.cursor/mcp.json` (or **Settings → MCP → Add**):

```json
{
  "mcpServers": {
    "verifly": {
      "url": "https://verifly.email/mcp",
      "headers": { "Authorization": "Bearer vf_your_api_key" }
    }
  }
}
```

### Windsurf

`~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "verifly": {
      "serverUrl": "https://verifly.email/mcp",
      "headers": { "Authorization": "Bearer vf_your_api_key" }
    }
  }
}
```

### Claude Code (CLI)

```bash
claude mcp add --transport http verifly https://verifly.email/mcp \
  --header "Authorization: Bearer vf_your_api_key"
```

## Option B — local server via npx (stdio)

Installs nothing permanently; runs the published
[`verifly-mcp-server`](https://www.npmjs.com/package/verifly-mcp-server) package.

```json
{
  "mcpServers": {
    "verifly": {
      "command": "npx",
      "args": ["-y", "verifly-mcp-server"],
      "env": { "VERIFLY_API_KEY": "vf_your_api_key" }
    }
  }
}
```

## The 15 tools

| Tool | What it does |
|---|---|
| `verify_email` | Verify a single address in real time. |
| `verify_batch` | Verify a list synchronously (up to a few hundred). |
| `submit_bulk` | Submit a large list as an async job. |
| `get_job_status` | Check a bulk job's progress. |
| `get_job_results` | Fetch results of a completed bulk job. |
| `list_jobs` | List your bulk jobs. |
| `clean_email_list` | Dedupe + drop invalid/disposable/role addresses. |
| `extract_emails` | Pull every email address out of free-form text. |
| `check_domain_health` | MX / SPF / DMARC + overall domain health score. |
| `get_credits` | Remaining credits (costs nothing). |
| `get_usage` | Detailed usage statistics. |
| `get_account` | Account information. |
| `get_packages` | List buyable credit packages. |
| `buy_credits` | Get a payment link for more credits. |
| `register_account` | Self-register a new account + API key. |

## Try it

In your MCP client, ask:

> Verify `test@gmial.com` with Verifly and tell me whether it's safe to send.

The agent calls `verify_email` and reports back `undeliverable`, with the
`did_you_mean` suggestion `test@gmail.com`.

### Quick raw check (no client)

```bash
curl -s -X POST https://verifly.email/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer vf_your_api_key" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```
