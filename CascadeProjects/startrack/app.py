# app.py
import os
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

# Charts
import plotly.express as px
import plotly.graph_objects as go

# Heatmap
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import seaborn as sns

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="ChiliLab – AFCON Talent Finder", layout="wide")
DATA_DIR = Path("app/data")
PLAYERS_FILE_CANDIDATES = ["AFCON_2023_with_predictionsXGB.xlsx", "afcon_players.csv"]
EVENTS_FILE_CANDIDATES  = ["combined_heatmap_df.xlsx", "afcon_events.csv"]

ATTACK_EVENTS = ['Pass', 'Carry', 'Shot', 'Dribble', 'Ball Receipt*']
DEFENSE_EVENTS = ['Pressure', 'Interception', 'Block', 'Duel', 'Clearance', 'Ball Recovery']

EXPECTED_COLS = [
    "player_id","player_name","team","total_minutes_played","matches_played","position",
    "total_shots","total_xg","goal_assists","shot_assists","total_passes","completed_passes",
    "progressive_passes","passes_into_final_third","passes_into_box","total_tackles",
    "total_interceptions","total_clearances","total_pressures","aerials_won",
    "PerformanceIndex","AfconBoost","CurrentValue","PredictedValue","UndervaluationScore",
    "Undervaluation%","PredictedValueXGB","UndervaluationScoreXGB","Undervaluation%XGB"
]

# ---------------------------
# LOADERS
# ---------------------------
@st.cache_data(show_spinner=True)
def load_players_df() -> pd.DataFrame:
    for f in PLAYERS_FILE_CANDIDATES:
        p = DATA_DIR / f
        if p.exists():
            if p.suffix.lower() in [".xlsx", ".xls"]:
                return pd.read_excel(p)
            return pd.read_csv(p)
    raise FileNotFoundError(f"Players file not found in {DATA_DIR}. Tried: {PLAYERS_FILE_CANDIDATES}")

@st.cache_data(show_spinner=True)
def load_events_df() -> pd.DataFrame:
    for f in EVENTS_FILE_CANDIDATES:
        p = DATA_DIR / f
        if p.exists():
            if p.suffix.lower() in [".xlsx", ".xls"]:
                return pd.read_excel(p)
            return pd.read_csv(p)
    # Not fatal: heatmaps just won’t render
    return pd.DataFrame(columns=["match_id","team_id","player_id","event_type","x","y","minute","second","player_name"])

def soft_coerce_cols(df: pd.DataFrame) -> pd.DataFrame:
    # Only rename if exact match ignoring case/spacing
    rename_map = {}
    lc_cols = {c.lower(): c for c in df.columns}
    for need in EXPECTED_COLS:
        key = need.lower()
        if key in lc_cols and lc_cols[key] != need:
            rename_map[lc_cols[key]] = need
    if rename_map:
        df = df.rename(columns=rename_map)
    return df

# ---------------------------
# DATA
# ---------------------------
players_df = load_players_df()
players_df = soft_coerce_cols(players_df)

missing = [c for c in EXPECTED_COLS if c not in players_df.columns]
if missing:
    st.warning(f"Some expected columns are missing in players data: {missing}")

events_df = load_events_df()
events_present = not events_df.empty and {"player_id","event_type","x","y"}.issubset(events_df.columns)

# ---------------------------
# SIDEBAR FILTERS
# ---------------------------
st.sidebar.header("Filters")
min_minutes_default = int(np.nanpercentile(players_df.get("total_minutes_played", pd.Series([0])), 50)) if "total_minutes_played" in players_df else 0
min_minutes = st.sidebar.number_input("Min minutes", min_value=0, value=min_minutes_default, step=30)
pos_options = sorted(players_df["position"].dropna().unique().tolist()) if "position" in players_df else []
sel_positions = st.sidebar.multiselect("Positions", pos_options, default=pos_options[:4] if pos_options else [])
undervaluation_thr = st.sidebar.slider("Min Undervaluation % (XGB)", 0.0, 100.0, 15.0, 0.5)
search = st.sidebar.text_input("Search player/team")

