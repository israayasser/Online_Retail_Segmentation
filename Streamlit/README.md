# Customer Intelligence Dashboard

A Streamlit dashboard for the DEBI-OnlineRetail customer segmentation project.

## Where this goes in your project folder

```
DEBI-OnlineRetail/
├── data/                          <- your existing data folder
├── notebook/                      <- your existing notebook folder
└── streamlit/                     <- rename "reports" to this (or any name you like)
    ├── app.py
    ├── requirements.txt
    ├── generate_sample_data.py    (optional -- only needed if you don't have real exports yet)
    ├── transactions_with_segments.csv
    ├── returns_data.csv
    └── guests_data.csv
```

The app reads its 3 data files from **the same folder it runs in** -- either keep the CSVs inside
`streamlit/` (simplest), or point the `pd.read_csv(...)` paths near the top of `app.py` at
`../data/...` if you'd rather keep the CSVs only inside `data/`.

## 1. Run it

```bash
cd streamlit
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`.

## 2. The 3 data files it uses (already provided)

| File | Required? | Powers |
|---|---|---|
| `transactions_with_segments.csv` | **Yes** | Overview, Customer Segments, Products & Markets, Strategy & Actions tabs |
| `returns_data.csv` | Optional | Returns panel in the 5th tab |
| `guests_data.csv` | Optional | Guest activity panel in the 5th tab |

If `returns_data.csv` and `guests_data.csv` are both missing, the app just shows the first 4 tabs and
skips the 5th -- nothing breaks.

To regenerate `transactions_with_segments.csv` after any change to your notebook's clustering:

```python
dashboard_data = df_rfm_ready.merge(
    rfm[['CustomerID', 'Cluster', 'Segment_Name']], on='CustomerID', how='left'
)
dashboard_data.to_csv('transactions_with_segments.csv', index=False)

returns_df.to_csv('returns_data.csv', index=False)
df_guests.to_csv('guests_data.csv', index=False)
```

## 3. Filters (Power BI-style)

The top filter bar (Segment / Country / Date range) applies live to every chart and card in tabs 1-4 --
everything is recomputed from the filtered transaction rows, not from pre-aggregated numbers, so any
combination of filters gives correct results.

## 4. Deploy for your marketing team (free)

1. Push the `streamlit/` folder (code + CSVs) to a GitHub repo.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub.
3. Point it at your repo and `app.py`. You get a public URL your team can open with no installs.

## Design notes

- Palette/type (`Fraunces` serif + `IBM Plex Sans`) are custom-loaded via Google Fonts -- not the
  generic dark-mode/neon or cream/terracotta "AI dashboard" look.
- Segment colors are functional, not decorative: gold = Champions, teal = Loyal Customers, brick = At Risk
  -- the same three colors repeat across every chart/card.
- If your segment names or count ever change, update the `SEGMENT_COLOR`, `SEGMENT_TINT`,
  `SEGMENT_ACTIONS`, and `SEGMENT_NOTE` dictionaries near the top of `app.py` to match.
