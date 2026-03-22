import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def generate_auto_insights(df, schema):
    """Generates 3 automatic insights from the dataset."""
    sample = df.head(50).to_string(index=False)
    prompt = f"""You are a business analyst. Analyze this dataset and generate exactly 3 interesting insights.

Schema:
{schema}

Sample data:
{sample}

Rules:
- Return exactly 3 insights
- Each insight must be specific with numbers
- Format as a Python list of strings like:
["insight 1", "insight 2", "insight 3"]
- No other text, just the list
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        import ast
        return ast.literal_eval(message.content[0].text.strip())
    except Exception:
        return [
            "Upload your data to see auto-generated insights",
            "Insights will be specific to your dataset",
            "Ask questions below to explore your data"
        ]

def generate_suggested_questions(schema):
    """Generates 5 suggested questions based on the schema."""
    prompt = f"""You are a business analyst. Given this database schema, suggest 5 useful business questions.

Schema:
{schema}

Rules:
- Return exactly 5 questions
- Make them specific to the columns available
- Format as a Python list of strings like:
["question 1", "question 2", "question 3", "question 4", "question 5"]
- No other text, just the list
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        import ast
        return ast.literal_eval(message.content[0].text.strip())
    except Exception:
        return [
            "What is the total revenue by category?",
            "Who are the top 10 customers?",
            "What is the monthly sales trend?",
            "Which region has the highest sales?",
            "What is the average order value?"
        ]