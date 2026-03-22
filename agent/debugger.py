import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def debug_sql(question, schema, broken_sql, error):
    """Fixes a broken SQL query."""
    prompt = f"""You are an expert SQL debugger. Fix this broken SQL query.

Schema:
{schema}

Question: {question}

Broken SQL:
{broken_sql}

Error:
{error}

Rules:
- Return ONLY the fixed SQL query, nothing else
- No markdown, no backticks, no explanations
- Table name is always 'data'
- For date columns stored as text MM/DD/YYYY, use substr(col, 7, 4) for year
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()

def validate_results(question, sql, results_str):
    """Validates if results correctly answer the question."""
    prompt = f"""You are a SQL analyst. Check if these results correctly answer the question.

Question: {question}
SQL: {sql}
Results: {results_str}

Does the result look correct and complete?
- If key columns have empty/null values that's WRONG
- If only 1 row returned when multiple expected that may be WRONG

Reply EXACTLY in this format:
VALID: yes or no
ISSUE: describe problem or none
FIX: corrected SQL or none
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    response = message.content[0].text.strip()
    is_valid, issue, fix = True, "none", "none"
    for line in response.split("\n"):
        if line.startswith("VALID:"):
            is_valid = "yes" in line.lower()
        elif line.startswith("ISSUE:"):
            issue = line.replace("ISSUE:", "").strip()
        elif line.startswith("FIX:"):
            fix = line.replace("FIX:", "").strip()
    return is_valid, issue, fix