def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "total_minutes_played" in out:
        out = out[out["total_minutes_played"] >= min_minutes]
    if sel_positions:
        out = out[out["position"].isin(sel_positions)]
    if "Undervaluation%XGB" in out:
        out = out[out["Undervaluation%XGB"] >= undervaluation_thr]
    if search:
        s = search.lower()
        cols = [c for c in ["player_name","team"] if c in out.columns]
        if cols:
            mask = pd.Series(False, index=out.index)
            for c in cols:
                mask = mask | out[c].astype(str).str.lower().str.contains(s, na=False)
            out = out[mask]
    return out

filtered_players = apply_filters(players_df)

# ---------------------------
# HEADER
# ---------------------------
st.title("🔥 ChiliLab – AFCON Talent Finder")
st.caption("MVP powered by AFCON 2023 data, event heatmaps, and undervaluation modeling (XGBoost).")

# ---------------------------
# TABS
# ---------------------------
tab_overview, tab_players, tab_player_detail, tab_analytics = st.tabs(["Overview","Players","Player Detail","Analytics"])

# ---------------------------
# OVERVIEW
# ---------------------------
with tab_overview:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Players", len(players_df))
    with col2:
        uv_col = "Undervaluation%XGB" if "Undervaluation%XGB" in players_df else "Undervaluation%"
        st.metric("Avg Undervaluation %", f"{players_df[uv_col].mean():.1f}%" if uv_col in players_df else "—")
    with col3:
        st.metric("Players ≥ Threshold", len(filtered_players))
    with col4:
        st.metric("Avg AFCON Boost", f"{players_df['AfconBoost'].mean():.3f}" if "AfconBoost" in players_df else "—")

    st.subheader("Top 10 Undervalued (XGB)")
    if {"player_name","team","CurrentValue","PredictedValueXGB","UndervaluationScoreXGB","Undervaluation%XGB"}.issubset(players_df.columns):
        top_uv = players_df.sort_values("UndervaluationScoreXGB", ascending=False).head(10)
        st.dataframe(top_uv[["player_name","team","position","CurrentValue","PredictedValueXGB","UndervaluationScoreXGB","Undervaluation%XGB"]], use_container_width=True)
    else:
        st.info("Not enough columns to show Top Undervalued (XGB).")

    st.subheader("Top 10 AFCON Boost")
    if {"player_name","team","AfconBoost","PerformanceIndex"}.issubset(players_df.columns):
        top_boost = players_df.sort_values("AfconBoost", ascending=False).head(10)
        st.dataframe(top_boost[["player_name","team","position","PerformanceIndex","AfconBoost"]], use_container_width=True)
    else:
        st.info("Not enough columns to show AFCON Boost.")

# ---------------------------
# PLAYERS TABLE
# ---------------------------
with tab_players:
    st.subheader("Players")
    show_cols = [c for c in EXPECTED_COLS if c in filtered_players.columns]
    if not show_cols:
        show_cols = filtered_players.columns.tolist()
    st.dataframe(filtered_players[show_cols], use_container_width=True, height=520)

    # Downloads
    csv_bytes = filtered_players[show_cols].to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered (CSV)", csv_bytes, file_name="chililab_filtered_players.csv", mime="text/csv")

