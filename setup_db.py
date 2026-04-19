"""
setup_db.py
═══════════════════════════════════════════════════════════════════
Retail Analytics — Database Setup & Data Export
Run once to:
  1. Load CSVs into SQLite (mimics MySQL DDL)
  2. Print summary statistics
  3. Export cleaned CSVs for Excel dashboard
═══════════════════════════════════════════════════════════════════
Usage:
    python setup_db.py
"""

import sqlite3
import pandas as pd
import os
import sys

DB_PATH            = "retail_analytics.db"
TRANSACTIONS_CSV   = "data/Retail_Data_Transactions.csv"
RESPONSE_CSV       = "data/Retail_Data_Response.csv"
EXPORTS_DIR        = "exports"

os.makedirs(EXPORTS_DIR, exist_ok=True)

print("=" * 60)
print("  RETAIL ANALYTICS — DATABASE SETUP")
print("=" * 60)


# ══════════════════════════════════════════════════════════════
# STEP 1: LOAD TRANSACTIONS
# ══════════════════════════════════════════════════════════════
print("\n[1/4] Loading transactions CSV …")

if not os.path.exists(TRANSACTIONS_CSV):
    sys.exit(f"❌  File not found: {TRANSACTIONS_CSV}\n"
             "    Please place the CSV in the data/ folder and re-run.")

df = pd.read_csv(TRANSACTIONS_CSV)
print(f"     Raw rows: {len(df):,}  |  Columns: {list(df.columns)}")

# Normalise column names
df.columns = (df.columns.str.strip()
                         .str.lower()
                         .str.replace(r"[\s\-]+", "_", regex=True))

renames = {}
for c in df.columns:
    cl = c.lower()
    if "transaction" in cl and "id"   in cl: renames[c] = "transaction_id"
    if "transaction" in cl and "time" in cl: renames[c] = "transaction_time"
    if "item"   in cl and "code" in cl:      renames[c] = "item_code"
    if "item"   in cl and "desc" in cl:      renames[c] = "item_description"
    if cl in ("numberofitemspurchased","qty","quantity","number_of_items_purchased"):
        renames[c] = "qty"
    if "cost" in cl and "per" in cl:         renames[c] = "cost_per_item"
    if cl == "country":                      renames[c] = "country"

df.rename(columns=renames, inplace=True)


# ══════════════════════════════════════════════════════════════
# STEP 2: CLEAN
# ══════════════════════════════════════════════════════════════
print("\n[2/4] Cleaning data …")

before = len(df)

# Datetime
# Safety: handle both possible column name formats
if "transactiontime" in df.columns:
    df.rename(columns={"transactiontime": "transaction_time"}, inplace=True)
if "transaction_time" not in df.columns:
    # Print actual columns to debug
    raise ValueError(f"Cannot find time column. Actual columns: {list(df.columns)}")

df["transaction_time"] = pd.to_datetime(df["transaction_time"], errors="coerce")
df.dropna(subset=["transaction_time"], inplace=True)

# Numeric coercion
df["qty"]           = pd.to_numeric(df.get("qty", 0),           errors="coerce").fillna(0)
df["cost_per_item"] = pd.to_numeric(df.get("cost_per_item", 0), errors="coerce").fillna(0)

# Remove invalid rows
df = df[(df["qty"] > 0) & (df["cost_per_item"] > 0)]

after = len(df)
print(f"     Removed {before - after:,} invalid/null rows  |  Clean rows: {after:,}")

# Null check
nulls = df.isnull().sum()
print(f"     Null counts:\n{nulls[nulls > 0].to_string() if nulls.any() else '     No nulls — data is clean ✔'}")


# ══════════════════════════════════════════════════════════════
# STEP 3: ENGINEER FEATURES
# ══════════════════════════════════════════════════════════════
print("\n[3/4] Engineering calculated fields …")

df["total_sales"]    = df["qty"] * df["cost_per_item"]
df["txn_year"]       = df["transaction_time"].dt.year
df["txn_month"]      = df["transaction_time"].dt.month
df["txn_month_name"] = df["transaction_time"].dt.strftime("%b")
df["txn_quarter"]    = df["transaction_time"].dt.quarter
df["txn_dow"]        = df["transaction_time"].dt.day_name()
df["txn_hour"]       = df["transaction_time"].dt.hour
df["year_month"]     = df["transaction_time"].dt.to_period("M").astype(str)

print(f"     Features added: total_sales, txn_year, txn_month, txn_quarter, txn_dow, txn_hour, year_month")


# ══════════════════════════════════════════════════════════════
# STEP 4: PERSIST TO SQLite  (MySQL-equivalent DDL shown below)
# ══════════════════════════════════════════════════════════════
print("\n[4/4] Writing to SQLite database …")

conn = sqlite3.connect(DB_PATH)
df.to_sql("transactions", conn, if_exists="replace", index=False)

if os.path.exists(RESPONSE_CSV):
    dfr = pd.read_csv(RESPONSE_CSV)
    dfr.columns = dfr.columns.str.strip().str.lower().str.replace(" ", "_")
    dfr.to_sql("customer_response", conn, if_exists="replace", index=False)
    print(f"     customer_response table: {len(dfr):,} rows")

conn.commit()


