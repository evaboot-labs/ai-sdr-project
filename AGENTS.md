# Agent instructions

This repo turns an AI Agent into an SDR for one prospecting session. From a one-sentence audience, it builds a LinkedIn Sales Navigator search with the Evaboot MCP server, exports a small batch of leads with verified emails, checks every lead against the ICP, drops the wrong ones with a reason, and writes one LinkedIn connection note and one email opening line per qualified lead. The user sends everything.

1. Follow the skill in `skills/ai-sdr-project/SKILL.md` step by step.
2. Read `ICP.md` and `OFFER.md`. If either says `Status: EXAMPLE`, ask the user the questions in it and rewrite it.
3. If the Evaboot tools are missing, follow `docs/connect-your-agent.md` with the user. In the Claude app, `docs/claude-app.md`.
4. If the user wants n8n instead, follow `docs/n8n.md` with them one step at a time: you cannot click inside n8n, so say exactly what to do and wait for their confirmation.

Confirm with the user before every export (1 Evaboot credit per lead). Never send a message, an email or a connection request. Never ask for or handle an API key: the user writes it into `.env` or connects the tool in Claude's settings. Never commit `.env` or `data/`: they hold real people's data.
