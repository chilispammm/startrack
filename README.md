# 🌍 Startrack Football Analytics – AFCON 2023 Valuation Project

## 📌 Overview

Startrack is an open-source, end-to-end football analytics pipeline designed to transform raw match event data into actionable sports intelligence. Using **AFCON 2023 event data** from the StatsBomb API, the project integrates modular ETL engineering, statistical modeling, and interactive dashboards to evaluate player performance and identify undervalued talent in the transfer market.

The ecosystem bridges deep data science with football recruitment workflows, providing a reproducible framework for tournament-based player valuation.

---

## 🏗️ System Architecture

```
[ StatsBomb API ] ➔ [ Data ETL Pipeline ] ➔ [ Feature Engineering ]
                                                    │ (PerformanceIndex, AfconBoost)
                                                    ▼
[ Interactive Streamlit App ] ◀─── [ XGBoost / Linear Models ]

```

---

## ✨ Key Features

### 🔹 1. Data ETL & Processing

* **Automated Ingestion:** Programmatic data fetching using `statsbombpy` directly from public tournament feeds.
* **Granular Aggregation:** Converts raw event logs into structured tabular datasets:
* **Player-level:** Aggregated expected goals (xG), progressive pass completions, shooting volume, and minutes played.
* **Team-level:** Tactical metrics spanning possession phases, defensive intensity, and territorial dominance.


* **Reproducible Outgest:** Formats outputs into clean CSV/Excel assets for downstream analytics.

### 🔹 2. Predictive Modeling & Feature Engineering

* **Custom Metrics:** Engineering of domain-specific features including `PerformanceIndex` (positional efficiency) and `AfconBoost` (tournament-specific weightings).
* **Comparative Machine Learning:**
* **Linear Regression:** Establishes a baseline market value predictor.
* **XGBoost Regressor:** Captures highly non-linear player interactions and tournament performance spikes.


* **Value Discrepancy Analysis:** Computes absolute and percentage differentials between model-predicted values and real-world market values to identify market inefficiencies.

### 🔹 3. Streamlit Analytics Dashboard

* **Tactical Visualizations:** Renders passing networks, shot maps, xG contribution charts, and positional heatmaps using `mplsoccer`.
* **Recruitment Filters:** Search and isolate players by position, age, team, and percentage of undervaluation.
* **Interactive Exploration:** Side-panel navigation designed for quick scout exploration and performance profile deep-dives.

---

## 🛠️ Tech Stack

* **Core Engine:** Python (3.10+)
* **Data Engineering & Analysis:** `statsbombpy`, `pandas`, `numpy`
* **Data Visualization:** `matplotlib`, `seaborn`, `plotly`, `mplsoccer`
* **Machine Learning:** `scikit-learn`, `xgboost`
* **Application Layer:** `streamlit`

---

## 🚀 Quick Start & Installation

### Prerequisites

Ensure you have Python 3.10 or higher installed locally.

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/startrack-football-analytics.git
cd startrack-football-analytics

```

### 2. Set Up a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

```

### 3. Install Dependencies

```bash
pip install -r requirements.txt

```

### 4. Run the Streamlit Dashboard

```bash
streamlit run app.py

```

---

## 📊 Sample Insights & Key Results

* **Market Inefficiencies:** The XGBoost model successfully identified several high-leverage market deviations, including highlighting **Ismaïla Sarr** as approximately 47.2% undervalued relative to his underlying performance metrics during the tournament.
* **Feature Importance:** Attacking contributions (high-value xG generation, shots, and progressive passes) proved to be the strongest statistical predictors of tournament market valuation.
* **Model Evaluation:** XGBoost significantly outperformed Linear Regression by effectively capturing non-linear performance variance characteristic of short-form international tournaments.

### Top Undervalued Player Output Snapshot

| Rank | Player | Position | Undervaluation (%) |
| --- | --- | --- | --- |
| 1 | Ismaïla Sarr | Forward / Winger | **47.2%** |
| 2 | Abdessamad Ezzalzouli | Winger | **32.3%** |
| 3 | Jean Michaël Seri | Midfielder | **31.5%** |
| 4 | Pape Matar Sarr | Midfielder | **26.7%** |

---

## 🔮 Roadmap & Next Steps

* [ ] **Multi-League Expansion:** Extend ETL pipelines to integrate domestic and continental leagues (e.g., PSL, CAF Champions League).
* [ ] **Advanced Advanced Metrics:** Integrate positional value modeling such as Expected Threat (xThreat) and defensive duel intensity maps.
* [ ] **Production Deployment:** Host the web app on Streamlit Cloud or Render with automated GitHub Actions for CI/CD.
* [ ] **Live Ingestion Automation:** Schedule pipeline updates via cron-jobs/workflows for near real-time data refreshes during active competitions.

---

## 🤝 Contributing

Contributions are what make the open-source community an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 👨‍💻 Author

Developed and maintained by **Wayne Chilionje** – Data Scientist and Football Analyst.

* Feel free to connect on [LinkedIn](https://www.google.com/search?q=your-linkedin-link) or open an issue in the tracker for technical feedback!
