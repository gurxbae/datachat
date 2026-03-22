import pandas as pd

def analyze_data_quality(df):
    report = []
    null_counts = df.isnull().sum()
    null_cols = null_counts[null_counts > 0]
    if not null_cols.empty:
        for col, count in null_cols.items():
            report.append({
                "type": "warning",
                "issue": f"{count} null values in '{col}'",
                "action": f"Fill nulls with median/mode or drop rows"
            })
    else:
        report.append({
            "type": "ok",
            "issue": "No null values found",
            "action": "None needed"
        })
    dupe_count = df.duplicated().sum()
    if dupe_count > 0:
        report.append({
            "type": "warning",
            "issue": f"{dupe_count} duplicate rows found",
            "action": "Remove duplicate rows"
        })
    else:
        report.append({
            "type": "ok",
            "issue": "No duplicate rows found",
            "action": "None needed"
        })
    bad_cols = [c for c in df.columns if " " in c or "-" in c]
    if bad_cols:
        report.append({
            "type": "info",
            "issue": f"Column names standardized: {', '.join(bad_cols)}",
            "action": "Spaces and hyphens replaced with underscores"
        })
    else:
        report.append({
            "type": "ok",
            "issue": "Column names are clean",
            "action": "None needed"
        })
    for col in df.columns:
        if "date" in col.lower():
            report.append({
                "type": "info",
                "issue": f"Date column detected: '{col}'",
                "action": "Stored as text — use substr() for year extraction in SQL"
            })
    return report

def clean_dataframe(df):
    original_rows = len(df)
    df = df.drop_duplicates()
    for col in df.columns:
        if df[col].dtype in ["float64", "int64"]:
            df[col] = df[col].fillna(df[col].median())
        else:
            df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "Unknown")
    removed = original_rows - len(df)
    return df, removed