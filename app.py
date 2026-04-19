"""
╔══════════════════════════════════════════════════════════════════╗
║   RETAIL CHAIN SALES ANALYTICS DASHBOARD                        ║
║   InternshipStudio Final Project                                 ║
║   Stack: Python · SQLite (MySQL-compatible) · Streamlit · Plotly ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import warnings
warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════
# PAGE CONFIGURATION
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="Retail Analytics | InternshipStudio",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════
# CUSTOM CSS — PROFESSIONAL DARK THEME
# ══════════════════════════════════════════════
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #0a0f1e; }
    [data-testid="stSidebar"] { background-color: #0d1526; border-right: 1px solid #1e3a5f; }
    
    .hero-header {
        background: linear-gradient(135deg, #0d1526 0%, #1a3a6b 50%, #0d1526 100%);
        border: 1px solid #1e4d8c;
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        text-align: center;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #64b5f6, #42a5f5, #90caf9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .hero-sub {
        color: #78909c;
        font-size: 0.95rem;
        margin-top: 6px;
    }

    .kpi-card {
        background: linear-gradient(145deg, #0d1f3c, #132a4a);
        border: 1px solid #1e4d8c;
        border-radius: 12px;
        padding: 20px 16px;
        text-align: center;
        height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .kpi-value {
        font-size: 1.7rem;
        font-weight: 700;
        color: #64b5f6;
        line-height: 1.2;
    }
    .kpi-label {
        font-size: 0.75rem;
        color: #78909c;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-top: 4px;
    }
    .kpi-delta {
        font-size: 0.75rem;
        color: #66bb6a;
        margin-top: 2px;
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #90caf9;
        padding: 10px 0 8px 0;
        border-bottom: 2px solid #1e4d8c;
        margin-bottom: 18px;
    }

    .insight-box {
        background: #0d1f3c;
        border-left: 4px solid #42a5f5;
        border-radius: 0 8px 8px 0;
        padding: 14px 18px;
        margin: 10px 0;
        font-size: 0.9rem;
        color: #b0bec5;
    }
    .insight-box strong { color: #64b5f6; }

    .sql-code {
        background: #060d1a;
        border: 1px solid #1e3a5f;
        border-left: 4px solid #42a5f5;
        border-radius: 0 8px 8px 0;
        padding: 16px;
        font-family: 'Courier New', monospace;
        font-size: 0.82rem;
        color: #a5d6a7;
        white-space: pre-wrap;
        overflow-x: auto;
    }

    .stTabs [data-baseweb="tab-list"] { gap: 6px; background: transparent; }
    .stTabs [data-baseweb="tab"] {
        background: #0d1f3c;
        border: 1px solid #1e3a5f;
        border-radius: 8px;
        color: #78909c;
        padding: 8px 18px;
        font-size: 0.88rem;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1565c0, #1976d2) !important;
        color: white !important;
        border-color: #1976d2 !important;
    }

    .stDataFrame { border-radius: 8px; }
    div[data-testid="metric-container"] {
        background: #0d1f3c;
        border: 1px solid #1e3a5f;
        border-radius: 10px;
        padding: 12px 16px;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# DATABASE & DATA LOADING
# ══════════════════════════════════════════════
DB_PATH = "retail_analytics.db"
TRANSACTIONS_CSV = "data/Retail_Data_Transactions.csv"
RESPONSE_CSV     = "data/Retail_Data_Response.csv"

PLOTLY_THEME = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(13,31,60,0.6)",
    font=dict(family="Inter, sans-serif", color="#b0bec5"),
    margin=dict(t=50, b=40, l=40, r=20),
    colorway=["#42a5f5","#66bb6a","#ffa726","#ef5350","#ab47bc","#26c6da","#d4e157"]
)

@st.cache_resource
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

@st.cache_data(show_spinner=False)
def initialise_db():
    """Reads CSVs, cleans data, persists to SQLite, returns success flag."""
    conn = get_conn()

    # ── TRANSACTIONS ──────────────────────────────────────────
    if not os.path.exists(TRANSACTIONS_CSV):
        return False, "Transactions CSV not found at data/Retail_Data_Transactions.csv"

    df = pd.read_csv(TRANSACTIONS_CSV)
    df.columns = (df.columns.str.strip()
                             .str.lower()
                             .str.replace(r"[\s\-]+", "_", regex=True))

    # Rename to canonical names regardless of source capitalisation
    renames = {}
    for c in df.columns:
        if "transaction" in c and "id" in c:   renames[c] = "transaction_id"
        if "transaction" in c and "time" in c: renames[c] = "transaction_time"
        if "item" in c and "code" in c:        renames[c] = "item_code"
        if "item" in c and "desc" in c:        renames[c] = "item_description"
        if "number" in c or "qty" in c or "quantity" in c: renames[c] = "qty"
        if "cost" in c and "per" in c:         renames[c] = "cost_per_item"
        if c == "country":                     renames[c] = "country"
    df.rename(columns=renames, inplace=True)

    # Parse datetime
    df["transaction_time"] = pd.to_datetime(df["transaction_time"], errors="coerce")
    df.dropna(subset=["transaction_time"], inplace=True)

    # Numeric coercion
    df["qty"]           = pd.to_numeric(df.get("qty", 0), errors="coerce").fillna(0)
    df["cost_per_item"] = pd.to_numeric(df.get("cost_per_item", 0), errors="coerce").fillna(0)

    # Remove junk rows
    df = df[(df["qty"] > 0) & (df["cost_per_item"] > 0)]

    # Calculated fields
    df["total_sales"]    = df["qty"] * df["cost_per_item"]
    df["txn_year"]       = df["transaction_time"].dt.year
    df["txn_month"]      = df["transaction_time"].dt.month
    df["txn_month_name"] = df["transaction_time"].dt.strftime("%b")
    df["txn_dow"]        = df["transaction_time"].dt.day_name()
    df["txn_hour"]       = df["transaction_time"].dt.hour
    df["year_month"]     = df["transaction_time"].dt.to_period("M").astype(str)

    df.to_sql("transactions", conn, if_exists="replace", index=False)

    # ── CUSTOMER RESPONSE ─────────────────────────────────────
    if os.path.exists(RESPONSE_CSV):
        dfr = pd.read_csv(RESPONSE_CSV)
        dfr.columns = dfr.columns.str.strip().str.lower().str.replace(" ", "_")
        dfr.to_sql("customer_response", conn, if_exists="replace", index=False)

    conn.commit()
    return True, "OK"

def qry(sql: str) -> pd.DataFrame:
    return pd.read_sql(sql, get_conn())


# ══════════════════════════════════════════════
# BOOT
# ══════════════════════════════════════════════
with st.spinner("⚙️  Initialising database …"):
    ok, msg = initialise_db()

if not ok:
    st.error(f"❌ {msg}")
    st.info("👉 Upload `Retail_Data_Transactions.csv` into the `data/` folder on Replit.")
    st.stop()

@st.cache_data(show_spinner=False)
def load_main():
    df = qry("SELECT * FROM transactions")
    df["transaction_time"] = pd.to_datetime(df["transaction_time"], errors="coerce")
    return df

@st.cache_data(show_spinner=False)
def load_response():
    try:
        return qry("SELECT * FROM customer_response")
    except Exception:
        return None

df  = load_main()
dfr = load_response()

# ══════════════════════════════════════════════
# SIDEBAR — GLOBAL FILTERS
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🛒 Retail Analytics")
    st.caption("InternshipStudio · Final Project")
    st.divider()

    st.markdown("#### 🔧 Global Filters")

    all_countries = sorted(df["country"].dropna().unique())
    sel_countries = st.multiselect("🌍 Countries", all_countries, default=all_countries)

    all_years = sorted(df["txn_year"].dropna().unique().astype(int))
    sel_years = st.multiselect("📅 Years", all_years, default=all_years)

    st.divider()
    date_min = df["transaction_time"].min().date()
    date_max = df["transaction_time"].max().date()
    st.caption(f"📆 **Range:** {date_min} → {date_max}")
    st.caption(f"📊 **Records:** {len(df):,}")
    st.caption(f"🌍 **Countries:** {df['country'].nunique()}")
    st.caption(f"📦 **Products:** {df['item_code'].nunique()}")

# Apply filters
fdf = df[df["country"].isin(sel_countries) & df["txn_year"].isin(sel_years)]

# ══════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════
st.markdown("""
<div class="hero-header">
  <p class="hero-title">🛒 Retail Chain Sales Analytics</p>
  <p class="hero-sub">InternshipStudio Final Project &nbsp;·&nbsp; Python · SQL · Excel &nbsp;·&nbsp; Interactive Intelligence Dashboard</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════
