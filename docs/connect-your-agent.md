# Connect your AI Agent

The AI SDR needs one MCP server: Evaboot.

## 1. Account

An [Evaboot account](https://dash.evaboot.com/accounts/signup/?last_click_origin=claude-ai-sdr-repo) with credits, and a Sales Navigator seat connected to it.

## 2. Connect the MCP server

**Claude (web and desktop app):** follow [claude-app.md](claude-app.md). The connector URL is `https://mcp.evaboot.com/mcp`.

**Claude Code:** sign in with the same Claude account and the connector is there. Or clone the repo, write `EVABOOT_API_KEY` ([dash.evaboot.com/dash/api/](https://dash.evaboot.com/dash/api/)) into `.env`, and start Claude Code from the repo folder with the key loaded: it reads `.mcp.json`.

```bash
git clone https://github.com/evaboot-labs/claude-ai-sdr
cd claude-ai-sdr
cp .env.example .env
# write your key into .env, then start Claude Code with it:
set -a; source .env; set +a
claude
```

**Codex, Cursor:** add `https://mcp.evaboot.com/mcp` as an HTTP MCP server with the header `Authorization: Bearer <your Evaboot API key>`.

## 3. Check

Ask your AI Agent: "Check my Evaboot quota and whether my Sales Navigator is connected." An answer with your credits and `has_valid_salesnav: true` means you are ready.

Back to the [README](../README.md).
