# Set it up in the Claude app

The AI SDR runs in a Claude Project on claude.ai or the Claude desktop app. No terminal, no code. You set it up once, then each chat is one prospecting session.

## 1. Connect Evaboot

*Customize > Connectors > Add custom connector*: name `Evaboot`, URL `https://mcp.evaboot.com/mcp`. Click **Connect**, sign in to Evaboot and approve. On a Team or Enterprise plan, an owner adds the connector first.

## 2. Add the skill

1. Download this repo (*Code > Download ZIP*) and unzip it.
2. Zip the `skills/claude-ai-sdr` folder on its own (`claude-ai-sdr.zip`, with `SKILL.md` inside the `claude-ai-sdr` folder).
3. *Customize > Skills > Upload a skill*, pick the zip, and turn the skill on.

## 3. Create the project

1. *Projects > New project*, name it `AI SDR`.
2. **Instructions**: paste the text from [project/instructions.md](../project/instructions.md).
3. **Files**: add `ICP.md` and `OFFER.md` from the repo. Fill them in first, or let Claude ask you the questions in the first chat.

## 4. Run a session

Start a chat inside the project and write who to reach, for example:

```text
Find 10 Heads of Sales in the UK who changed jobs in the past 90 days, qualify them and prepare the first touch.
```

Claude checks your Evaboot quota, builds the Sales Navigator search, asks before the export, then gives you the prospect sheet: a table, the dropped leads with a reason each, and a CSV file.

## Good to know

- One exported lead costs 1 Evaboot credit, email included. The search itself is free.
- Claude never sends anything. You send each connection note and email yourself.
- To run the same search every day, use [daily-lead-pipeline](https://github.com/evaboot-labs/daily-lead-pipeline) instead.

Back to the [README](../README.md).
