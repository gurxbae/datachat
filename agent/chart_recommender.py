import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def recommend_chart(question, df):
    """Recommends the best chart type and axes for the results."""
    columns = df.columns.tolist()
    num_cols = df.select_dtypes(include="number").columns.tolist()
    sample = df.head(5).to_string(index=False)
    prompt = f"""You are a data visualization expert. Recommend the best chart for these results.

Question: {question}
Columns: {columns}
Sample data:
{sample}

Return ONLY a JSON object like this:
{{
  "chart_type": "bar",
  "x": "column_name",
  "y": "column_name",
  "color": null,
  "reason": "one sentence explanation"
}}

chart_type must be one of: bar, line, pie, scatter, area
Use null for color if not needed.
No other text, just the JSON.
"""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        import json
        text = message.content[0].text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception:
        return {
            "chart_type": "bar",
            "x": columns[0] if columns else "x",
            "y": num_cols[0] if num_cols else columns[1],
            "color": None,
            "reason": "Default bar chart recommendation"
        }