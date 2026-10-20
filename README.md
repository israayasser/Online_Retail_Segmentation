# Customer Segmentation — Online Retail

Unsupervised machine learning project that segments the customers of a UK-based online retailer using RFM (Recency, Frequency, Monetary) analysis and K-Means clustering, with a business playbook for each segment.

## Team
- Esraa Yasser Sayed Ahmed
- Doha Waleed Zaghloul Abdelnaeem
- Alyaa Mohamed Abdelftah Etman
- Hasnaa Hussien Abdelkader Khallaf

## Problem
The business had 541,959 raw transactions with missing customer IDs, cancellations, returns and invalid prices. Marketing spend was not targeted, so it was hard to tell which customers were most valuable and which were at risk of leaving.

## Approach
1. **Data cleaning:** recovered 19,156 missing CustomerIDs and 18,870 missing InvoiceNos from invoice-level and customer-timestamp relationships, removed duplicates, invalid prices and non-product codes, and split returns and guest purchases into separate datasets.
2. **EDA:** revenue trends, top products, country mix, returns and purchase frequency.
3. **RFM features:** 4,330 customers, with log-transform on Frequency and Monetary, then StandardScaler.
4. **Modeling:** K-Means (k selected by Silhouette Score and Davies–Bouldin), compared against Hierarchical clustering, DBSCAN and Gaussian Mixture Models.
5. **Validation:** Adjusted Rand Index against Hierarchical clustering (0.676) and an independent CLV measure.

## Results

| Segment | Customers | Avg. recency | Avg. purchases | Avg. spend | Share of customer revenue |
|---|---|---|---|---|---|
| Champions | 1,325 (30.6%) | 30 days | 9.7 | £5,145 | 80.9% |
| Loyal Customers | 2,020 (46.7%) | 55 days | 2.0 | £601 | 14.4% |
| At Risk | 985 (22.7%) | 255 days | 1.4 | £405 | 4.7% |

Model quality: Silhouette Score 0.415, Davies–Bouldin 0.827. The silhouette score is below the 0.50 target; this is expected for continuous RFM data and is discussed in the notebook.

## Recommendations
- **Champions:** retention first (premium loyalty, early access, VIP support).
- **Loyal Customers:** upsell and cross-sell to raise purchase frequency and basket size.
- **At Risk:** win-back campaigns with personalized offers before the segment churns.

## Repository contents
- `Customer_Segmentation.ipynb`: full analysis notebook with findings for every section.

## Dashboard Link:
https://onlineretailsegmentation-pwdmmwka2nmssyvmmxbpbm.streamlit.app/


## Tech stack
Python, pandas, NumPy, scikit-learn, Plotly, Matplotlib, Seaborn, Streamlit.

## Limitations
- One year of data from a single UK retailer, so results may not generalize to other markets.
- About a third of transactions are guest purchases and are excluded from the customer-level segmentation.
- Segments represent general behavioral tendencies rather than sharply separated groups.
