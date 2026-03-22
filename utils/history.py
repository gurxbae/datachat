import streamlit as st

def init_history():
    """Initializes query history in session state."""
    if "history" not in st.session_state:
        st.session_state.history = []

def add_to_history(question, sql, df):
    """Adds a query result to history."""
    st.session_state.history.append({
        "question": question,
        "sql": sql,
        "df": df
    })

def get_history():
    """Returns full query history."""
    return st.session_state.get("history", [])

def clear_history():
    """Clears query history."""
    st.session_state.history = []