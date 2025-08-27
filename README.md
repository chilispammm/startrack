# 🌍 Startrack Football Analytics – AFCON 2023 Valuation Project

## 📌 Overview
This project implements an **end-to-end football analytics pipeline** using **AFCON 2023 event data** from StatsBomb.  
It combines **ETL pipelines, machine learning modelling, and interactive visualization** into one integrated system for scouting, valuation, and performance analysis.  

The centerpiece is a **Streamlit web app** backed by a **Jupyter Notebook workflow**, designed to:  
- Collect and process AFCON 2023 event-level data.  
- Engineer features and player performance metrics.  
- Train regression models (Linear Regression & XGBoost) to predict market values.  
- Identify undervalued players (transfer bargains).  
- Provide interactive dashboards for exploration.  

---

## ✨ Key Features
### 🔹 Data ETL & Processing
- Automated ingestion of **AFCON 2023 match data** from the free StatsBomb API.  
- Transformation into structured datasets:
  - Player-level aggregates (xG, passes, shots, minutes).  
  - Team-level summaries (goals, possession, progressive play).  
- Saved as clean CSV/Excel outputs for reproducibility.  

### 🔹 Notebook Analysis & Modelling
- Feature engineering: **PerformanceIndex**, **AfconBoost**, position encoding.  
- Models:
  - **Linear Regression** → baseline predictor.  
  - **XGBoost Regressor** → captures non-linear interactions, improved accuracy.  
- Outputs:
  - `PredictedValue` and `PredictedValueXGB` for each player.  
  - **Undervaluation metrics** (absolute & % difference from current market value).  
- Export to `AFCON_2023_with_predictionsXGB.xlsx`.  

### 🔹 Interactive Streamlit Web App
- Team and player dashboards with **filters & selectors**.  
- Plots and KPIs:
  - Passing networks, shot maps, xG contributions.  
  - Player & team heatmaps (attack vs defense).  
  - Top undervalued players table.  
- Sidebar navigation for **exploring AFCON data interactively**.  

---

## 📊 Example Insights
- **Ismaïla Sarr** identified as highly undervalued (≈47% by XGBoost model).  
- Attacking contributions (xG, shots, progressive passes) most predictive of value.  
- Non-linear tournament boosts captured better by XGBoost vs Linear models.  

---

## 🛠️ Tech Stack
- **Python** (3.10+)  
- **Data**: `statsbombpy`, `pandas`, `numpy`  
- **Viz**: `matplotlib`, `seaborn`, `plotly`, `mplsoccer`  
- **ML**: `scikit-learn`, `xgboost`  
- **App**: `streamlit`  
- **Docs**: Jupyter Notebook, Markdown  

---

## 📂 Repository Structure

```
├── notebooks/
│   └── Afcon_2023_Analysis.ipynb    # ETL, feature engineering, modelling
├── data/
│   ├── final_robust.csv             # Processed dataset
│   └── AFCON_2023_with_predictionsXGB.xlsx
├── app.py                           # Streamlit dashboard
├── requirements.txt                 # Dependencies
├── README.md                        # Project overview
```

---

## 📈 Results Snapshot

**Top 10 Undervalued Players (XGBoost Model, % undervaluation):**

1. Ismaïla Sarr (47.2%)
2. Pape Matar Sarr (26.7%)
3. Abdessamad Ezzalzouli (32.3%)
4. Jean Michaël Seri (31.5%)
   ...

---

## 🌟 Applications

* **Scouting & Recruitment** → identify undervalued AFCON talents.
* **Transfer Market Analysis** → model-driven valuation framework.
* **Sports Data Science** → case study of tournament-based player valuation.
* **Education & Research** → reproducible workflow for applied ML in football analytics.

---

## 🔮 Next Steps

* Extend to **other competitions** (PSL, CAF CL, domestic leagues).
* Add advanced metrics (xThreat, possession value, defensive duels).
* Deploy Streamlit app to **Streamlit Cloud / Render**.
* Automate ETL for real-time updates.

---

## 👨‍💻 Author

Developed by **Wayne Chilionje** – Data Scientist and Football Analyst.

