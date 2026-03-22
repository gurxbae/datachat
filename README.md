# DataChat - AI Business Intelligence Dashboard

A full-stack AI-powered business intelligence platform that lets anyone 
upload a dataset, ask questions in plain English, and instantly get 
SQL-generated answers with interactive charts — no coding required.

## Features
- Upload any CSV file
- Automated data cleaning — detects and fixes nulls, duplicates, formatting
- Auto-generated insights and suggested questions on upload
- Natural language to SQL with self-correcting agentic loop (3 retries)
- Interactive Plotly charts with full customization:
  - Chart type: bar, line, pie, scatter, area
  - X axis, Y axis, color grouping controls
  - Color themes: Blue, Green, Coral, Purple, Amber
  - Data labels, gridlines, sort order, top N filter
  - Visible filter toggle to declutter the UI
- Download cleaned CSV, chart as PNG, full session as PDF report
- Query history in sidebar

## Tech Stack
Python, Streamlit, Anthropic Claude API, SQLite, Plotly, 
pandas, FPDF2, python-dotenv

## How to run
1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Add your Anthropic API key to `.env` as `ANTHROPIC_API_KEY=your_key`
4. Run: `streamlit run app.py`
5. Open browser at `http://localhost:8501`
6. Upload any CSV and start asking questions!

## Example Questions
- "What are the top 5 states by total sales?"
- "What is the monthly revenue trend?"
- "Which product category has the highest revenue?"
- "Who are the top 10 customers by sales?"

## Resume Description
Built DataChat — a full-stack AI business intelligence platform featuring 
automated data cleaning, natural language SQL querying with self-correcting 
agentic loops, interactive Tableau-style visualizations with user-controlled 
variables, and PDF report export. Designed as a conversational alternative 
to traditional BI tools for non-technical business users.