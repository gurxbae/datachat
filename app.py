from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sqlite3

from core.db_manager import load_csv, get_schema, db_exists
from core.query_executor import run_query
from core.exporter import export_session_pdf
from agent.cleaner import analyze_data_quality, clean_dataframe
from agent.sql_generator import generate_sql
from agent.debugger import debug_sql, validate_results
from agent.insights import generate_auto_insights, generate_suggested_questions
from agent.chart_recommender import recommend_chart
from utils.history import init_history, add_to_history, get_history, clear_history

st.set_page_config(
    page_title="DataChat",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
.block-container{padding-top:1.5rem;}
.stTabs [data-baseweb="tab"]{font-size:13px;}
div[data-testid="metric-container"]{background:var(--background-color);border:1px solid rgba(128,128,128,0.2);border-radius:8px;padding:12px;}
</style>
""", unsafe_allow_html=True)

init_history()

# Sidebar
with st.sidebar:
    st.markdown("## 📊 DataChat")
    st.caption("AI Business Intelligence")
    st.divider()

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file:
        st.success(f"Loaded: {uploaded_file.name}")

    st.divider()

    history = get_history()
    if history:
        st.markdown("**Query history**")
        for i, item in enumerate(reversed(history)):
            st.caption(f"Q{len(history)-i}: {item['question'][:40]}...")
        st.divider()
        if st.button("Clear history"):
            clear_history()
            st.rerun()

        if st.button("Export PDF report"):
            with st.spinner("Generating PDF..."):
                path = export_session_pdf(get_history())
                with open(path, "rb") as f:
                    st.download_button(
                        "Download PDF",
                        data=f,
                        file_name="datachat_report.pdf",
                        mime="application/pdf"
                    )
    else:
        st.caption("No queries yet")

# Main area
st.markdown("# 📊 DataChat")
st.caption("Ask any business question about your data in plain English")
st.divider()

if uploaded_file is None:
    st.info("Upload a CSV file in the sidebar to get started.")
    st.stop()

# Load and clean data
if "df_clean" not in st.session_state or st.session_state.get("last_file") != uploaded_file.name:
    with st.spinner("Loading and analyzing your data..."):
        uploaded_file.seek(0)
        df_raw = pd.read_csv(uploaded_file, encoding="latin-1")
        df_raw.columns = (df_raw.columns.str.strip().str.lower()
                         .str.replace(" ", "_").str.replace("-", "_")
                         .str.replace("/", "_"))

        report = analyze_data_quality(df_raw)
        df_clean, removed = clean_dataframe(df_raw.copy())

        conn = sqlite3.connect("datachat.db")
        df_clean.to_sql("data", conn, if_exists="replace", index=False)
        conn.close()

        schema = get_schema()
        insights = generate_auto_insights(df_clean, schema)
        suggestions = generate_suggested_questions(schema)

        st.session_state.df_clean = df_clean
        st.session_state.report = report
        st.session_state.removed = removed
        st.session_state.schema = schema
        st.session_state.insights = insights
        st.session_state.suggestions = suggestions
        st.session_state.last_file = uploaded_file.name

df = st.session_state.df_clean
schema = st.session_state.schema
report = st.session_state.report
insights = st.session_state.insights
suggestions = st.session_state.suggestions

# Section 1 - Data Overview
with st.expander("Data overview & cleaning report", expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total rows", f"{len(df):,}")
    col2.metric("Columns", len(df.columns))
    col3.metric("Duplicates removed", st.session_state.removed)
    col4.metric("File", uploaded_file.name)

    st.divider()

    st.markdown("**Cleaning report**")
    for item in report:
        if item["type"] == "ok":
            st.success(item["issue"])
        elif item["type"] == "warning":
            st.warning(f"{item['issue']} -> {item['action']}")
        elif item["type"] == "info":
            st.info(item["issue"])

    st.divider()

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download cleaned CSV",
        data=csv_bytes,
        file_name="cleaned_data.csv",
        mime="text/csv"
    )

    st.markdown("**Data preview**")
    st.dataframe(df.head(10), use_container_width=True)

# Section 2 - Auto Insights
with st.expander("Auto insights", expanded=True):
    for insight in insights:
        st.markdown(f"- {insight}")

    st.divider()
    st.markdown("**Suggested questions**")
    cols = st.columns(3)
    for i, q in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(q, key=f"sug_{i}", use_container_width=True):
                st.session_state.auto_question = q
                st.rerun()

# Section 3 - Question Input
st.divider()
st.markdown("### Ask a question")

if "auto_question" in st.session_state:
    st.session_state.question_input = st.session_state.auto_question
    del st.session_state.auto_question

with st.form(key="question_form"):
    question = st.text_input(
        "Your question",
        placeholder="e.g. What are the top 5 states by total sales?",
        label_visibility="collapsed",
        key="question_input"
    )
    run_btn = st.form_submit_button("Run", type="primary")

# Section 4 - Run query
if run_btn and question.strip():
    with st.spinner("Generating SQL and running query..."):

        sql = generate_sql(question, schema)
        success = False
        attempts = 0
        MAX_RETRIES = 3
        result_df = None

        while not success and attempts < MAX_RETRIES:
            attempts += 1
            ok, data = run_query(sql)

            if ok:
                results_str = data.head(20).to_string(index=False)
                is_valid, issue, fix = validate_results(question, sql, results_str)

                if is_valid:
                    success = True
                    result_df = data
                else:
                    if fix != "none" and attempts < MAX_RETRIES:
                        sql = fix
                    else:
                        success = True
                        result_df = data
            else:
                if attempts < MAX_RETRIES:
                    sql = debug_sql(question, schema, sql, data)
                else:
                    st.error(f"Could not execute query after {MAX_RETRIES} attempts.")
                    st.stop()

        if result_df is not None:
            add_to_history(question, sql, result_df)
            st.session_state.last_result_df = result_df
            st.session_state.last_question = question
            st.session_state.last_sql = sql

# Section 5 - Display results
if "last_result_df" in st.session_state:
    result_df = st.session_state.last_result_df
    question = st.session_state.last_question
    sql = st.session_state.last_sql

if "last_result_df" in st.session_state and st.session_state.last_result_df is not None:
    result_df = st.session_state.last_result_df

    if not result_df.empty:
        st.divider()

        # PDF export
        col_exp1, col_exp2 = st.columns([1, 4])
        with col_exp1:
            if st.button("Export session as PDF", use_container_width=True):
                with st.spinner("Generating PDF..."):
                    path = export_session_pdf(get_history())
                    with open(path, "rb") as f:
                        st.download_button(
                            "Download PDF",
                            data=f,
                            file_name="datachat_report.pdf",
                            mime="application/pdf",
                            key="inline_pdf"
                        )

        st.divider()

        tab1, tab2, tab3 = st.tabs(["Results table", "SQL query", "Chart"])

        with tab1:
            st.dataframe(result_df, use_container_width=True)
            csv = result_df.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", csv, "results.csv", "text/csv")

        with tab2:
            st.code(st.session_state.last_sql, language="sql")

        with tab3:
            rec = recommend_chart(st.session_state.last_question, result_df)
            st.caption(f"AI recommendation: {rec.get('reason', '')}")

            cols = result_df.columns.tolist()
            num_cols = result_df.select_dtypes(include="number").columns.tolist()

            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                chart_type = st.selectbox("Chart type",
                    ["bar", "line", "pie", "scatter", "area"],
                    index=["bar","line","pie","scatter","area"].index(
                        rec.get("chart_type", "bar")))
            with c2:
                x_col = st.selectbox("X axis", cols,
                    index=cols.index(rec.get("x", cols[0]))
                    if rec.get("x") in cols else 0)
            with c3:
                y_col = st.selectbox("Y axis",
                    num_cols if num_cols else cols, index=0)
            with c4:
                color_col = st.selectbox("Color by", ["None"] + cols)
                color_col = None if color_col == "None" else color_col
            with c5:
                theme = st.selectbox("Theme",
                    ["Blue", "Green", "Coral", "Purple", "Amber"])

            themes = {
                "Blue": px.colors.sequential.Blues_r,
                "Green": px.colors.sequential.Greens_r,
                "Coral": px.colors.sequential.Oranges_r,
                "Purple": px.colors.sequential.Purples_r,
                "Amber": px.colors.sequential.YlOrBr_r
            }

            with st.expander("Advanced customization"):
                ac1, ac2, ac3 = st.columns(3)
                with ac1:
                    show_labels = st.checkbox("Data labels", value=True)
                    show_grid = st.checkbox("Gridlines", value=True)
                with ac2:
                    sort_order = st.selectbox("Sort",
                        ["Descending", "Ascending", "None"])
                    top_n = st.selectbox("Show top", [5, 10, 20, 50, "All"])
                with ac3:
                    x_label = st.text_input("X axis label", value=x_col)
                    y_label = st.text_input("Y axis label", value=y_col)

                st.markdown("**Visible filters**")
                str_cols = result_df.select_dtypes(exclude="number").columns.tolist()
                filter_cols = st.multiselect(
                    "Select filters to show",
                    cols,
                    default=str_cols[:2] if str_cols else []
                )

            # Apply top N and sort
            plot_df = result_df.copy()
            if top_n != "All":
                plot_df = plot_df.head(int(top_n))
            if sort_order == "Descending" and y_col in plot_df.columns:
                plot_df = plot_df.sort_values(y_col, ascending=False)
            elif sort_order == "Ascending" and y_col in plot_df.columns:
                plot_df = plot_df.sort_values(y_col, ascending=True)

            # Apply filters
            for fc in filter_cols:
                unique_vals = result_df[fc].dropna().unique().tolist()
                selected = st.multiselect(
                    f"Filter: {fc}", unique_vals,
                    default=unique_vals, key=f"f_{fc}")
                plot_df = plot_df[plot_df[fc].isin(selected)]

            # Generate chart
            color_seq = themes[theme]
            fig = None

            if chart_type == "bar":
                fig = px.bar(plot_df, x=x_col, y=y_col, color=color_col,
                             color_discrete_sequence=color_seq,
                             text_auto=show_labels,
                             labels={x_col: x_label, y_col: y_label})
            elif chart_type == "line":
                fig = px.line(plot_df, x=x_col, y=y_col, color=color_col,
                              color_discrete_sequence=color_seq,
                              labels={x_col: x_label, y_col: y_label},
                              markers=True)
            elif chart_type == "pie":
                fig = px.pie(plot_df, names=x_col, values=y_col,
                             color_discrete_sequence=color_seq)
            elif chart_type == "scatter":
                fig = px.scatter(plot_df, x=x_col, y=y_col, color=color_col,
                                 color_discrete_sequence=color_seq,
                                 labels={x_col: x_label, y_col: y_label})
            elif chart_type == "area":
                fig = px.area(plot_df, x=x_col, y=y_col, color=color_col,
                              color_discrete_sequence=color_seq,
                              labels={x_col: x_label, y_col: y_label})

            if fig:
                fig.update_layout(
                    showlegend=True,
                    xaxis_showgrid=show_grid,
                    yaxis_showgrid=show_grid,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(t=30, b=30, l=20, r=20)
                )
                st.plotly_chart(fig, use_container_width=True)

                try:
                    st.download_button(
                        "Download chart as PNG",
                        data=fig.to_image(format="png"),
                        file_name="chart.png",
                        mime="image/png"
                    )
                except Exception:
                    st.caption("Install kaleido to enable PNG export: pip install kaleido")

    else:
        st.warning("Query returned no results. Try rephrasing your question.")