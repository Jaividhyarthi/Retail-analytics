"""
RETAIL CHAIN SALES ANALYTICS DASHBOARD
InternshipStudio Final Project
Stack: Python · SQLite · Streamlit · Plotly
"""

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import os
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Retail Analytics | InternshipStudio",
    page_icon="🛒", layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background-color:#0a0f1e;}
[data-testid="stSidebar"]{background-color:#0d1526;border-right:1px solid #1e3a5f;}
.hero-header{background:linear-gradient(135deg,#0d1526 0%,#1a3a6b 50%,#0d1526 100%);
  border:1px solid #1e4d8c;border-radius:16px;padding:28px 32px;
  margin-bottom:24px;text-align:center;}
.hero-title{font-size:2.1rem;font-weight:800;
  background:linear-gradient(90deg,#64b5f6,#42a5f5,#90caf9);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0;}
.hero-sub{color:#78909c;font-size:.92rem;margin-top:6px;}
.kpi-card{background:linear-gradient(145deg,#0d1f3c,#132a4a);
  border:1px solid #1e4d8c;border-radius:12px;padding:18px 12px;
  text-align:center;height:100px;display:flex;flex-direction:column;justify-content:center;}
.kpi-value{font-size:1.6rem;font-weight:700;color:#64b5f6;line-height:1.2;}
.kpi-label{font-size:.72rem;color:#78909c;text-transform:uppercase;letter-spacing:1px;margin-top:4px;}
.section-title{font-size:1.2rem;font-weight:600;color:#90caf9;
  padding:8px 0;border-bottom:2px solid #1e4d8c;margin-bottom:16px;}
.insight-box{background:#0d1f3c;border-left:4px solid #42a5f5;
  border-radius:0 8px 8px 0;padding:12px 16px;margin:8px 0;
  font-size:.88rem;color:#b0bec5;}
.insight-box strong{color:#64b5f6;}
.stTabs [data-baseweb="tab-list"]{gap:6px;background:transparent;}
.stTabs [data-baseweb="tab"]{background:#0d1f3c;border:1px solid #1e3a5f;
  border-radius:8px;color:#78909c;padding:8px 16px;font-size:.85rem;}
.stTabs [aria-selected="true"]{
  background:linear-gradient(135deg,#1565c0,#1976d2)!important;
  color:white!important;border-color:#1976d2!important;}
div[data-testid="metric-container"]{background:#0d1f3c;
  border:1px solid #1e3a5f;border-radius:10px;padding:12px;}
</style>
""", unsafe_allow_html=True)

PT = dict(
    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(13,31,60,0.5)",
    font=dict(family="Inter,sans-serif", color="#b0bec5"),
    margin=dict(t=48, b=36, l=36, r=20),
)

# ══════════════════════════════════════════════
# BULLETPROOF COLUMN NORMALISER
# Handles every known Kaggle retail CSV format
# ══════════════════════════════════════════════
def normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map whatever columns the CSV has → standard names."""
    df = df.copy()
    # Step 1: lowercase + remove all spaces/hyphens
    df.columns = (df.columns.str.strip()
                             .str.lower()
                             .str.replace(r"[\s\-_]+", "", regex=True))

    col_set = set(df.columns)

    # ── TRANSACTION ID ──────────────────────────
    for c in ["transactionid","transaction_id","txnid","id","trans_id"]:
        if c in col_set:
            df.rename(columns={c: "transaction_id"}, inplace=True)
            break
    if "transaction_id" not in df.columns:
        df["transaction_id"] = df.index.astype(str)

    # ── TRANSACTION TIME ────────────────────────
    for c in ["transactiontime","transactiondate","trans_date","transdate",
              "date","datetime","timestamp","orderdate","order_date",
              "transaction_date","saledate","sale_date"]:
        if c in df.columns:
            df.rename(columns={c: "transaction_time"}, inplace=True)
            break

    # ── ITEM CODE ───────────────────────────────
    for c in ["itemcode","item_code","sku","productcode","product_code","prodcode"]:
        if c in df.columns:
            df.rename(columns={c: "item_code"}, inplace=True)
            break
    if "item_code" not in df.columns:
        df["item_code"] = "ITEM001"

    # ── ITEM DESCRIPTION ────────────────────────
    for c in ["itemdescription","item_description","description","productname",
              "product_name","itemname","item_name","product","prodname"]:
        if c in df.columns:
            df.rename(columns={c: "item_description"}, inplace=True)
            break
    if "item_description" not in df.columns:
        df["item_description"] = df.get("item_code", "Unknown")

    # ── QUANTITY ────────────────────────────────
    for c in ["numberofitemspurchased","quantity","qty","units","count",
              "numitems","num_items","items","number_of_items","noofitems"]:
        if c in df.columns:
            df.rename(columns={c: "qty"}, inplace=True)
            break
    if "qty" not in df.columns:
        df["qty"] = 1  # default: 1 unit per transaction

    # ── COST / PRICE ────────────────────────────
    for c in ["costperitem","cost_per_item","price","unitprice","unit_price",
              "amount","tran_amount","tranamount","transamount","cost",
              "saleamount","sale_amount","value","revenue","total"]:
        if c in df.columns:
            df.rename(columns={c: "cost_per_item"}, inplace=True)
            break
    if "cost_per_item" not in df.columns:
        df["cost_per_item"] = 0.0

    # ── COUNTRY ─────────────────────────────────
    for c in ["country","region","market","location","territory","area"]:
        if c in df.columns:
            df.rename(columns={c: "country"}, inplace=True)
            break
    if "country" not in df.columns:
        df["country"] = "Unknown"

    return df


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    df = normalise_columns(df)

    # Validate we have a time column
    if "transaction_time" not in df.columns:
        available = list(df.columns)
        raise ValueError(
            f"Could not find a date/time column.\n"
            f"Columns in your CSV: {available}\n"
            f"Expected one of: TransactionTime, Date, trans_date, etc."
        )

    df["transaction_time"] = pd.to_datetime(df["transaction_time"], errors="coerce")
    df.dropna(subset=["transaction_time"], inplace=True)

    df["qty"]           = pd.to_numeric(df["qty"],           errors="coerce").fillna(1)
    df["cost_per_item"] = pd.to_numeric(df["cost_per_item"], errors="coerce").fillna(0)
    df = df[(df["qty"] > 0) & (df["cost_per_item"] > 0)]

    if len(df) == 0:
        raise ValueError("After cleaning, 0 valid rows remain. "
                         "Check that qty > 0 and cost_per_item > 0 in your CSV.")

    df["total_sales"]    = df["qty"] * df["cost_per_item"]
    df["txn_year"]       = df["transaction_time"].dt.year
    df["txn_month"]      = df["transaction_time"].dt.month
    df["txn_quarter"]    = df["transaction_time"].dt.quarter
    df["txn_dow"]        = df["transaction_time"].dt.day_name()
    df["txn_hour"]       = df["transaction_time"].dt.hour
    df["year_month"]     = df["transaction_time"].dt.to_period("M").astype(str)
    return df


# ══════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════
if "df"  not in st.session_state: st.session_state["df"]  = None
if "dfr" not in st.session_state: st.session_state["dfr"] = None

# Try loading from data/ folder automatically
if st.session_state["df"] is None:
    for fname in ["Retail_Data_Transactions.csv",
                  "retail_data_transactions.csv",
                  "transactions.csv"]:
        path = os.path.join("data", fname)
        if os.path.exists(path):
            try:
                st.session_state["df"] = clean_transactions(pd.read_csv(path))
                break
            except Exception:
                pass

    for rname in ["Retail_Data_Response.csv",
                  "retail_data_response.csv",
                  "response.csv"]:
        rpath = os.path.join("data", rname)
        if os.path.exists(rpath) and st.session_state["dfr"] is None:
            try:
                dfr = pd.read_csv(rpath)
                dfr.columns = dfr.columns.str.strip().str.lower().str.replace(" ","_")
                st.session_state["dfr"] = dfr
            except Exception:
                pass

# ══════════════════════════════════════════════
# UPLOAD GATE
# ══════════════════════════════════════════════
if st.session_state["df"] is None:
    st.markdown("""
    <div class="hero-header">
      <p class="hero-title">🛒 Retail Chain Sales Analytics</p>
      <p class="hero-sub">InternshipStudio Final Project · Upload your Kaggle data files below</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📂 Upload CSV Files from Kaggle")
    st.info("Dataset: **[Retail Transaction Data](https://www.kaggle.com/datasets/regivm/retailtransactiondata)** → download both CSV files and upload here.")

    c1, c2 = st.columns(2)
    with c1:
        t_file = st.file_uploader("📋 Retail_Data_Transactions.csv *(required)*", type="csv")
    with c2:
        r_file = st.file_uploader("👥 Retail_Data_Response.csv *(optional)*", type="csv")

    if t_file:
        with st.spinner("Loading and cleaning data…"):
            try:
                raw = pd.read_csv(t_file)
                st.session_state["df"] = clean_transactions(raw)
                if r_file:
                    dfr = pd.read_csv(r_file)
                    dfr.columns = dfr.columns.str.strip().str.lower().str.replace(" ","_")
                    st.session_state["dfr"] = dfr
                st.success(f"✅ Loaded {len(st.session_state['df']):,} records!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ {e}")
                st.markdown("**Your CSV columns:**")
                try:
                    raw2 = pd.read_csv(t_file)
                    st.write(list(raw2.columns))
                except Exception:
                    pass
    else:
        st.warning("⬆️ Upload Retail_Data_Transactions.csv to launch the dashboard.")
    st.stop()

# ══════════════════════════════════════════════
# DATA READY
# ══════════════════════════════════════════════
df  = st.session_state["df"]
dfr = st.session_state["dfr"]

# SIDEBAR
with st.sidebar:
    st.markdown("### 🛒 Retail Analytics")
    st.caption("InternshipStudio · Final Project")
    st.divider()
    st.markdown("#### 🔧 Filters")
    all_countries = sorted(df["country"].dropna().unique())
    sel_countries = st.multiselect("🌍 Country", all_countries, default=all_countries)
    all_years = sorted(df["txn_year"].dropna().unique().astype(int))
    sel_years = st.multiselect("📅 Year", all_years, default=all_years)
    st.divider()
    st.caption(f"📆 {df['transaction_time'].min().date()} → {df['transaction_time'].max().date()}")
    st.caption(f"📊 Records: {len(df):,}")
    st.caption(f"🌍 Countries: {df['country'].nunique()}")
    st.caption(f"📦 Products: {df['item_code'].nunique()}")
    st.divider()
    if st.button("🔄 Upload New Data"):
        st.session_state["df"]  = None
        st.session_state["dfr"] = None
        st.rerun()

fdf = df[df["country"].isin(sel_countries) & df["txn_year"].isin(sel_years)]
if len(fdf) == 0:
    st.warning("No data for current filters.")
    st.stop()

# HEADER
st.markdown("""
<div class="hero-header">
  <p class="hero-title">🛒 Retail Chain Sales Analytics Dashboard</p>
  <p class="hero-sub">InternshipStudio Final Project &nbsp;·&nbsp; Python · SQL · Excel &nbsp;·&nbsp; 6-Tab Intelligence Platform</p>
</div>""", unsafe_allow_html=True)

tabs = st.tabs(["📊 Overview","🌍 Geographic","📦 Products","📅 Time Trends","👥 Customers","🔍 SQL Lab"])

# ╔══════════════╗
# ║  TAB 1       ║
# ╚══════════════╝
with tabs[0]:
    st.markdown('<div class="section-title">📊 Executive Overview</div>', unsafe_allow_html=True)

    total_rev   = fdf["total_sales"].sum()
    total_txns  = fdf["transaction_id"].nunique()
    n_countries = fdf["country"].nunique()
    n_products  = fdf["item_code"].nunique()
    aov         = fdf.groupby("transaction_id")["total_sales"].sum().mean()
    avg_basket  = fdf.groupby("transaction_id")["qty"].sum().mean()

    cols = st.columns(6)
    for (label, val), col in zip([
        ("💰 Total Revenue",   f"${total_rev:,.0f}"),
        ("🧾 Transactions",    f"{total_txns:,}"),
        ("🌍 Countries",       f"{n_countries}"),
        ("📦 Products",        f"{n_products}"),
        ("🛒 Avg Order Value", f"${aov:,.2f}"),
        ("🛍️ Avg Basket",     f"{avg_basket:.1f} items"),
    ], cols):
        with col:
            st.markdown(f'<div class="kpi-card"><div class="kpi-value">{val}</div>'
                        f'<div class="kpi-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([2, 1])

    with left:
        monthly = fdf.groupby("year_month")["total_sales"].sum().reset_index().sort_values("year_month")
        fig = go.Figure(go.Scatter(
            x=monthly["year_month"], y=monthly["total_sales"],
            mode="lines", fill="tozeroy",
            line=dict(color="#42a5f5", width=2.5),
            fillcolor="rgba(66,165,245,0.15)"
        ))
        fig.update_layout(title="📈 Monthly Revenue Trend",
                          xaxis_tickangle=-45, xaxis_title="Month",
                          yaxis_title="Revenue ($)", **PT)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        cr = fdf.groupby("country")["total_sales"].sum().reset_index()\
               .sort_values("total_sales", ascending=False).head(8)
        fig2 = px.pie(cr, names="country", values="total_sales",
                      title="🌍 Revenue by Country", hole=0.45,
                      color_discrete_sequence=px.colors.sequential.Blues_r)
        fig2.update_layout(**PT)
        fig2.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">🏆 Top 5 Products</div>', unsafe_allow_html=True)
    top5 = (fdf.groupby(["item_code","item_description"])
               .agg(Revenue=("total_sales","sum"), Transactions=("transaction_id","count"),
                    Units=("qty","sum"), AvgPrice=("cost_per_item","mean"))
               .reset_index().sort_values("Revenue", ascending=False).head(5))
    top5["Revenue"]  = top5["Revenue"].apply(lambda x: f"${x:,.2f}")
    top5["AvgPrice"] = top5["AvgPrice"].apply(lambda x: f"${x:,.2f}")
    st.dataframe(top5, use_container_width=True, hide_index=True)

    top_country = fdf.groupby("country")["total_sales"].sum().idxmax()
    top_month   = monthly.loc[monthly["total_sales"].idxmax(), "year_month"]
    top_product = fdf.groupby("item_description")["total_sales"].sum().idxmax()
    st.markdown(f"""
    <div class="insight-box">💡 <strong>Top Market:</strong> {top_country} leads in total revenue.</div>
    <div class="insight-box">📅 <strong>Peak Month:</strong> {top_month} recorded highest monthly sales.</div>
    <div class="insight-box">📦 <strong>Star Product:</strong> "{top_product}" is the highest-grossing item.</div>
    """, unsafe_allow_html=True)


# ╔══════════════╗
# ║  TAB 2       ║
# ╚══════════════╝
with tabs[1]:
    st.markdown('<div class="section-title">🌍 Geographic Analysis</div>', unsafe_allow_html=True)
    geo = fdf.groupby("country").agg(
        Revenue=("total_sales","sum"), Transactions=("transaction_id","count"),
        Units=("qty","sum"), AOV=("total_sales","mean")
    ).reset_index().sort_values("Revenue", ascending=False)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(geo, x="country", y="Revenue", title="💰 Revenue by Country",
                     color="Revenue", color_continuous_scale="Blues", text_auto=".2s")
        fig.update_layout(xaxis_tickangle=-40, **PT)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig2 = px.bar(geo, x="country", y="Transactions", title="🧾 Transaction Volume",
                      color="Transactions", color_continuous_scale="Greens", text_auto=True)
        fig2.update_layout(xaxis_tickangle=-40, **PT)
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig3 = px.bar(geo, x="country", y="AOV", title="🛒 Avg Order Value",
                      color="AOV", color_continuous_scale="Oranges", text_auto=".2f")
        fig3.update_layout(xaxis_tickangle=-40, **PT)
        st.plotly_chart(fig3, use_container_width=True)
    with c4:
        fig4 = px.scatter(geo, x="Transactions", y="Revenue", size="Units",
                          color="country", text="country",
                          title="🔵 Revenue vs Volume", size_max=55)
        fig4.update_traces(textposition="top center")
        fig4.update_layout(**PT)
        st.plotly_chart(fig4, use_container_width=True)

    disp = geo.copy()
    disp["Revenue"] = disp["Revenue"].apply(lambda x: f"${x:,.2f}")
    disp["AOV"]     = disp["AOV"].apply(lambda x: f"${x:,.2f}")
    st.dataframe(disp, use_container_width=True, hide_index=True)


# ╔══════════════╗
# ║  TAB 3       ║
# ╚══════════════╝
with tabs[2]:
    st.markdown('<div class="section-title">📦 Product Performance</div>', unsafe_allow_html=True)
    prod = fdf.groupby(["item_code","item_description"]).agg(
        Revenue=("total_sales","sum"), Qty=("qty","sum"),
        Transactions=("transaction_id","count"), AvgPrice=("cost_per_item","mean")
    ).reset_index()

    top_n = st.slider("Show top N products", 5, 30, 15)
    c1, c2 = st.columns(2)
    with c1:
        dfp = prod.sort_values("Revenue", ascending=True).tail(top_n)
        fig = px.bar(dfp, x="Revenue", y="item_description", orientation="h",
                     title=f"💰 Top {top_n} — Revenue",
                     color="Revenue", color_continuous_scale="Blues", text_auto=".2s")
        fig.update_layout(yaxis_title="", height=500, **PT)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        dfq = prod.sort_values("Qty", ascending=True).tail(top_n)
        fig2 = px.bar(dfq, x="Qty", y="item_description", orientation="h",
                      title=f"📦 Top {top_n} — Units Sold",
                      color="Qty", color_continuous_scale="Greens", text_auto=True)
        fig2.update_layout(yaxis_title="", height=500, **PT)
        st.plotly_chart(fig2, use_container_width=True)

    # Pareto
    st.markdown('<div class="section-title">📐 Pareto — 80/20 Analysis</div>', unsafe_allow_html=True)
    pareto = prod.sort_values("Revenue", ascending=False).copy()
    pareto["cum_pct"] = pareto["Revenue"].cumsum() / pareto["Revenue"].sum() * 100
    top80 = len(pareto[pareto["cum_pct"] <= 80])
    st.markdown(f'<div class="insight-box">📐 Top <strong>{top80}</strong> of {len(pareto)} products = 80% of revenue.</div>', unsafe_allow_html=True)

    fig5 = go.Figure()
    fig5.add_trace(go.Bar(x=pareto.head(25)["item_description"],
                          y=pareto.head(25)["Revenue"],
                          name="Revenue", marker_color="#42a5f5"))
    fig5.add_trace(go.Scatter(x=pareto.head(25)["item_description"],
                              y=pareto.head(25)["cum_pct"],
                              mode="lines+markers", name="Cumulative %", yaxis="y2",
                              line=dict(color="#ffa726", width=2.5)))
    fig5.update_layout(title="Pareto Chart — Top 25",
                       yaxis=dict(title="Revenue ($)"),
                       yaxis2=dict(title="Cumulative %", overlaying="y", side="right",
                                   range=[0,105], ticksuffix="%"),
                       xaxis_tickangle=-45, **PT)
    st.plotly_chart(fig5, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig3 = px.histogram(fdf, x="cost_per_item", nbins=60,
                            title="Price Distribution", color_discrete_sequence=["#42a5f5"])
        fig3.update_layout(**PT)
        st.plotly_chart(fig3, use_container_width=True)
    with c4:
        fig4 = px.box(fdf, x="country", y="cost_per_item", color="country",
                      title="Price Spread by Country")
        fig4.update_layout(xaxis_tickangle=-40, showlegend=False, **PT)
        st.plotly_chart(fig4, use_container_width=True)


# ╔══════════════╗
# ║  TAB 4       ║
# ╚══════════════╝
with tabs[3]:
    st.markdown('<div class="section-title">📅 Temporal Sales Patterns</div>', unsafe_allow_html=True)
    dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

    c1, c2 = st.columns(2)
    with c1:
        dow = fdf.groupby("txn_dow")["total_sales"].sum().reindex(dow_order).reset_index()
        fig = px.bar(dow, x="txn_dow", y="total_sales", title="📅 Revenue by Day of Week",
                     color="total_sales", color_continuous_scale="Blues", text_auto=".2s")
        fig.update_layout(xaxis_title="", **PT)
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
        fig2.update_layout(title="⏰ Revenue by Hour",
                           xaxis_title="Hour", yaxis_title="Revenue ($)", **PT)
        st.plotly_chart(fig2, use_container_width=True)

    yoy = fdf.groupby(["txn_year","txn_month"])["total_sales"].sum().reset_index()
    yoy["year_str"] = yoy["txn_year"].astype(str)
    fig3 = px.line(yoy, x="txn_month", y="total_sales", color="year_str",
                   markers=True, title="📈 Year-over-Year Monthly Comparison",
                   labels={"txn_month":"Month","total_sales":"Revenue ($)","year_str":"Year"})
    fig3.update_xaxes(tickvals=list(range(1,13)),
                      ticktext=["Jan","Feb","Mar","Apr","May","Jun",
                                "Jul","Aug","Sep","Oct","Nov","Dec"])
    fig3.update_layout(**PT)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<div class="section-title">🔥 Sales Heatmap — Day × Hour</div>', unsafe_allow_html=True)
    heat = fdf.groupby(["txn_dow","txn_hour"])["total_sales"]\
              .sum().unstack(fill_value=0).reindex(dow_order)
    fig4 = px.imshow(heat, color_continuous_scale="Blues", aspect="auto",
                     labels=dict(x="Hour", y="Day", color="Revenue ($)"),
                     title="Sales Intensity Heatmap")
    fig4.update_layout(**PT)
    st.plotly_chart(fig4, use_container_width=True)

    peak_day  = dow.loc[dow["total_sales"].idxmax(), "txn_dow"]
    peak_hour = int(hour.loc[hour["total_sales"].idxmax(), "txn_hour"])
    st.markdown(f"""
    <div class="insight-box">⏰ <strong>Peak Day:</strong> {peak_day} generates the most revenue.</div>
    <div class="insight-box">🕐 <strong>Peak Hour:</strong> {peak_hour:02d}:00–{peak_hour+1:02d}:00 is the busiest window.</div>
    """, unsafe_allow_html=True)


# ╔══════════════╗
# ║  TAB 5       ║
# ╚══════════════╝
with tabs[4]:
    st.markdown('<div class="section-title">👥 Customer Intelligence</div>', unsafe_allow_html=True)

    if dfr is not None:
        # detect response column
        resp_col = None
        for c in ["response","responded","label","target","y"]:
            if c in dfr.columns:
                resp_col = c
                break

        if resp_col:
            total_cust = len(dfr)
            responded  = int(dfr[resp_col].sum())
            rate       = responded / total_cust * 100

            c1, c2, c3 = st.columns(3)
            with c1: st.metric("👥 Total Customers",    f"{total_cust:,}")
            with c2: st.metric("✅ Positive Responses", f"{responded:,}")
            with c3: st.metric("📊 Response Rate",      f"{rate:.1f}%")

            rc = pd.DataFrame({"Segment":["Responded","Did Not Respond"],
                               "Count":[responded, total_cust-responded]})
            c4, c5 = st.columns(2)
            with c4:
                fig = px.pie(rc, names="Segment", values="Count",
                             title="Campaign Response", hole=0.45,
                             color_discrete_sequence=["#42a5f5","#ef5350"])
                fig.update_layout(**PT)
                st.plotly_chart(fig, use_container_width=True)
            with c5:
                fig2 = px.bar(rc, x="Segment", y="Count", color="Segment",
                              title="Response Count",
                              color_discrete_sequence=["#42a5f5","#ef5350"])
                fig2.update_layout(showlegend=False, **PT)
                st.plotly_chart(fig2, use_container_width=True)

            st.markdown(f'<div class="insight-box">📬 {rate:.1f}% response rate. <strong>{total_cust-responded:,}</strong> customers are unconverted — prime re-engagement targets.</div>', unsafe_allow_html=True)
    else:
        st.info("📂 Upload Retail_Data_Response.csv for customer analysis.")

    st.markdown('<div class="section-title">💰 Transaction Value Distribution</div>', unsafe_allow_html=True)
    tv = fdf.groupby("transaction_id")["total_sales"].sum().reset_index()
    c6, c7 = st.columns(2)
    with c6:
        fig3 = px.histogram(tv, x="total_sales", nbins=80,
                            title="Transaction Value Distribution",
                            color_discrete_sequence=["#42a5f5"])
        fig3.update_layout(**PT)
        st.plotly_chart(fig3, use_container_width=True)
    with c7:
        fig4 = px.box(tv, y="total_sales", title="Box Plot",
                      color_discrete_sequence=["#ffa726"])
        fig4.update_layout(**PT)
        st.plotly_chart(fig4, use_container_width=True)

    pcts = tv["total_sales"].quantile([.25,.5,.75,.9,.95]).to_dict()
    st.markdown(f'<div class="insight-box">📊 P25: ${pcts[.25]:.2f} | Median: ${pcts[.5]:.2f} | P75: ${pcts[.75]:.2f} | P90: ${pcts[.9]:.2f} | P95: ${pcts[.95]:.2f}</div>', unsafe_allow_html=True)


# ╔══════════════╗
# ║  TAB 6       ║
# ╚══════════════╝
with tabs[5]:
    st.markdown('<div class="section-title">🔍 Interactive SQL Lab</div>', unsafe_allow_html=True)
    st.caption("Live queries against SQLite — identical logic to MySQL.")

    sql_conn = sqlite3.connect(":memory:", check_same_thread=False)
    df.to_sql("transactions", sql_conn, if_exists="replace", index=False)
    if dfr is not None:
        dfr.to_sql("customer_response", sql_conn, if_exists="replace", index=False)

    PRESETS = {
        "📦 Top 10 Products by Revenue": """SELECT item_description,
       ROUND(SUM(total_sales),2)       AS total_revenue,
       SUM(qty)                        AS units_sold,
       COUNT(DISTINCT transaction_id)  AS transactions,
       ROUND(AVG(cost_per_item),2)     AS avg_price
FROM transactions
GROUP BY item_description
ORDER BY total_revenue DESC LIMIT 10;""",

        "🌍 Revenue by Country": """SELECT country,
       COUNT(DISTINCT transaction_id)  AS transactions,
       ROUND(SUM(total_sales),2)       AS total_revenue,
       ROUND(AVG(total_sales),2)       AS avg_order_value
FROM transactions
GROUP BY country ORDER BY total_revenue DESC;""",

        "📅 Monthly Sales Trend": """SELECT year_month,
       COUNT(DISTINCT transaction_id)  AS transactions,
       ROUND(SUM(total_sales),2)       AS monthly_revenue
FROM transactions
GROUP BY year_month ORDER BY year_month;""",

        "⏰ Revenue by Hour": """SELECT txn_hour AS hour,
       COUNT(DISTINCT transaction_id)  AS transactions,
       ROUND(SUM(total_sales),2)       AS revenue
FROM transactions
GROUP BY txn_hour ORDER BY revenue DESC;""",

        "🔍 Data Quality Check": """SELECT
       COUNT(*)                        AS total_rows,
       COUNT(DISTINCT transaction_id)  AS unique_txns,
       COUNT(DISTINCT item_code)       AS products,
       COUNT(DISTINCT country)         AS countries,
       MIN(transaction_time)           AS first_date,
       MAX(transaction_time)           AS last_date,
       ROUND(MIN(cost_per_item),2)     AS min_price,
       ROUND(MAX(cost_per_item),2)     AS max_price,
       ROUND(AVG(cost_per_item),2)     AS avg_price,
       ROUND(SUM(total_sales),2)       AS grand_total
FROM transactions;""",

        "📐 Pareto Top 20": """SELECT item_description,
       ROUND(SUM(total_sales),2) AS revenue,
       ROUND(100.0*SUM(total_sales)/
         (SELECT SUM(total_sales) FROM transactions),2) AS pct_total
FROM transactions
GROUP BY item_description
ORDER BY revenue DESC LIMIT 20;"""
    }

    sel = st.selectbox("📋 Preset Query", list(PRESETS.keys()))
    sql_text = st.text_area("✏️ SQL Editor", value=PRESETS[sel], height=175)

    if st.button("▶️ Run Query", type="primary"):
        try:
            result = pd.read_sql(sql_text, sql_conn)
            st.success(f"✅ {len(result):,} rows returned")
            st.dataframe(result, use_container_width=True)
            num_cols  = result.select_dtypes("number").columns.tolist()
            text_cols = result.select_dtypes("object").columns.tolist()
            if text_cols and num_cols and len(result) > 1:
                fig = px.bar(result.head(20), x=text_cols[0], y=num_cols[0],
                             title=f"Auto-chart: {text_cols[0]} vs {num_cols[0]}",
                             color=num_cols[0], color_continuous_scale="Blues",
                             text_auto=".2s")
                fig.update_layout(xaxis_tickangle=-40, **PT)
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"❌ SQL Error: {e}")

    with st.expander("📋 Schema Reference"):
        st.markdown("""
| Column | Description |
|---|---|
| `transaction_id` | Unique ID |
| `transaction_time` | Full datetime |
| `item_code` | SKU |
| `item_description` | Product name |
| `qty` | Units |
| `cost_per_item` | Unit price |
| `country` | Market |
| `total_sales` | qty × price |
| `txn_year/month/dow/hour` | Time fields |
""")

st.divider()
c1, c2, c3 = st.columns(3)
with c1: st.caption("🛒 **Retail Chain Sales Analytics**")
with c2: st.caption("📊 InternshipStudio Final Project")
with c3: st.caption("⚙️ Python · SQLite · Streamlit · Plotly")