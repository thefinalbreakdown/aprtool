import streamlit as st
import pandas as pd
import io
from datetime import datetime, timedelta

st.title("📈 Isolated Funding Rate APR Viewer")

st.markdown("""
Upload a single funding file (Bybit or WOOX).

- App will calculate APR per entry.
- You can manually adjust the funding interval (e.g., 4 hours).
- Select timeframe (30, 14, 7, 3, or 1 day).
- Chart and export enriched CSV with APR.
""")

uploaded_file = st.file_uploader("Upload Bybit or WOOX funding file (.csv or .xlsx)", type=["csv", "xlsx"])

if uploaded_file:
    exchange = st.selectbox("Select Exchange", ["Bybit", "WOOX"])

    # Read file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.write("Raw Data Preview:", df.head())
    st.write("Columns detected in file:", list(df.columns))

    # Let user select timestamp and funding columns manually
    time_col = st.selectbox("Select Timestamp Column", options=df.columns)
    funding_col = st.selectbox("Select Funding Rate Column", options=df.columns)

    # Convert timestamp to datetime
    df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
    df = df.dropna(subset=[time_col])
    df = df.sort_values(by=time_col)

    # Detect or override interval
    if len(df) > 1:
        detected_interval = (df[time_col].iloc[1] - df[time_col].iloc[0]).total_seconds() / 3600
    else:
        detected_interval = 4  # default to 4 hours
    interval_hours = st.number_input("Funding Interval (Hours)", value=round(detected_interval), step=1)

    # Calculate APR
    df['Funding (%)'] = df[funding_col] * 100
    df['APR (%)'] = df[funding_col] * (365 * 24 / interval_hours) * 100

    # Timeframe selection
    days = st.selectbox("Select APR Timeframe", [30, 14, 7, 3, 1])
    cutoff_time = df[time_col].max() - timedelta(days=days)
    df_filtered = df[df[time_col] >= cutoff_time]

    avg_apr = df_filtered['APR (%)'].mean()

    st.metric(label=f"Average APR over last {days} days", value=f"{avg_apr:.2f}%")

    st.line_chart(df_filtered.set_index(time_col)['APR (%)'])

    # Export enriched CSV
    output = io.BytesIO()
    df.to_csv(output, index=False)
    st.download_button(
        label="📤 Download CSV with APR",
        data=output.getvalue(),
        file_name=f"{exchange.lower()}_with_apr.csv",
        mime="text/csv"
    )