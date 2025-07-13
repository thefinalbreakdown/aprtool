import streamlit as st
import pandas as pd
import io
from datetime import datetime, timedelta

st.title("📈 Isolated Funding Rate APR Viewer")

st.markdown("""
Upload a single funding file (Bybit or WOOX).

- Manually select timestamp and funding rate columns
- Set funding interval (e.g., 4 hours)
- Choose timeframe (30, 14, 7, 3, or 1 day)
- View APR, funding rate charts, and export enriched CSV
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

    # Manual column selection
    time_col = st.selectbox("Select Timestamp Column", options=df.columns)
    funding_col = st.selectbox("Select Funding Rate Column", options=df.columns)

    # Convert timestamp
    df[time_col] = pd.to_datetime(df[time_col], errors='coerce')
    df = df.dropna(subset=[time_col])
    df = df.sort_values(by=time_col)

    # Detect or override funding interval
    if len(df) > 1:
        detected_interval = (df[time_col].iloc[1] - df[time_col].iloc[0]).total_seconds() / 3600
    else:
        detected_interval = 4
    interval_hours = st.number_input("Funding Interval (Hours)", value=round(detected_interval), step=1)

    # Clean and convert funding rate values
    df[funding_col] = df[funding_col].astype(str).str.replace('%', '', regex=False)
    df[funding_col] = pd.to_numeric(df[funding_col], errors='coerce') / 100
    df = df.dropna(subset=[funding_col])

    # Calculate APR
    df['Funding (%)'] = df[funding_col] * 100
    df['APR (%)'] = df[funding_col] * (365 * 24 / interval_hours) * 100

    # Select timeframe
    days = st.selectbox("Select APR Timeframe", [30, 14, 7, 3, 1])
    cutoff_time = df[time_col].max() - timedelta(days=days)
    df_filtered = df[df[time_col] >= cutoff_time]

    # Display average APR
    avg_apr = df_filtered['APR (%)'].mean()
    st.metric(label=f"Average APR over last {days} days", value=f"{avg_apr:.2f}%")

    # Chart 1: APR over time
    st.subheader("📈 APR (%) Over Time")
    st.line_chart(df_filtered.set_index(time_col)['APR (%)'])

    # Chart 2: Raw Funding Rate (%) over time
    st.subheader("💹 Funding Rate (%) Over Time")
    st.line_chart(df_filtered.set_index(time_col)['Funding (%)'])

    # Chart 3: Bar chart of APR per funding interval
    st.subheader("📊 APR Per Funding Interval")
    st.bar_chart(df_filtered.set_index(time_col)['APR (%)'])

    # Export enriched CSV
    output = io.BytesIO()
    df.to_csv(output, index=False)
    st.download_button(
        label="📤 Download CSV with APR",
        data=output.getvalue(),
        file_name=f"{exchange.lower()}_with_apr.csv",
        mime="text/csv"
    )