"""Builds n8n/claude-ai-sdr.json. Run: python3 n8n/build_workflow.py

One prospecting session as an n8n form: paste a Sales Navigator search URL and a lead count, Evaboot exports the
leads with verified emails, a check drops the wrong ones, Claude scores each remaining lead against your ICP and
writes one LinkedIn connection note and one email opening line, and you get the prospect sheet as a CSV file.
Nothing is sent.
"""
import json
import uuid
from pathlib import Path

EVABOOT_MCP = "https://mcp.evaboot.com/mcp"
EVABOOT_CRED = {"httpBearerAuth": {"id": "", "name": "Evaboot MCP (Bearer)"}}
ANTHROPIC_CRED = {"anthropicApi": {"id": "", "name": "Anthropic"}}
MODEL = "claude-sonnet-5-5"

nodes, connections = [], {}


def node(name, type_, version, params, pos, creds=None, **extra):
    n = {"parameters": params, "id": str(uuid.uuid4()), "name": name, "type": type_,
         "typeVersion": version, "position": pos, **extra}
    if creds:
        n["credentials"] = creds
    nodes.append(n)


def link(a, b, kind="main", out=0):
    connections.setdefault(a, {}).setdefault(kind, [])
    while len(connections[a][kind]) <= out:
        connections[a][kind].append([])
    connections[a][kind][out].append({"node": b, "type": kind, "index": 0})


def mcp_call(name, tool, json_expr, pos):
    node(name, "@n8n/n8n-nodes-langchain.mcpClient", 1.1, {
        "endpointUrl": EVABOOT_MCP, "authentication": "bearerAuth",
        "tool": {"__rl": True, "mode": "list", "value": tool, "cachedResultName": tool},
        "inputMode": "json", "jsonInput": json_expr, "options": {"timeout": 120000},
    }, pos, EVABOOT_CRED)


def code(name, js, pos, **extra):
    node(name, "n8n-nodes-base.code", 2, {"jsCode": js}, pos, **extra)


S = "$('Your settings').first().json"

CHECK_JS = r"""
// Rules 1 and 2 of the skill, in code: Evaboot's own filter check, then placeholder companies.
// Everything else (ICP hard rules, fit score) is Claude's job, with the fields it needs.
const num = v => { const n = parseFloat(String(v ?? '').replace(/,/g, '')); return isNaN(n) ? null : n; };
const words = s => String(s || '').split(/\s+/).join(' ').trim();
const all = $json.structuredContent?.result?.prospects || [];
const PLACEHOLDER = /\b(stealth|freelance|self-employed|undisclosed|confidential)\b/i;
return all.map((p, i) => {
  const base = { id: String(i + 1), name: `${p['First Name'] || ''} ${p['Last Name'] || ''}`.trim(),
    title: String(p['Current Job'] || '').trim(), company: p['Company Name'] || '',
    email: p['Email'] || '', email_status: p['Email Status'] || '', linkedin_url: p['Linkedin URL Public'] || '' };
  let drop = '';
  if (String(p['Matches Filters'] || '').toUpperCase() === 'NO') drop = `Matches Filters NO: ${p['No Match Reasons'] || 'no reason given'}`;
  else if (p['Company Type'] === 'Self-Employed' || PLACEHOLDER.test(base.company)) drop = `placeholder company: ${base.company}`;
  if (drop) return { json: { ...base, drop } };
  const y = num(p['Years in Position']) || 0, m = num(p['Months in Position']) || 0;
  return { json: { ...base, drop: '',
    time_in_role: [[y, 'year'], [m, 'month']].filter(([n]) => n).map(([n, u]) => `${n} ${u}${n > 1 ? 's' : ''}`).join(' ') || 'under a month',
    company_headcount: num(p['Company Employee Exact Count']), company_hq: p['Company Headquarters (Full Address)'] || '',
    company_industry: p['Company Industry'] || '', company_description: words(p['Company Description']).slice(0, 400),
    company_specialities: words(p['Company Specialities']).slice(0, 200),
    sales_team: num(p['Sales Team Size']), bd_team: num(p['Business Development Size']),
    company_growth_1y_pct: num(p['Company Employee Growth 1 Year (%)']),
    recent_posts_30d: num(p['Profile Recent Posts (30 Days)']), headline: words(p['Profile Headline']) } };
});
"""