# ---------------------------
# PLAYER DETAIL
# ---------------------------
with tab_player_detail:
    st.subheader("Player Detail")
    # Preselect from query param (?player_id=xxxx) if present
    qp = st.query_params
    preselect_id = qp.get("player_id", [None])[0] if qp else None

    options = players_df["player_id"].astype(str).tolist() if "player_id" in players_df else []
    labels = players_df["player_name"].astype(str).tolist() if "player_name" in players_df else []
    id_to_label = dict(zip(options, labels))

    sel_id = st.selectbox("Select Player ID", options=options, index=options.index(preselect_id) if preselect_id in options else 0, format_func=lambda x: f"{x} – {id_to_label.get(x, '')}")

    p = players_df[players_df["player_id"].astype(str) == sel_id]
    if p.empty:
        st.info("Player not found with current filters.")
    else:
        row = p.iloc[0]
        # Header cards
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("Current €M", f"{row.get('CurrentValue', np.nan):,.2f}")
        with c2: st.metric("Predicted €M (XGB)", f"{row.get('PredictedValueXGB', np.nan):,.2f}")
        with c3: st.metric("Undervaluation % (XGB)", f"{row.get('Undervaluation%XGB', np.nan):.1f}%")
        with c4: st.metric("AFCON Boost", f"{row.get('AfconBoost', np.nan):.3f}")

        c5,c6,c7,c8,c9,c10 = st.columns(6)
        with c5: st.metric("xG", f"{row.get('total_xg', np.nan):.2f}")
        with c6: st.metric("Shots", f"{row.get('total_shots', np.nan):.0f}")
        with c7: st.metric("Passes", f"{row.get('total_passes', np.nan):.0f}")
        with c8: st.metric("Completed", f"{row.get('completed_passes', np.nan):.0f}")
        with c9: st.metric("Tackles", f"{row.get('total_tackles', np.nan):.0f}")
        with c10: st.metric("Pressures", f"{row.get('total_pressures', np.nan):.0f}")

        # Heatmap
        st.markdown("### Heatmap")
        if events_present:
            mode = st.radio("Phase", ["Attack","Defense"], horizontal=True)
            if mode == "Attack":
                mask = (events_df["player_id"].astype(str) == sel_id) & (events_df["event_type"].isin(ATTACK_EVENTS))
            else:
                mask = (events_df["player_id"].astype(str) == sel_id) & (events_df["event_type"].isin(DEFENSE_EVENTS))
            pdata = events_df[mask].dropna(subset=["x","y"])

            fig, ax = plt.subplots(figsize=(7, 5))
            pitch = Pitch(pitch_type='statsbomb', pitch_color='white', line_color='black')
            pitch.draw(ax=ax)
            if not pdata.empty:
                sns.kdeplot(
                    x=pdata["x"], y=pdata["y"],
                    fill=True, levels=50, bw_adjust=.6, cmap="Reds" if mode=="Attack" else "Blues", ax=ax
                )
                ax.set_title(f"{row.get('player_name','Player')} – {mode} Heatmap")
            else:
                ax.set_title("No events available for this phase.")
            st.pyplot(fig, clear_figure=True)
        else:
            st.info("Event file not found or missing required columns: cannot render heatmaps.")
        sns.kdeplot(
            x=pdata["x"], 
            y=pdata["y"],
            fill=True, 
            levels=50, 
            bw_adjust=.6,
            cmap="Reds" if mode=="Attack" else "Blues",
            ax=ax,
            alpha=0.30,   # lighter overlay
            thresh=0.05    # avoids global wash
)
        # Raw row (toggle)
        with st.expander("Show full row"):
            st.json({c: row.get(c, None) for c in EXPECTED_COLS if c in players_df.columns})

# ---------------------------
# ANALYTICS
# ---------------------------
with tab_analytics:
    st.subheader("Analytics")

    # Scatter: Current vs Predicted (XGB)
    if {"CurrentValue","PredictedValueXGB","player_name"}.issubset(players_df.columns):
        fig = px.scatter(
            players_df, x="CurrentValue", y="PredictedValueXGB",
            hover_name="player_name", color="position" if "position" in players_df else None,
            title="Current vs Predicted (XGB)"
        )
        fig.add_trace(go.Scatter(x=[players_df["CurrentValue"].min(), players_df["CurrentValue"].max()],
                                 y=[players_df["CurrentValue"].min(), players_df["CurrentValue"].max()],
                                 mode="lines", name="Parity"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough columns for Current vs Predicted (XGB).")

    # Histogram Undervaluation % (XGB)
    if "Undervaluation%XGB" in players_df:
        fig_hist = px.histogram(players_df, x="Undervaluation%XGB", nbins=30, title="Distribution: Undervaluation % (XGB)")
        st.plotly_chart(fig_hist, use_container_width=True)

    # Team bar: sum undervaluation score
    if {"team","UndervaluationScoreXGB"}.issubset(players_df.columns):
        team_sum = players_df.groupby("team", dropna=True)["UndervaluationScoreXGB"].sum().sort_values(ascending=False).head(20)
        fig_bar = px.bar(team_sum, title="Top Teams by Total Undervaluation Score (XGB)", labels={"value":"Total Score","team":"Team"})
        st.plotly_chart(fig_bar, use_container_width=True)
