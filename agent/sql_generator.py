import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def generate_sql(question, schema):
    """Generates SQL from a plain English question."""
    prompt = f"""You are an expert SQL analyst. Generate a SQL query for this question.

Schema:
{schema}

Question: {question}

Rules:
- Return ONLY the SQL query, nothing else
- No markdown, no backticks, no explanations
- Use only columns defined in the schema
- Table name is always 'data'
- For date columns stored as text MM/DD/YYYY, use substr(col, 7, 4) for year
- Keep queries efficient and correct
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()