SHEET_JS = r"""
// The prospect sheet: kept leads best fit first, then the dropped ones with their reason.
const leads = $('Check each lead').all().map(i => i.json);
const out = Object.fromEntries(($json.output?.leads || []).map(l => [l.id, l]));
const rows = leads.map(l => {
  const c = out[l.id] || {};
  const drop = l.drop || c.drop || (c.fit >= 2 ? '' : `fit ${c.fit ?? '?'}: ${c.reason || 'not scored'}`);
  const channel = ['safe'].includes(l.email_status) ? 'email + LinkedIn' : l.email_status === 'riskier' ? 'LinkedIn first' : 'LinkedIn only';
  return { status: drop ? 'dropped' : 'kept', fit: drop ? '' : c.fit, name: l.name, title: l.title, company: l.company,
    size: l.company_headcount ?? '', time_in_role: l.time_in_role || '', reason: drop || c.reason || '',
    channel: drop ? '' : channel, email: drop || channel === 'LinkedIn only' ? '' : l.email,
    connection_note: drop ? '' : c.connection_note || '', opening_line: drop || channel === 'LinkedIn only' ? '' : c.opening_line || '',
    linkedin_url: l.linkedin_url };
});
rows.sort((a, b) => (a.status === b.status ? (b.fit || 0) - (a.fit || 0) : a.status === 'kept' ? -1 : 1));
return rows.map(json => ({ json }));
"""

SYSTEM = """You are an SDR. For each lead in the JSON, apply the ICP below: first its hard rules (fail one = drop, with the field and its value), then the fit score from 1 to 3 with a one-line reason that quotes the fields you used.
For every lead scored 2 or 3, write a LinkedIn connection note under 200 characters built on one fact from the lead (no pitch, no link), and a one-sentence email opening line built on a different fact. Follow the offer and tone below.
Use only facts in the JSON and the offer: never invent a customer, a number, a post or a mutual connection.
Return {id, drop} for a dropped lead, or {id, fit, reason, connection_note, opening_line}.

ICP:
"""

node("Prospecting session", "n8n-nodes-base.formTrigger", 2.2, {
    "formTitle": "AI SDR session",
    "formDescription": "Paste a Sales Navigator search URL. Evaboot exports the leads (1 credit each), Claude qualifies them and writes the first touch. Nothing is sent.",
    "formFields": {"values": [
        {"fieldLabel": "Sales Navigator search URL", "requiredField": True},
        {"fieldLabel": "How many leads", "fieldType": "number", "requiredField": True},
    ]},
    "options": {},
}, [0, 0], webhookId=str(uuid.uuid4()))
node("Your settings", "n8n-nodes-base.set", 3.4, {"assignments": {"assignments": [
    {"id": str(uuid.uuid4()), "name": "icp", "type": "string", "value": "PASTE YOUR ICP.md"},
    {"id": str(uuid.uuid4()), "name": "offer", "type": "string", "value": "PASTE YOUR OFFER.md"},
]}, "options": {}}, [220, 0])
mcp_call("Start the export", "export_sn_search_or_list",
         "={{ JSON.stringify({ search_url: $('Prospecting session').first().json['Sales Navigator search URL'], "
         "name: 'AI SDR session ' + $now.toFormat('yyyy-MM-dd HH:mm'), "
         "max_results: Math.min(Number($('Prospecting session').first().json['How many leads']) || 10, 100) }) }}",
         [440, 0])
node("Wait 30 s", "n8n-nodes-base.wait", 1.1, {"amount": 30}, [660, 0], webhookId=str(uuid.uuid4()))
mcp_call("Export status", "get_export",
         "={{ JSON.stringify({ extraction_id: $('Start the export').first().json.structuredContent.result.extraction_id, limit: 0 }) }}",
         [880, 0])
