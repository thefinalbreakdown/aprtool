# Isolated APR Viewer

A simple Streamlit app to:

- Upload funding rate data (Bybit or WOOX)
- Calculate APR based on funding rate and interval
- Display APR over customizable timeframes (30, 14, 7, 3, 1 days)
- Export enriched CSV with APR

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Cloud

1. Push these files to a GitHub repo.
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud).
3. Connect your repo and deploy!