# ══════════════════════════════════════════════════════════════
# ANALYTICS SUMMARY (also saved to CSV for report)
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("  QUICK ANALYTICS SUMMARY")
print("=" * 60)

total_rev  = df["total_sales"].sum()
n_txns     = df["transaction_id"].nunique()
n_products = df["item_code"].nunique()
n_countries= df["country"].nunique()
aov        = df.groupby("transaction_id")["total_sales"].sum().mean()

print(f"\n  Total Revenue:        ${total_rev:,.2f}")
print(f"  Unique Transactions:  {n_txns:,}")
print(f"  Unique Products:      {n_products}")
print(f"  Countries:            {n_countries}")
print(f"  Avg Order Value:      ${aov:,.2f}")

print("\n  Top 5 Countries by Revenue:")
top_c = df.groupby("country")["total_sales"].sum().sort_values(ascending=False).head(5)
for c, v in top_c.items():
    print(f"    {c:<25} ${v:>12,.2f}")

print("\n  Top 5 Products by Revenue:")
top_p = df.groupby("item_description")["total_sales"].sum().sort_values(ascending=False).head(5)
for p, v in top_p.items():
    print(f"    {p[:40]:<42} ${v:>10,.2f}")


# ══════════════════════════════════════════════════════════════
# EXPORT CSVs FOR EXCEL DASHBOARD
# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("  EXPORTING CSVs FOR EXCEL DASHBOARD")
print("=" * 60)

# 1. Monthly summary
monthly = (df.groupby("year_month")
             .agg(Revenue=("total_sales","sum"),
                  Transactions=("transaction_id","count"),
                  Units_Sold=("qty","sum"))
             .reset_index())
monthly.to_csv(f"{EXPORTS_DIR}/monthly_summary.csv", index=False)

# 2. Country summary
country = (df.groupby("country")
             .agg(Revenue=("total_sales","sum"),
                  Transactions=("transaction_id","count"),
                  Units=("qty","sum"),
                  AOV=("total_sales","mean"))
             .reset_index().sort_values("Revenue", ascending=False))
country.to_csv(f"{EXPORTS_DIR}/country_summary.csv", index=False)

# 3. Product summary
product = (df.groupby(["item_code","item_description"])
             .agg(Revenue=("total_sales","sum"),
                  Units=("qty","sum"),
                  Transactions=("transaction_id","count"),
                  AvgPrice=("cost_per_item","mean"))
             .reset_index().sort_values("Revenue", ascending=False))
product.to_csv(f"{EXPORTS_DIR}/product_summary.csv", index=False)

# 4. DOW summary
dow = (df.groupby("txn_dow")
         .agg(Revenue=("total_sales","sum"),
              Transactions=("transaction_id","count"))
         .reset_index())
dow.to_csv(f"{EXPORTS_DIR}/dow_summary.csv", index=False)

# 5. Cleaned full dataset (for Excel pivot tables)
df.to_csv(f"{EXPORTS_DIR}/cleaned_transactions.csv", index=False)

print(f"\n  ✅ Exported to '{EXPORTS_DIR}/' folder:")
print("     monthly_summary.csv")
print("     country_summary.csv")
print("     product_summary.csv")
print("     dow_summary.csv")
print("     cleaned_transactions.csv  ← import into Excel for pivot tables")


# ══════════════════════════════════════════════════════════════
# MYSQL EQUIVALENT DDL (for documentation / submission)
# ══════════════════════════════════════════════════════════════
mysql_ddl = """
-- ═══════════════════════════════════════════════════════════
-- MySQL DDL (equivalent schema — used as SQLite on Replit)
-- ═══════════════════════════════════════════════════════════

CREATE DATABASE IF NOT EXISTS retail_analytics;
USE retail_analytics;

CREATE TABLE IF NOT EXISTS transactions (
    id                INTEGER      AUTO_INCREMENT PRIMARY KEY,
    transaction_id    VARCHAR(50)  NOT NULL,
    transaction_time  DATETIME     NOT NULL,
    item_code         VARCHAR(50),
    item_description  VARCHAR(255),
    qty               INT          NOT NULL CHECK (qty > 0),
    cost_per_item     DECIMAL(10,2) NOT NULL CHECK (cost_per_item > 0),
    country           VARCHAR(100),
    total_sales       DECIMAL(12,2) GENERATED ALWAYS AS (qty * cost_per_item) STORED,
    txn_year          SMALLINT,
    txn_month         TINYINT,
    txn_month_name    VARCHAR(10),
    txn_quarter       TINYINT,
    txn_dow           VARCHAR(15),
    txn_hour          TINYINT,
    year_month        VARCHAR(8),
    INDEX idx_country  (country),
    INDEX idx_item     (item_code),
    INDEX idx_time     (transaction_time),
    INDEX idx_txnid    (transaction_id)
);

CREATE TABLE IF NOT EXISTS customer_response (
    customer_id   VARCHAR(50) PRIMARY KEY,
    response      TINYINT NOT NULL  -- 1 = Positive, 0 = Negative
);
"""

with open(f"{EXPORTS_DIR}/mysql_schema.sql", "w") as f:
    f.write(mysql_ddl)
print("\n  ✅ MySQL DDL saved to exports/mysql_schema.sql")

conn.close()
print("\n✅ Database setup complete. Run:  streamlit run app.py\n")