code("Still running?", r"""
// Stop on a failed export, or after 20 minutes, instead of waiting forever.
const s = $json.structuredContent?.result?.status;
if (['FAILED', 'ERROR', 'CANCELLED', 'CANCELED'].includes(s)) throw new Error(`The export ended with status ${s}.`);
if ($runIndex >= 40) throw new Error('The export is still not finished after 20 minutes.');
return $input.all();
""", [1100, 160])
node("Finished?", "n8n-nodes-base.if", 2.2, {"conditions": {
    "options": {"caseSensitive": True, "typeValidation": "loose", "version": 2},
    "conditions": [{"id": str(uuid.uuid4()), "leftValue": "={{ $json.structuredContent.result.status }}",
                    "rightValue": "EXECUTED", "operator": {"type": "string", "operation": "equals"}}],
    "combinator": "and"}, "options": {}}, [1100, 0])
mcp_call("Get the leads", "get_export",
         "={{ JSON.stringify({ extraction_id: $('Start the export').first().json.structuredContent.result.extraction_id }) }}",
         [1320, -120])
code("Check each lead", CHECK_JS, [1540, -120])
node("Leads to qualify", "n8n-nodes-base.filter", 2.2, {"conditions": {
    "options": {"caseSensitive": True, "typeValidation": "loose", "version": 2},
    "conditions": [{"id": str(uuid.uuid4()), "leftValue": "={{ $json.drop }}", "rightValue": "",
                    "operator": {"type": "string", "operation": "empty", "singleValue": True}}],
    "combinator": "and"}, "options": {}}, [1760, -120], alwaysOutputData=True)
node("All leads", "n8n-nodes-base.aggregate", 1, {
    "aggregate": "aggregateAllItemData", "destinationFieldName": "leads", "options": {}}, [1980, -120])
node("Qualify and write", "@n8n/n8n-nodes-langchain.agent", 2.2, {
    "promptType": "define", "text": "={{ JSON.stringify($json.leads.filter(l => l.id)) }}", "hasOutputParser": True,
    "options": {"systemMessage": "=" + SYSTEM + "{{ " + S + ".icp }}\n\nOffer and tone:\n{{ " + S + ".offer }}",
                "maxIterations": 3},
}, [2200, -120], retryOnFail=True, maxTries=3, waitBetweenTries=2000)
node("Claude", "@n8n/n8n-nodes-langchain.lmChatAnthropic", 1.3, {
    "model": {"__rl": True, "mode": "list", "value": MODEL, "cachedResultName": MODEL},
    "options": {"maxTokensToSample": 12000},
}, [2160, 100], ANTHROPIC_CRED)
node("Qualified leads", "@n8n/n8n-nodes-langchain.outputParserStructured", 1.3, {
    "schemaType": "manual",
    "inputSchema": json.dumps({"type": "object", "required": ["leads"], "properties": {"leads": {
        "type": "array", "items": {"type": "object", "required": ["id"], "properties": {
            "id": {"type": "string"}, "drop": {"type": "string"}, "fit": {"type": "integer"},
            "reason": {"type": "string"}, "connection_note": {"type": "string"},
            "opening_line": {"type": "string"}}}}}}, indent=2),
}, [2320, 100])
code("Prospect sheet", SHEET_JS, [2420, -120])
node("CSV file", "n8n-nodes-base.convertToFile", 1.1, {
    "options": {"fileName": "={{ 'prospects-' + $now.toFormat('yyyy-MM-dd') + '.csv' }}"}}, [2640, -120])

for a, b in [("Prospecting session", "Your settings"), ("Your settings", "Start the export"),
             ("Start the export", "Wait 30 s"), ("Wait 30 s", "Export status"), ("Export status", "Finished?"),
             ("Get the leads", "Check each lead"), ("Check each lead", "Leads to qualify"),
             ("Leads to qualify", "All leads"), ("All leads", "Qualify and write"),
             ("Qualify and write", "Prospect sheet"), ("Prospect sheet", "CSV file")]:
    link(a, b)
link("Finished?", "Get the leads", out=0)
link("Finished?", "Still running?", out=1)
link("Still running?", "Wait 30 s")
link("Claude", "Qualify and write", "ai_languageModel")
link("Qualified leads", "Qualify and write", "ai_outputParser")

workflow = {"name": "AI SDR session (Evaboot + Claude)", "nodes": nodes,
            "connections": connections, "settings": {"executionOrder": "v1"}, "pinData": {}}
out = Path(__file__).with_name("claude-ai-sdr.json")
out.write_text(json.dumps(workflow, indent=2, ensure_ascii=False) + "\n")
print(out, len(nodes), "nodes")
