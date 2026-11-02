# Run it in n8n

[`n8n/ai-sdr-project.json`](../n8n/ai-sdr-project.json) is the same session as an n8n form, when you prefer n8n to a chat. You paste a Sales Navigator search URL and a lead count; you get the prospect sheet as a CSV file.

## What runs

1. **Prospecting session** (Form): the Sales Navigator search URL and how many leads (up to 100).
2. **Your settings** (Set): your `ICP.md` and `OFFER.md`, pasted as text.
3. **Start the export**, **Wait 30 s**, **Export status**, **Finished?**, **Still running?** (Evaboot MCP + Code): exports the leads and waits until the export is done. It stops with an error if the export fails or takes over 20 minutes.
4. **Get the leads** and **Check each lead** (Evaboot MCP + Code): drops leads that fail Evaboot's filter check or work at a placeholder company.
5. **Qualify and write** (AI Agent with Claude): applies your ICP, scores each lead from 1 to 3 with a reason, and writes the connection note and the opening line.
6. **Prospect sheet** and **CSV file**: kept leads best fit first, then the dropped ones with their reason.

## Set it up

1. **Import** the JSON: *Workflows > Import from file*.
2. **Add two credentials:**
   - **Bearer Auth** named `Evaboot MCP (Bearer)`: your key from [dash.evaboot.com/dash/api/](https://dash.evaboot.com/dash/api/). Select it on the four Evaboot nodes.
   - **Anthropic** on the **Claude** node.
3. **Fill in Your settings** with your ICP and your offer.
4. **Get the search URL**: build the search in Sales Navigator (or ask Claude with the Evaboot connector), and copy the URL.
5. **Test**: publish the workflow, open the form URL from **Prospecting session**, paste the URL and 5 leads. Open the execution and download the CSV from **CSV file**.

## Good to know

- Each exported lead costs 1 Evaboot credit, email included.
- Nothing is sent. You send each note and email yourself.

Back to the [README](../README.md).
