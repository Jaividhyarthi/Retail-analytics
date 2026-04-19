# 🛒 Retail Chain Sales Analytics
### InternshipStudio Final Project

> **Stack:** Python · SQLite (MySQL-compatible) · Streamlit · Plotly · Excel  
> **Deployed on:** Replit

---

## 🚀 Quick Start on Replit

### 1. Upload your data
Create a folder called `data/` in the Replit file tree and upload:
- `Retail_Data_Transactions.csv`
- `Retail_Data_Response.csv`

### 2. Install dependencies
Replit handles this automatically via `requirements.txt`. If not:
```bash
pip install -r requirements.txt
```

### 3. (Optional) Run DB setup separately
```bash
python setup_db.py
```
This creates the database AND exports CSVs to `exports/` for your Excel dashboard.

### 4. Launch the dashboard
Click the **Run** button on Replit, or:
```bash
streamlit run app.py --server.port 8080 --server.headless true
```

---

## 📂 Project Structure

```
retail_project/
├── app.py                  ← Main Streamlit dashboard (6 tabs)
├── setup_db.py             ← DB initialisation + CSV export script
├── requirements.txt        ← Python dependencies
├── .replit                 ← Replit run configuration
├── REPORT.md               ← Full project report
├── data/
│   ├── Retail_Data_Transactions.csv   ← Upload here
│   └── Retail_Data_Response.csv       ← Upload here
├── exports/                ← Auto-generated after setup_db.py
│   ├── cleaned_transactions.csv
│   ├── monthly_summary.csv
│   ├── country_summary.csv
│   ├── product_summary.csv
│   ├── dow_summary.csv
│   └── mysql_schema.sql
└── retail_analytics.db     ← Auto-generated SQLite database
```

---

## 📊 Dashboard Tabs

| Tab | What it shows |
|-----|--------------|
| 📊 Overview | KPIs, revenue trend, top products, key insights |
| 🌍 Geographic | Revenue/volume/AOV by country |
| 📦 Products | Top N products, price distribution, Pareto chart |
| 📅 Time Trends | Day-of-week, hourly, year-over-year, heatmap |
| 👥 Customers | Response funnel, transaction value distribution |
| 🔍 SQL Lab | Live SQL query editor with auto-visualization |

---

## 📋 Excel Dashboard

After running `python setup_db.py`, import `exports/cleaned_transactions.csv` into Excel.  
See **Section 7** of `REPORT.md` for full step-by-step pivot table + chart instructions.

---

## 🗄️ MySQL Schema

For production MySQL deployment, see `exports/mysql_schema.sql`.

---

*InternshipStudio Final Project · Sales Data Analysis and Reporting for a Retail Chain*