tabs = st.tabs([
    "📊 Overview",
    "🌍 Geographic",
    "📦 Products",
    "📅 Time Trends",
    "👥 Customers",
    "🔍 SQL Lab"
])


# ╔══════════════════════════════════╗
# ║  TAB 1 · EXECUTIVE OVERVIEW      ║
# ╚══════════════════════════════════╝
with tabs[0]:
    st.markdown('<div class="section-title">📊 Executive Overview</div>', unsafe_allow_html=True)

    # ── KPI ROW ──────────────────────────────
    total_rev  = fdf["total_sales"].sum()
    total_txns = fdf["transaction_id"].nunique()
    n_countries = fdf["country"].nunique()
    n_products  = fdf["item_code"].nunique()
    aov         = fdf.groupby("transaction_id")["total_sales"].sum().mean()
    avg_basket  = fdf.groupby("transaction_id")["qty"].sum().mean()

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    kpis = [
        ("💰 Total Revenue",    f"${total_rev:,.0f}",    c1),
        ("🧾 Transactions",     f"{total_txns:,}",       c2),
        ("🌍 Countries",        f"{n_countries}",        c3),
        ("📦 Products",         f"{n_products}",         c4),
        ("🛒 Avg Order Value",  f"${aov:,.2f}",          c5),
        ("🛍️ Avg Basket Size",  f"{avg_basket:.1f} items",c6),
    ]
    for label, val, col in kpis:
        with col:
            st.markdown(f"""
            <div class="kpi-card">
              <div class="kpi-value">{val}</div>
              <div class="kpi-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── REVENUE TREND + PIE ───────────────────
    col_left, col_right = st.columns([2, 1])

    with col_left:
        monthly = (fdf.groupby("year_month")["total_sales"]
                      .sum().reset_index()
                      .sort_values("year_month"))
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly["year_month"], y=monthly["total_sales"],
            mode="lines", fill="tozeroy",
            line=dict(color="#42a5f5", width=2.5),
            fillcolor="rgba(66,165,245,0.15)",
            name="Revenue"
        ))
        fig.update_layout(
            title="📈 Monthly Revenue Trend",
            xaxis_title="Month", yaxis_title="Revenue ($)",
            xaxis_tickangle=-45,
            **PLOTLY_THEME
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        cr = (fdf.groupby("country")["total_sales"]
                 .sum().reset_index()
                 .sort_values("total_sales", ascending=False)
                 .head(8))
        fig2 = px.pie(cr, names="country", values="total_sales",
                      title="🌍 Revenue Share by Country", hole=0.45,
                      color_discrete_sequence=px.colors.sequential.Blues_r)
        fig2.update_layout(**PLOTLY_THEME)
        fig2.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig2, use_container_width=True)

    # ── TOP 5 PRODUCTS TABLE ──────────────────
    st.markdown('<div class="section-title">🏆 Top 5 Revenue Drivers</div>', unsafe_allow_html=True)
    top5 = (fdf.groupby(["item_code","item_description"])
               .agg(Revenue=("total_sales","sum"),
                    Transactions=("transaction_id","count"),
                    AvgPrice=("cost_per_item","mean"))
               .reset_index()
               .sort_values("Revenue", ascending=False)
               .head(5))
    top5["Revenue"]  = top5["Revenue"].apply(lambda x: f"${x:,.2f}")
    top5["AvgPrice"] = top5["AvgPrice"].apply(lambda x: f"${x:,.2f}")
    st.dataframe(top5, use_container_width=True, hide_index=True)

    # ── KEY INSIGHTS ─────────────────────────
    top_country = fdf.groupby("country")["total_sales"].sum().idxmax()
    top_month   = monthly.loc[monthly["total_sales"].idxmax(), "year_month"]
    top_product = (fdf.groupby("item_description")["total_sales"]
                      .sum().idxmax())

    st.markdown(f"""
    <div class="insight-box">💡 <strong>Top Market:</strong> {top_country} leads in total revenue.</div>
    <div class="insight-box">📅 <strong>Peak Month:</strong> {top_month} recorded the highest monthly sales.</div>
    <div class="insight-box">📦 <strong>Star Product:</strong> "{top_product}" is the highest-grossing item.</div>
    """, unsafe_allow_html=True)


# ╔══════════════════════════════════╗
# ║  TAB 2 · GEOGRAPHIC ANALYSIS     ║
# ╚══════════════════════════════════╝
with tabs[1]:
    st.markdown('<div class="section-title">🌍 Geographic Analysis</div>', unsafe_allow_html=True)

    geo = fdf.groupby("country").agg(
        Revenue=("total_sales","sum"),
        Transactions=("transaction_id","count"),
        Items_Sold=("qty","sum"),
        AOV=("total_sales","mean"),
        Avg_Item_Price=("cost_per_item","mean")
    ).reset_index().sort_values("Revenue", ascending=False)

    c1,c2 = st.columns(2)
    with c1:
        fig = px.bar(geo, x="country", y="Revenue",
                     title="💰 Total Revenue by Country",
                     color="Revenue", color_continuous_scale="Blues",
                     text_auto=".2s")
        fig.update_layout(xaxis_tickangle=-40, **PLOTLY_THEME)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = px.bar(geo, x="country", y="Transactions",
                      title="🧾 Transaction Volume by Country",
                      color="Transactions", color_continuous_scale="Greens",
                      text_auto=True)
        fig2.update_layout(xaxis_tickangle=-40, **PLOTLY_THEME)
        st.plotly_chart(fig2, use_container_width=True)

    c3,c4 = st.columns(2)
    with c3:
        fig3 = px.bar(geo, x="country", y="AOV",
                      title="🛒 Average Order Value by Country",
                      color="AOV", color_continuous_scale="Oranges",
                      text_auto=".2f")
        fig3.update_layout(xaxis_tickangle=-40, **PLOTLY_THEME)
        st.plotly_chart(fig3, use_container_width=True)
    with c4:
        fig4 = px.scatter(geo, x="Transactions", y="Revenue",
                          size="Items_Sold", color="country", text="country",
                          title="🔵 Revenue vs Volume (bubble = units sold)",
                          size_max=60)
        fig4.update_traces(textposition="top center")
        fig4.update_layout(**PLOTLY_THEME)
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown('<div class="section-title">📋 Country Performance Summary</div>', unsafe_allow_html=True)
    geo_disp = geo.copy()
    geo_disp["Revenue"]         = geo_disp["Revenue"].apply(lambda x: f"${x:,.2f}")
    geo_disp["AOV"]             = geo_disp["AOV"].apply(lambda x: f"${x:,.2f}")
    geo_disp["Avg_Item_Price"]  = geo_disp["Avg_Item_Price"].apply(lambda x: f"${x:,.2f}")
    st.dataframe(geo_disp, use_container_width=True, hide_index=True)


# ╔══════════════════════════════════╗
# ║  TAB 3 · PRODUCT ANALYSIS        ║
# ╚══════════════════════════════════╝
with tabs[2]:
    st.markdown('<div class="section-title">📦 Product Performance Analysis</div>', unsafe_allow_html=True)

    prod = fdf.groupby(["item_code","item_description"]).agg(
        Revenue=("total_sales","sum"),
        Qty=("qty","sum"),
        Transactions=("transaction_id","count"),
        AvgPrice=("cost_per_item","mean")
    ).reset_index()

    top_n = st.slider("📊 Show top N products", 5, 30, 15, key="prod_n")

    c1,c2 = st.columns(2)
    with c1:
        dfp = prod.sort_values("Revenue", ascending=True).tail(top_n)
        fig = px.bar(dfp, x="Revenue", y="item_description", orientation="h",
                     title=f"💰 Top {top_n} Products — Revenue",
                     color="Revenue", color_continuous_scale="Blues",
                     text_auto=".2s")
        fig.update_layout(yaxis_title="", height=520, **PLOTLY_THEME)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        dfq = prod.sort_values("Qty", ascending=True).tail(top_n)
        fig2 = px.bar(dfq, x="Qty", y="item_description", orientation="h",
                      title=f"📦 Top {top_n} Products — Units Sold",
                      color="Qty", color_continuous_scale="Greens",
                      text_auto=True)
        fig2.update_layout(yaxis_title="", height=520, **PLOTLY_THEME)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">💲 Price Analysis</div>', unsafe_allow_html=True)
    c3,c4 = st.columns(2)
    with c3:
        fig3 = px.histogram(fdf, x="cost_per_item", nbins=60,
                            title="Distribution of Item Prices",
                            color_discrete_sequence=["#42a5f5"])
        fig3.update_layout(**PLOTLY_THEME)
        st.plotly_chart(fig3, use_container_width=True)
    with c4:
        fig4 = px.box(fdf, x="country", y="cost_per_item",
                      color="country",
                      title="Price Spread by Country")
        fig4.update_layout(xaxis_tickangle=-40, showlegend=False, **PLOTLY_THEME)
        st.plotly_chart(fig4, use_container_width=True)

    # Revenue contribution (80/20 analysis)
    st.markdown('<div class="section-title">📐 Pareto — 80/20 Revenue Contribution</div>', unsafe_allow_html=True)
    pareto = prod.sort_values("Revenue", ascending=False).copy()
    pareto["cum_pct"] = pareto["Revenue"].cumsum() / pareto["Revenue"].sum() * 100
    pareto["rank"] = range(1, len(pareto)+1)
    top80 = pareto[pareto["cum_pct"] <= 80]
    st.markdown(f"""
    <div class="insight-box">
      📐 <strong>Pareto Insight:</strong> The top <strong>{len(top80)}</strong> products 
      (out of {len(pareto)}) account for <strong>80%</strong> of total revenue —
      these are your core SKUs to protect and prioritise.
    </div>""", unsafe_allow_html=True)

    fig5 = go.Figure()
    fig5.add_trace(go.Bar(x=pareto.head(30)["item_description"],
                          y=pareto.head(30)["Revenue"],
                          name="Revenue", marker_color="#42a5f5"))
    fig5.add_trace(go.Scatter(x=pareto.head(30)["item_description"],
                              y=pareto.head(30)["cum_pct"],
                              mode="lines+markers", name="Cumulative %",
                              yaxis="y2", line=dict(color="#ffa726", width=2)))
    fig5.update_layout(
        title="Pareto Chart — Top 30 Products",
        yaxis=dict(title="Revenue ($)"),
        yaxis2=dict(title="Cumulative %", overlaying="y", side="right",
                    range=[0,105], ticksuffix="%"),
        xaxis_tickangle=-45,
        **PLOTLY_THEME
    )
    st.plotly_chart(fig5, use_container_width=True)


# ╔══════════════════════════════════╗
# ║  TAB 4 · TIME TRENDS             ║
# ╚══════════════════════════════════╝
with tabs[3]:
    st.markdown('<div class="section-title">📅 Temporal Sales Analysis</div>', unsafe_allow_html=True)

    c1,c2 = st.columns(2)

    with c1:
        dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        dow = (fdf.groupby("txn_dow")["total_sales"].sum()
                  .reindex(dow_order).reset_index())
        fig = px.bar(dow, x="txn_dow", y="total_sales",
                     title="📅 Revenue by Day of Week",
                     color="total_sales", color_continuous_scale="Blues",
                     text_auto=".2s")
        fig.update_layout(xaxis_title="", **PLOTLY_THEME)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        hour = fdf.groupby("txn_hour")["total_sales"].sum().reset_index()
        fig2 = go.Figure(go.Scatter(
            x=hour["txn_hour"], y=hour["total_sales"],
            mode="lines+markers",
            line=dict(color="#42a5f5", width=2.5),
            marker=dict(size=7, color="#ffa726"),
            fill="tozeroy", fillcolor="rgba(66,165,245,0.12)"
        ))
        fig2.update_layout(title="⏰ Revenue by Hour of Day",
                           xaxis_title="Hour", yaxis_title="Revenue ($)",
                           **PLOTLY_THEME)
        st.plotly_chart(fig2, use_container_width=True)

    # Year-over-year
    if len(sel_years) >= 1:
        yoy = fdf.groupby(["txn_year","txn_month"])["total_sales"].sum().reset_index()
        yoy["year_str"] = yoy["txn_year"].astype(str)
        fig3 = px.line(yoy, x="txn_month", y="total_sales", color="year_str",
                       markers=True,
                       title="📈 Year-over-Year Monthly Comparison",
                       labels={"txn_month":"Month","total_sales":"Revenue ($)","year_str":"Year"})
        fig3.update_xaxes(tickvals=list(range(1,13)),
                          ticktext=["Jan","Feb","Mar","Apr","May","Jun",
                                    "Jul","Aug","Sep","Oct","Nov","Dec"])
        fig3.update_layout(**PLOTLY_THEME)
        st.plotly_chart(fig3, use_container_width=True)

    # Heatmap
    st.markdown('<div class="section-title">🔥 Sales Intensity Heatmap</div>', unsafe_allow_html=True)
    heat = (fdf.groupby(["txn_dow","txn_hour"])["total_sales"]
               .sum().unstack(fill_value=0)
               .reindex(dow_order))
    fig4 = px.imshow(heat, title="Revenue Heatmap — Day × Hour",
                     color_continuous_scale="Blues",
                     labels=dict(x="Hour of Day", y="Day of Week", color="Revenue ($)"),
                     aspect="auto")
    fig4.update_layout(**PLOTLY_THEME)
    st.plotly_chart(fig4, use_container_width=True)

    peak_day  = dow.loc[dow["total_sales"].idxmax(), "txn_dow"]
    peak_hour = hour.loc[hour["total_sales"].idxmax(), "txn_hour"]
    st.markdown(f"""
    <div class="insight-box">⏰ <strong>Peak Day:</strong> {peak_day} sees the highest transaction volume.</div>
    <div class="insight-box">🕐 <strong>Peak Hour:</strong> {int(peak_hour):02d}:00 – {int(peak_hour)+1:02d}:00 is the busiest trading window.</div>
    """, unsafe_allow_html=True)


# ╔══════════════════════════════════╗
# ║  TAB 5 · CUSTOMER INTELLIGENCE   ║
# ╚══════════════════════════════════╝
with tabs[4]:
    st.markdown('<div class="section-title">👥 Customer Intelligence</div>', unsafe_allow_html=True)

    if dfr is not None:
        total_cust = len(dfr)
        responded  = int(dfr["response"].sum())
        no_resp    = total_cust - responded
        rate       = responded / total_cust * 100

        c1,c2,c3 = st.columns(3)
        with c1: st.metric("👥 Total Customers", f"{total_cust:,}")
        with c2: st.metric("✅ Positive Responses", f"{responded:,}")
        with c3: st.metric("📊 Response Rate", f"{rate:.1f}%")

        c4,c5 = st.columns(2)
        with c4:
            rc = pd.DataFrame({
                "Segment": ["Positive Response","No Response"],
                "Count":   [responded, no_resp]
            })
            fig = px.pie(rc, names="Segment", values="Count",
                         title="Campaign Response Distribution", hole=0.45,
                         color_discrete_sequence=["#42a5f5","#ef5350"])
            fig.update_layout(**PLOTLY_THEME)
            st.plotly_chart(fig, use_container_width=True)
        with c5:
            fig2 = px.funnel(rc, x="Count", y="Segment",
                             title="Conversion Funnel",
                             color_discrete_sequence=["#42a5f5","#ef5350"])
            fig2.update_layout(**PLOTLY_THEME)
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown(f"""
        <div class="insight-box">
          📬 <strong>Campaign Insight:</strong> Out of {total_cust:,} customers, 
          only <strong>{rate:.1f}%</strong> responded positively. 
          This signals opportunity — {no_resp:,} customers remain unconverted 
          and can be targeted with personalised follow-up campaigns.
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-title">🗂️ Customer Response Sample</div>', unsafe_allow_html=True)
        st.dataframe(dfr.head(100), use_container_width=True, hide_index=True)
    else:
        st.info("📂 Customer response data not found — add `data/Retail_Data_Response.csv` to enable this tab.")

    # Transaction value distribution (always available)
    st.markdown('<div class="section-title">💰 Transaction Value Distribution</div>', unsafe_allow_html=True)
    tv = fdf.groupby("transaction_id")["total_sales"].sum().reset_index()

    c6,c7 = st.columns(2)
    with c6:
        fig3 = px.histogram(tv, x="total_sales", nbins=80,
                            title="Distribution of Transaction Values",
                            color_discrete_sequence=["#42a5f5"])
        fig3.update_layout(**PLOTLY_THEME)
        st.plotly_chart(fig3, use_container_width=True)
    with c7:
        fig4 = px.box(tv, y="total_sales", title="Transaction Value Box Plot",
                      color_discrete_sequence=["#ffa726"])
        fig4.update_layout(**PLOTLY_THEME)
        st.plotly_chart(fig4, use_container_width=True)

    # Percentile breakdown
    pcts = tv["total_sales"].quantile([.25,.5,.75,.9,.95,.99]).to_dict()
    st.markdown(f"""
    <div class="insight-box">
      📊 <strong>Percentile Breakdown —</strong>
      P25: ${pcts[.25]:.2f} &nbsp;|&nbsp;
      Median: ${pcts[.5]:.2f} &nbsp;|&nbsp;
      P75: ${pcts[.75]:.2f} &nbsp;|&nbsp;
      P90: ${pcts[.9]:.2f} &nbsp;|&nbsp;
      P99: ${pcts[.99]:.2f}
    </div>""", unsafe_allow_html=True)


# ╔══════════════════════════════════╗
# ║  TAB 6 · SQL LAB                 ║
# ╚══════════════════════════════════╝
with tabs[5]:
    st.markdown('<div class="section-title">🔍 Interactive SQL Lab</div>', unsafe_allow_html=True)
    st.caption("All queries run against the SQLite database built from your CSVs — identical logic to MySQL.")

    PRESET_QUERIES = {
        "📦 Top 10 Products by Revenue": """SELECT
    item_description,
    SUM(total_sales)           AS total_revenue,
    SUM(qty)                   AS total_units_sold,
    COUNT(DISTINCT transaction_id) AS transactions,
    ROUND(AVG(cost_per_item), 2)   AS avg_price
FROM transactions
GROUP BY item_description
ORDER BY total_revenue DESC
LIMIT 10;""",

        "🌍 Revenue & Transactions by Country": """SELECT
    country,
    COUNT(DISTINCT transaction_id) AS transactions,
    SUM(qty)                       AS units_sold,
    ROUND(SUM(total_sales), 2)     AS total_revenue,
    ROUND(AVG(total_sales), 2)     AS avg_order_value
FROM transactions
GROUP BY country
ORDER BY total_revenue DESC;""",

        "📅 Monthly Sales Trend": """SELECT
    year_month,
    COUNT(DISTINCT transaction_id) AS transactions,
    ROUND(SUM(total_sales), 2)     AS monthly_revenue,
    ROUND(AVG(total_sales), 2)     AS avg_sale_value
FROM transactions
GROUP BY year_month
ORDER BY year_month;""",

        "⏰ Revenue by Hour of Day": """SELECT
    txn_hour                       AS hour_of_day,
    COUNT(DISTINCT transaction_id) AS transactions,
    ROUND(SUM(total_sales), 2)     AS revenue
FROM transactions
GROUP BY txn_hour
ORDER BY revenue DESC;""",

        "📅 Revenue by Day of Week": """SELECT
    txn_dow                        AS day,
    COUNT(DISTINCT transaction_id) AS transactions,
    ROUND(SUM(total_sales), 2)     AS revenue,
    ROUND(AVG(total_sales), 2)     AS avg_sale
FROM transactions
GROUP BY txn_dow
ORDER BY revenue DESC;""",

        "🔍 Data Quality Check": """SELECT
    COUNT(*)                                   AS total_rows,
    COUNT(DISTINCT transaction_id)             AS unique_transactions,
    COUNT(DISTINCT item_code)                  AS unique_products,
    COUNT(DISTINCT country)                    AS unique_countries,
    MIN(transaction_time)                      AS earliest_transaction,
    MAX(transaction_time)                      AS latest_transaction,
    ROUND(MIN(cost_per_item), 2)               AS min_price,
    ROUND(MAX(cost_per_item), 2)               AS max_price,
    ROUND(AVG(cost_per_item), 2)               AS avg_price
FROM transactions;""",

        "📐 Pareto — Product Revenue Contribution": """SELECT
    item_description,
    ROUND(SUM(total_sales), 2) AS revenue,
    ROUND(
        100.0 * SUM(total_sales) / (SELECT SUM(total_sales) FROM transactions),
        2
    )                          AS pct_of_total
FROM transactions
GROUP BY item_description
ORDER BY revenue DESC
LIMIT 20;"""
    }

    selected = st.selectbox("📋 Preset Query", list(PRESET_QUERIES.keys()))
    user_sql = st.text_area("✏️ SQL Editor", value=PRESET_QUERIES[selected], height=180)

    if st.button("▶️ Run Query", type="primary"):
        try:
            result = qry(user_sql)
            st.success(f"✅ {len(result):,} rows returned")
            st.dataframe(result, use_container_width=True)

            # Auto chart
            num_cols  = result.select_dtypes("number").columns.tolist()
            text_cols = result.select_dtypes("object").columns.tolist()
            if text_cols and num_cols and len(result) > 1:
                auto_fig = px.bar(
                    result.head(25),
                    x=text_cols[0], y=num_cols[0],
                    title=f"Auto-chart: {text_cols[0]} vs {num_cols[0]}",
                    color=num_cols[0], color_continuous_scale="Blues",
                    text_auto=".2s"
                )
                auto_fig.update_layout(xaxis_tickangle=-40, **PLOTLY_THEME)
                st.plotly_chart(auto_fig, use_container_width=True)
        except Exception as e:
            st.error(f"❌ SQL Error: {e}")

    # Show schema
    with st.expander("📋 Database Schema Reference"):
        st.markdown("""
**Table: `transactions`**

| Column | Type | Description |
|---|---|---|
| transaction_id | TEXT | Unique transaction identifier |
| transaction_time | DATETIME | Full datetime of transaction |
| item_code | TEXT | Product SKU code |
| item_description | TEXT | Product name |
| qty | INTEGER | Units purchased |
| cost_per_item | REAL | Unit price |
| country | TEXT | Market/country |
| total_sales | REAL | Calculated: qty × cost_per_item |
| txn_year | INTEGER | Extracted year |
| txn_month | INTEGER | Extracted month (1–12) |
| txn_dow | TEXT | Day of week name |
| txn_hour | INTEGER | Hour of day (0–23) |
| year_month | TEXT | 'YYYY-MM' period string |

**Table: `customer_response`**

| Column | Type | Description |
|---|---|---|
| customer_id | TEXT | Customer identifier |
| response | INTEGER | Campaign response: 1 = Yes, 0 = No |
""")


# ── FOOTER ─────────────────────────────────────────────────────────────────
st.divider()
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    st.caption("🛒 **Retail Chain Sales Analytics**")
with col_f2:
    st.caption("📊 InternshipStudio Final Project")
with col_f3:
    st.caption("⚙️ Python · SQLite · Streamlit · Plotly")
