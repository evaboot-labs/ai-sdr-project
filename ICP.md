# Ideal customer profile

Status: EXAMPLE

Replace this example with your own. Your AI Agent asks you these questions when the status is EXAMPLE:
who buys, which companies, what disqualifies a lead, and what makes one a strong fit.

## Who

- Sales leaders: Head of Sales, VP Sales, Sales Director, Commercial Director, Director of Business Development.
- Signal: started the role in the past 90 days.

## Hard rules (fail one = drop)

- Company HQ in the United Kingdom (`Company Headquarters (Full Address)`).
- 10 to 500 employees (`Company Employee Exact Count`).
- Not staffing and recruiting, not sports clubs, not self-employed.

## Fit score

- **3**: B2B company with a sales or business development team of 3 or more (`Sales Team Size`, `Business Development Size`) and the person in role for 6 months or less.
- **2**: passes the hard rules, but one fit fact is missing or unclear (no team size, a services firm that may be a partner rather than a buyer).
- **1**: passes the hard rules, nothing else fits. Not contacted.
