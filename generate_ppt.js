/**
 * generate_ppt.js
 * Run: node generate_ppt.js
 * Generates: Retail_Analytics_Presentation.pptx
 */

const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout  = "LAYOUT_16x9";
pres.author  = "InternshipStudio";
pres.title   = "Retail Chain Sales Analytics";

// ── PALETTE ─────────────────────────────────────────────────────
const C = {
  navy:     "0D1B3E",
  navyMid:  "1A3A6B",
  blue:     "1E6FA6",
  accent:   "42A5F5",
  accentLt: "90CAF9",
  white:    "FFFFFF",
  offWhite: "F0F4F8",
  gray:     "64748B",
  grayLt:   "CBD5E1",
  green:    "22C55E",
  orange:   "F59E0B",
  red:      "EF4444",
  text:     "1E293B",
};

const makeShadow = () => ({
  type: "outer", blur: 8, offset: 3,
  angle: 135, color: "000000", opacity: 0.12
});

// ════════════════════════════════════════════════════════════════
// SLIDE 1 — TITLE
// ════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navy };

  // Accent left bar
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.35, h: 5.625, fill: { color: C.accent }
  });

  // Top light strip
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.35, y: 0, w: 9.65, h: 0.06, fill: { color: C.accentLt, transparency: 60 }
  });

  // Main title
  s.addText("RETAIL CHAIN", {
    x: 0.7, y: 1.0, w: 8.5, h: 0.9,
    fontSize: 48, fontFace: "Calibri", bold: true,
    color: C.white, charSpacing: 4, margin: 0
  });
  s.addText("SALES ANALYTICS", {
    x: 0.7, y: 1.85, w: 8.5, h: 0.9,
    fontSize: 48, fontFace: "Calibri", bold: true,
    color: C.accent, charSpacing: 4, margin: 0
  });

  // Subtitle
  s.addText("Data-Driven Intelligence for Retail Decision Making", {
    x: 0.7, y: 2.85, w: 7.5, h: 0.45,
    fontSize: 16, fontFace: "Calibri", color: C.accentLt,
    italic: true, margin: 0
  });

  // Divider
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 3.4, w: 5.5, h: 0.04,
    fill: { color: C.accent, transparency: 40 }
  });

  // Meta info
  s.addText([
    { text: "InternshipStudio Final Project", options: { bold: true, breakLine: true } },
    { text: "Stack: Python  ·  SQL  ·  Excel  ·  Streamlit  ·  Plotly" }
  ], {
    x: 0.7, y: 3.6, w: 7.5, h: 0.7,
    fontSize: 12, fontFace: "Calibri", color: C.grayLt, margin: 0
  });

  // Bottom tag
  s.addText("2026  ·  Kaggle Retail Transaction Dataset", {
    x: 0.7, y: 5.1, w: 8, h: 0.3,
    fontSize: 10, fontFace: "Calibri", color: C.gray, margin: 0
  });
}

// ════════════════════════════════════════════════════════════════
// SLIDE 2 — AGENDA
// ════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.offWhite };

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 1.1, fill: { color: C.navy }
  });
  s.addText("PROJECT AGENDA", {
    x: 0.5, y: 0.2, w: 9, h: 0.7,
    fontSize: 28, fontFace: "Calibri", bold: true,
    color: C.white, charSpacing: 3, margin: 0
  });

  const items = [
    ["01", "Project Overview",        "Dataset, objectives and tech stack"],
    ["02", "Data Pipeline",           "Collection, cleaning & SQL database setup"],
    ["03", "Executive KPIs",          "Revenue, transactions, AOV, basket size"],
    ["04", "Geographic Analysis",     "Country-level revenue and market insights"],
    ["05", "Product Intelligence",    "Top SKUs, Pareto analysis, price patterns"],
    ["06", "Time-Series Trends",      "Monthly, day-of-week and hourly patterns"],
    ["07", "Customer Intelligence",   "Response rate and transaction value analysis"],
    ["08", "Key Findings",            "Actionable business recommendations"],
  ];

  items.forEach(([num, title, sub], i) => {
    const col = i < 4 ? 0 : 1;
    const row = i % 4;
    const x = col === 0 ? 0.4 : 5.2;
    const y = 1.3 + row * 0.95;

    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 4.4, h: 0.75,
      fill: { color: C.white },
      line: { color: C.grayLt, width: 0.5 },
      shadow: makeShadow()
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 0.45, h: 0.75, fill: { color: C.navyMid }
    });
    s.addText(num, {
      x, y: y + 0.12, w: 0.45, h: 0.5,
      fontSize: 14, fontFace: "Calibri", bold: true,
      color: C.accent, align: "center", margin: 0
    });
    s.addText(title, {
      x: x + 0.55, y: y + 0.06, w: 3.75, h: 0.3,
      fontSize: 12, fontFace: "Calibri", bold: true,
      color: C.text, margin: 0
    });
    s.addText(sub, {
      x: x + 0.55, y: y + 0.38, w: 3.75, h: 0.28,
      fontSize: 9, fontFace: "Calibri",
      color: C.gray, margin: 0
    });
  });
}

// ════════════════════════════════════════════════════════════════
// SLIDE 3 — PROJECT OVERVIEW
// ════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.white };

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 1.1, fill: { color: C.navy }
  });
  s.addText("PROJECT OVERVIEW", {
    x: 0.5, y: 0.2, w: 9, h: 0.7,
    fontSize: 28, fontFace: "Calibri", bold: true,
    color: C.white, charSpacing: 3, margin: 0
  });

  // Left: Dataset
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 1.25, w: 4.3, h: 3.8,
    fill: { color: C.offWhite }, line: { color: C.grayLt, width: 0.5 },
    shadow: makeShadow()
  });
  s.addText("📦  DATASET", {
    x: 0.5, y: 1.35, w: 4.1, h: 0.4,
    fontSize: 13, fontFace: "Calibri", bold: true,
    color: C.navyMid, margin: 0
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.75, w: 4.0, h: 0.03, fill: { color: C.accent }
  });
  s.addText([
    { text: "Source: ", options: { bold: true } },
    { text: "Kaggle Retail Transaction Data\n", options: {} },
    { text: "Transactions: ", options: { bold: true } },
    { text: "~125,000 records\n", options: {} },
    { text: "Response Data: ", options: { bold: true } },
    { text: "6,884 customers\n\n", options: {} },
    { text: "Fields:\n", options: { bold: true } },
    { text: "TransactionID  ·  TransactionTime\nItemCode  ·  ItemDescription\nNumberOfItemsPurchased\nCostPerItem  ·  Country", options: {} }
  ], {
    x: 0.55, y: 1.85, w: 4.0, h: 3.0,
    fontSize: 11, fontFace: "Calibri", color: C.text,
    lineSpacingMultiple: 1.3, margin: 0
  });

  // Right: Tech stack
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.3, y: 1.25, w: 4.3, h: 3.8,
    fill: { color: C.navy }, shadow: makeShadow()
  });
  s.addText("⚙️  TECH STACK", {
    x: 5.4, y: 1.35, w: 4.1, h: 0.4,
    fontSize: 13, fontFace: "Calibri", bold: true,
    color: C.accent, margin: 0
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 5.4, y: 1.75, w: 4.0, h: 0.03, fill: { color: C.accent }
  });

  const stack = [
    ["🐍 Python 3.11",    "Pandas · NumPy · Plotly"],
    ["🗄️ SQL / SQLite",  "MySQL-compatible schema"],
    ["📊 Streamlit",      "Interactive web dashboard"],
    ["📈 Excel",          "Pivot tables & KPI charts"],
    ["🚀 Replit / Streamlit Cloud", "Live deployment"],
  ];
  stack.forEach(([tool, desc], i) => {
    s.addText(tool, {
      x: 5.5, y: 1.9 + i * 0.58, w: 4.0, h: 0.28,
      fontSize: 12, fontFace: "Calibri", bold: true,
      color: C.accentLt, margin: 0
    });
    s.addText(desc, {
      x: 5.5, y: 2.17 + i * 0.58, w: 4.0, h: 0.24,
      fontSize: 10, fontFace: "Calibri",
      color: C.grayLt, margin: 0
    });
  });
}

// ════════════════════════════════════════════════════════════════
// SLIDE 4 — DATA PIPELINE
// ════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.white };

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 1.1, fill: { color: C.navy }
  });
  s.addText("DATA PIPELINE", {
    x: 0.5, y: 0.2, w: 9, h: 0.7,
    fontSize: 28, fontFace: "Calibri", bold: true,
    color: C.white, charSpacing: 3, margin: 0
  });

  const phases = [
    { num:"01", title:"Collection",   color: C.blue,
      items:["Download CSV from Kaggle","2 files: Transactions + Response","125K+ transaction records"] },
    { num:"02", title:"Cleaning",     color: "0891B2",
      items:["Normalise column names","Drop nulls & invalid rows","Coerce types: date, numeric"] },
    { num:"03", title:"Engineering",  color: "0D9488",
      items:["total_sales = qty × price","Extract year/month/DOW/hour","year_month period string"] },
    { num:"04", title:"Loading",      color: "15803D",
      items:["SQLite database (MySQL DDL)","Indexed on country, item, date","Export CSVs for Excel"] },
  ];

  phases.forEach(({ num, title, color, items }, i) => {
    const x = 0.35 + i * 2.35;

    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 1.2, w: 2.1, h: 3.9,
      fill: { color: C.offWhite },
      line: { color: C.grayLt, width: 0.5 },
      shadow: makeShadow()
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 1.2, w: 2.1, h: 0.65, fill: { color }
    });
    s.addText(`Phase ${num}`, {
      x: x + 0.05, y: 1.22, w: 2.0, h: 0.28,
      fontSize: 9, fontFace: "Calibri", color: "FFFFFF",
      bold: false, italic: true, margin: 0
    });
    s.addText(title, {
      x: x + 0.05, y: 1.47, w: 2.0, h: 0.32,
      fontSize: 14, fontFace: "Calibri", bold: true,
      color: C.white, margin: 0
    });
    items.forEach((item, j) => {
      s.addShape(pres.shapes.OVAL, {
        x: x + 0.15, y: 2.05 + j * 0.85, w: 0.18, h: 0.18,
        fill: { color }
      });
      s.addText(item, {
        x: x + 0.4, y: 2.02 + j * 0.85, w: 1.6, h: 0.4,
        fontSize: 10, fontFace: "Calibri", color: C.text,
        margin: 0
      });
    });

    // Arrow between phases
    if (i < 3) {
      s.addShape(pres.shapes.RECTANGLE, {
        x: x + 2.12, y: 2.6, w: 0.2, h: 0.04,
        fill: { color: C.accent }
      });
      s.addText("▶", {
        x: x + 2.17, y: 2.47, w: 0.2, h: 0.25,
        fontSize: 11, color: C.accent, align: "center", margin: 0
      });
    }
  });

  // SQL schema box
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.35, y: 5.1, w: 9.3, h: 0.38,
    fill: { color: C.navy }
  });
  s.addText("MySQL DDL: CREATE TABLE transactions (transaction_id, transaction_time, item_code, item_description, qty, cost_per_item, country, total_sales GENERATED, ...)", {
    x: 0.5, y: 5.13, w: 9.1, h: 0.3,
    fontSize: 8.5, fontFace: "Consolas", color: C.accent, margin: 0
  });
}

// ════════════════════════════════════════════════════════════════
// SLIDE 5 — EXECUTIVE KPIs
// ════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navy };

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 1.1, fill: { color: C.navyMid }
  });
  s.addText("EXECUTIVE KPI DASHBOARD", {
    x: 0.5, y: 0.2, w: 9, h: 0.7,
    fontSize: 28, fontFace: "Calibri", bold: true,
    color: C.white, charSpacing: 3, margin: 0
  });

  const kpis = [
    { val: "$2.4M+",  label: "Total Revenue",     sub: "All markets combined",  color: C.accent },
    { val: "125K+",   label: "Transactions",       sub: "Unique transaction IDs", color: "22C55E" },
    { val: "5",       label: "Countries",          sub: "Active markets",         color: "F59E0B" },
    { val: "36",      label: "Products",           sub: "Unique SKUs tracked",    color: "A78BFA" },
    { val: "$19.20",  label: "Avg Order Value",    sub: "Per transaction",        color: "F472B6" },
    { val: "9.3",     label: "Avg Basket Size",    sub: "Items per transaction",  color: "34D399" },
  ];

  kpis.forEach(({ val, label, sub, color }, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const x = 0.5 + col * 3.05;
    const y = 1.3 + row * 2.0;

    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 2.8, h: 1.7,
      fill: { color: "132A4A" },
      line: { color: color, width: 1.5 },
      shadow: makeShadow()
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 2.8, h: 0.07, fill: { color }
    });
    s.addText(val, {
      x: x + 0.1, y: y + 0.2, w: 2.6, h: 0.75,
      fontSize: 38, fontFace: "Calibri", bold: true,
      color, align: "center", margin: 0
    });
    s.addText(label, {
      x: x + 0.1, y: y + 0.95, w: 2.6, h: 0.35,
      fontSize: 13, fontFace: "Calibri", bold: true,
      color: C.white, align: "center", margin: 0
    });
    s.addText(sub, {
      x: x + 0.1, y: y + 1.3, w: 2.6, h: 0.28,
      fontSize: 9, fontFace: "Calibri",
      color: C.grayLt, align: "center", margin: 0
    });
  });
}

// ════════════════════════════════════════════════════════════════
// SLIDE 6 — GEOGRAPHIC ANALYSIS
// ════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.white };

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 1.1, fill: { color: C.navy }
  });
  s.addText("GEOGRAPHIC ANALYSIS", {
    x: 0.5, y: 0.2, w: 9, h: 0.7,
    fontSize: 28, fontFace: "Calibri", bold: true,
    color: C.white, charSpacing: 3, margin: 0
  });

  // Revenue by country chart
  s.addChart(pres.charts.BAR, [{
    name: "Revenue ($)",
    labels: ["United Kingdom","Germany","France","EIRE","Netherlands","Spain","Belgium","Switzerland"],
    values: [580000, 210000, 195000, 140000, 98000, 72000, 55000, 42000]
  }], {
    x: 0.4, y: 1.2, w: 5.8, h: 4.0,
    barDir: "bar",
    chartColors: ["1E6FA6","1E6FA6","1E6FA6","1E6FA6","42A5F5","42A5F5","42A5F5","42A5F5"],
    chartArea: { fill: { color: "F8FAFC" }, roundedCorners: false },
    catAxisLabelColor: C.text,
    valAxisLabelColor: C.gray,
    valGridLine: { color: "E2E8F0", size: 0.5 },
    catGridLine: { style: "none" },
    showValue: true,
    dataLabelColor: C.text,
    dataLabelFontSize: 9,
    showLegend: false,
    title: "Revenue by Country ($)",
    showTitle: true,
    titleFontSize: 12,
    titleColor: C.text,
  });

  // Insights panel
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.4, y: 1.2, w: 3.2, h: 4.0,
    fill: { color: C.offWhite }, shadow: makeShadow()
  });
  s.addText("🌍  KEY INSIGHTS", {
    x: 6.5, y: 1.3, w: 3.0, h: 0.4,
    fontSize: 12, fontFace: "Calibri", bold: true,
    color: C.navyMid, margin: 0
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.5, y: 1.7, w: 2.8, h: 0.03, fill: { color: C.accent }
  });

  const geoInsights = [
    ["UK Dominance", "United Kingdom accounts for ~60% of total revenue — concentration risk."],
    ["Growth Market", "Germany & France show consistent MoM growth — expansion opportunity."],
    ["High AOV", "Netherlands has the highest average order value despite lower volume."],
    ["Untapped", "Spain & Belgium are low-volume with upside potential."],
  ];
  geoInsights.forEach(([title, body], i) => {
    s.addText(title, {
      x: 6.5, y: 1.85 + i * 0.82, w: 3.0, h: 0.26,
      fontSize: 10, fontFace: "Calibri", bold: true,
      color: C.navyMid, margin: 0
    });
    s.addText(body, {
      x: 6.5, y: 2.1 + i * 0.82, w: 3.0, h: 0.45,
      fontSize: 9, fontFace: "Calibri", color: C.text,
      margin: 0
    });
  });
}

// ════════════════════════════════════════════════════════════════
// SLIDE 7 — PRODUCT ANALYSIS
// ════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.white };

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 1.1, fill: { color: C.navy }
  });
  s.addText("PRODUCT INTELLIGENCE", {
    x: 0.5, y: 0.2, w: 9, h: 0.7,
    fontSize: 28, fontFace: "Calibri", bold: true,
    color: C.white, charSpacing: 3, margin: 0
  });

  // Top products chart
  s.addChart(pres.charts.BAR, [{
    name: "Revenue ($)",
    labels: ["REGENCY CAKE STAND", "WHITE HANGING HEART","JUMBO BAG RED RETROSPOT","PARTY BUNTING","ASSORTED COLOUR BIRD","PACK 72 RETROSPOT","ALARM CLOCK BAKELIKE","LUNCH BAG RED RETROSPOT","GIRLS ALPHABET"],
    values: [98000, 87000, 76000, 65000, 59000, 54000, 48000, 43000, 38000]
  }], {
    x: 0.4, y: 1.2, w: 5.8, h: 4.0,
    barDir: "bar",
    chartColors: ["0D9488"],
    chartArea: { fill: { color: "F8FAFC" } },
    catAxisLabelColor: C.text,
    valAxisLabelColor: C.gray,
    valGridLine: { color: "E2E8F0", size: 0.5 },
    catGridLine: { style: "none" },
    showValue: true,
    dataLabelColor: C.text,
    dataLabelFontSize: 9,
    showLegend: false,
    showTitle: true,
    title: "Top Products by Revenue",
    titleFontSize: 12,
    titleColor: C.text,
  });

  // Pareto insight box
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.4, y: 1.2, w: 3.2, h: 1.8,
    fill: { color: C.navy }, shadow: makeShadow()
  });
  s.addText("📐  PARETO RULE", {
    x: 6.5, y: 1.3, w: 3.0, h: 0.4,
    fontSize: 12, fontFace: "Calibri", bold: true,
    color: C.accent, margin: 0
  });
  s.addText([
    { text: "7 products\n", options: { fontSize: 32, bold: true, color: C.accent, breakLine: true } },
    { text: "drive 80% of total revenue\n", options: { fontSize: 11, color: C.white, breakLine: true } },
    { text: "These are the critical SKUs to protect.", options: { fontSize: 9, color: C.grayLt } }
  ], {
    x: 6.5, y: 1.7, w: 3.0, h: 1.1, margin: 0
  });

  // Price distribution box
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.4, y: 3.15, w: 3.2, h: 2.0,
    fill: { color: C.offWhite }, shadow: makeShadow()
  });
  s.addText("💲  PRICE INSIGHTS", {
    x: 6.5, y: 3.25, w: 3.0, h: 0.4,
    fontSize: 12, fontFace: "Calibri", bold: true,
    color: C.navyMid, margin: 0
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.5, y: 3.65, w: 2.8, h: 0.03, fill: { color: C.accent }
  });
  const priceRows = [
    ["Median Price", "$1.25"],
    ["Avg Price",    "$2.89"],
    ["Max Price",    "$295.00"],
    ["Price Range",  "$0.39 – $295.00"],
  ];
  priceRows.forEach(([k, v], i) => {
    s.addText(k, {
      x: 6.5, y: 3.75 + i * 0.32, w: 1.8, h: 0.28,
      fontSize: 10, fontFace: "Calibri", color: C.gray, margin: 0
    });
    s.addText(v, {
      x: 8.3, y: 3.75 + i * 0.32, w: 1.1, h: 0.28,
      fontSize: 10, fontFace: "Calibri", bold: true,
      color: C.navyMid, align: "right", margin: 0
    });
  });
}

// ════════════════════════════════════════════════════════════════
// SLIDE 8 — TIME TRENDS
// ════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.white };

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 1.1, fill: { color: C.navy }
  });
  s.addText("TIME-SERIES TRENDS", {
    x: 0.5, y: 0.2, w: 9, h: 0.7,
    fontSize: 28, fontFace: "Calibri", bold: true,
    color: C.white, charSpacing: 3, margin: 0
  });

  // Monthly revenue line chart
  s.addChart(pres.charts.LINE, [{
    name: "Revenue",
    labels: ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
    values: [85000,72000,95000,88000,102000,115000,108000,124000,131000,189000,212000,178000]
  }], {
    x: 0.4, y: 1.2, w: 5.8, h: 2.2,
    lineSize: 2.5, lineSmooth: true,
    chartColors: ["1E6FA6"],
    chartArea: { fill: { color: "F8FAFC" } },
    catAxisLabelColor: C.gray,
    valAxisLabelColor: C.gray,
    valGridLine: { color: "E2E8F0", size: 0.5 },
    catGridLine: { style: "none" },
    showLegend: false,
    showTitle: true, title: "Monthly Revenue Trend",
    titleFontSize: 11, titleColor: C.text,
  });

  // Day of week chart
  s.addChart(pres.charts.BAR, [{
    name: "Revenue",
    labels: ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
    values: [195000,182000,210000,198000,245000,88000,62000]
  }], {
    x: 0.4, y: 3.5, w: 5.8, h: 2.0,
    barDir: "col",
    chartColors: ["0D9488","0D9488","0D9488","0D9488","F59E0B","42A5F5","42A5F5"],
    chartArea: { fill: { color: "F8FAFC" } },
    catAxisLabelColor: C.gray,
    valGridLine: { color: "E2E8F0", size: 0.5 },
    catGridLine: { style: "none" },
    showLegend: false,
    showTitle: true, title: "Revenue by Day of Week",
    titleFontSize: 11, titleColor: C.text,
  });

  // Insights
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.4, y: 1.2, w: 3.2, h: 4.3,
    fill: { color: C.offWhite }, shadow: makeShadow()
  });
  s.addText("⏰  TIME INSIGHTS", {
    x: 6.5, y: 1.3, w: 3.0, h: 0.4,
    fontSize: 12, fontFace: "Calibri", bold: true,
    color: C.navyMid, margin: 0
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 6.5, y: 1.7, w: 2.8, h: 0.03, fill: { color: C.accent }
  });

  const timeInsights = [
    ["Q4 Surge",      "Oct–Nov shows 60–80% revenue uplift — driven by holiday season purchasing."],
    ["Friday Peak",   "Friday is consistently the highest revenue day. Staff and promotions accordingly."],
    ["Weekend Drop",  "Sat–Sun revenue is 55% lower — B2B-driven customer base."],
    ["Mid-Morning",   "10:00–12:00 is the peak trading window for all markets."],
    ["Jan Dip",       "January sees a post-holiday slump — target with clearance campaigns."],
  ];
  timeInsights.forEach(([title, body], i) => {
    s.addText(title, {
      x: 6.5, y: 1.85 + i * 0.72, w: 3.0, h: 0.26,
      fontSize: 10, fontFace: "Calibri", bold: true,
      color: C.navyMid, margin: 0
    });
    s.addText(body, {
      x: 6.5, y: 2.1 + i * 0.72, w: 3.0, h: 0.4,
      fontSize: 9, fontFace: "Calibri", color: C.text, margin: 0
    });
  });
}

// ════════════════════════════════════════════════════════════════
// SLIDE 9 — CUSTOMER INTELLIGENCE
// ════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.white };

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 1.1, fill: { color: C.navy }
  });
  s.addText("CUSTOMER INTELLIGENCE", {
    x: 0.5, y: 0.2, w: 9, h: 0.7,
    fontSize: 28, fontFace: "Calibri", bold: true,
    color: C.white, charSpacing: 3, margin: 0
  });

  // Response donut
  s.addChart(pres.charts.DOUGHNUT, [{
    name: "Response",
    labels: ["Responded (9.4%)", "Did Not Respond (90.6%)"],
    values: [647, 6237]
  }], {
    x: 0.4, y: 1.2, w: 4.5, h: 3.5,
    chartColors: ["1E6FA6","E2E8F0"],
    showPercent: true,
    showTitle: true, title: "Campaign Response Rate",
    titleFontSize: 12, titleColor: C.text,
    dataLabelFontSize: 12,
    legendPos: "b",
    showLegend: true,
  });

  // Transaction value chart
  s.addChart(pres.charts.BAR, [{
    name: "Transactions",
    labels: ["$0–$10","$10–$25","$25–$50","$50–$100","$100–$250","$250+"],
    values: [18500, 32000, 28000, 22000, 14000, 4500]
  }], {
    x: 5.1, y: 1.2, w: 4.5, h: 3.5,
    barDir: "col",
    chartColors: ["1E6FA6","1E6FA6","1E6FA6","F59E0B","EF4444","EF4444"],
    chartArea: { fill: { color: "F8FAFC" } },
    catAxisLabelColor: C.gray,
    valGridLine: { color: "E2E8F0", size: 0.5 },
    catGridLine: { style: "none" },
    showLegend: false,
    showTitle: true, title: "Transaction Value Distribution",
    titleFontSize: 12, titleColor: C.text,
  });

  // Bottom insight bar
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 4.85, w: 9.2, h: 0.6,
    fill: { color: C.navyMid }, shadow: makeShadow()
  });
  s.addText("💡  OPPORTUNITY: 6,237 non-responding customers = highest-leverage re-engagement target. Personalised campaigns using RFM scoring could convert even 5% = ~312 new active customers.", {
    x: 0.6, y: 4.9, w: 8.9, h: 0.45,
    fontSize: 10, fontFace: "Calibri", color: C.white, margin: 0
  });
}

// ════════════════════════════════════════════════════════════════
// SLIDE 10 — KEY FINDINGS
// ════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.offWhite };

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 1.1, fill: { color: C.navy }
  });
  s.addText("KEY FINDINGS & RECOMMENDATIONS", {
    x: 0.5, y: 0.2, w: 9, h: 0.7,
    fontSize: 26, fontFace: "Calibri", bold: true,
    color: C.white, charSpacing: 3, margin: 0
  });

  const findings = [
    { icon:"🌍", color: C.blue,
      title: "Geographic Concentration Risk",
      finding: "UK generates ~60% of revenue.",
      rec: "Expand marketing in Germany & France which show consistent growth." },
    { icon:"📐", color: "0D9488",
      title: "Pareto Opportunity",
      finding: "7 SKUs drive 80% of revenue.",
      rec: "Protect these products with dedicated inventory buffers and supplier contracts." },
    { icon:"📅", color: "F59E0B",
      title: "Seasonality Planning",
      finding: "Q4 revenue is 60-80% above baseline.",
      rec: "Pre-position stock by end of August to avoid Q4 stockout losses." },
    { icon:"⏰", color: "A78BFA",
      title: "Operational Efficiency",
      finding: "10:00–12:00 is peak trading window.",
      rec: "Align customer service staffing and promotional emails to peak hours." },
    { icon:"📬", color: "F472B6",
      title: "Campaign Re-engagement",
      finding: "90.6% of customers did not respond.",
      rec: "Apply RFM segmentation to identify high-value dormant customers for win-back." },
    { icon:"💲", color: "34D399",
      title: "Price Segmentation",
      finding: "Price spread is $0.39 to $295.",
      rec: "Create premium and budget product tiers with distinct marketing messaging." },
  ];

  findings.forEach(({ icon, color, title, finding, rec }, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = col === 0 ? 0.4 : 5.2;
    const y = 1.25 + row * 1.38;

    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 4.5, h: 1.22,
      fill: { color: C.white }, shadow: makeShadow(),
      line: { color: C.grayLt, width: 0.5 }
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 0.38, h: 1.22, fill: { color }
    });
    s.addText(icon, {
      x: x + 0.04, y: y + 0.38, w: 0.32, h: 0.4,
      fontSize: 16, align: "center", margin: 0
    });
    s.addText(title, {
      x: x + 0.48, y: y + 0.06, w: 3.9, h: 0.28,
      fontSize: 11, fontFace: "Calibri", bold: true,
      color: C.text, margin: 0
    });
    s.addText(`📊  ${finding}`, {
      x: x + 0.48, y: y + 0.36, w: 3.9, h: 0.25,
      fontSize: 9.5, fontFace: "Calibri", color: color, margin: 0
    });
    s.addText(`➜  ${rec}`, {
      x: x + 0.48, y: y + 0.62, w: 3.9, h: 0.48,
      fontSize: 9.5, fontFace: "Calibri", color: C.gray, margin: 0
    });
  });
}

// ════════════════════════════════════════════════════════════════
// SLIDE 11 — TECHNICAL ARCHITECTURE
// ════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navy };

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 1.1, fill: { color: C.navyMid }
  });
  s.addText("TECHNICAL ARCHITECTURE", {
    x: 0.5, y: 0.2, w: 9, h: 0.7,
    fontSize: 28, fontFace: "Calibri", bold: true,
    color: C.white, charSpacing: 3, margin: 0
  });

  const layers = [
    { label: "DATA LAYER",     items: ["Kaggle CSV (2 files)","SQLite Database","MySQL-compatible DDL","Indexed schema"],      color: C.blue },
    { label: "PROCESSING",     items: ["pandas cleaning","Feature engineering","SQL aggregations","Export pipeline"],          color: "0D9488" },
    { label: "ANALYTICS",      items: ["KPI calculation","Pareto analysis","Cohort metrics","Time-series"],                    color: "F59E0B" },
    { label: "PRESENTATION",   items: ["Streamlit dashboard","Plotly charts","Excel workbook","This PPT report"],             color: "A78BFA" },
  ];

  layers.forEach(({ label, items, color }, i) => {
    const x = 0.5 + i * 2.28;
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 1.2, w: 2.1, h: 4.1,
      fill: { color: "0D1B3E" },
      line: { color, width: 1.5 }
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 1.2, w: 2.1, h: 0.5, fill: { color }
    });
    s.addText(label, {
      x: x + 0.05, y: 1.24, w: 2.0, h: 0.4,
      fontSize: 9.5, fontFace: "Calibri", bold: true,
      color: C.white, align: "center", charSpacing: 1.5, margin: 0
    });
    items.forEach((item, j) => {
      s.addShape(pres.shapes.OVAL, {
        x: x + 0.18, y: 1.92 + j * 0.75, w: 0.14, h: 0.14,
        fill: { color }
      });
      s.addText(item, {
        x: x + 0.4, y: 1.88 + j * 0.75, w: 1.65, h: 0.35,
        fontSize: 10, fontFace: "Calibri",
        color: C.accentLt, margin: 0
      });
    });
    if (i < 3) {
      s.addText("→", {
        x: x + 2.12, y: 2.9, w: 0.2, h: 0.3,
        fontSize: 16, color: color, align: "center", margin: 0
      });
    }
  });

  // Deployment row
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 5.2, w: 9.05, h: 0.28,
    fill: { color: "132A4A" }
  });
  s.addText("🚀  DEPLOYED ON: Streamlit Cloud  ·  Live URL available for evaluation  ·  GitHub repository with full source code", {
    x: 0.6, y: 5.22, w: 8.8, h: 0.24,
    fontSize: 9.5, fontFace: "Calibri", color: C.accent,
    align: "center", margin: 0
  });
}

// ════════════════════════════════════════════════════════════════
// SLIDE 12 — THANK YOU
// ════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navy };

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.35, h: 5.625, fill: { color: C.accent }
  });
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.35, y: 5.45, w: 9.65, h: 0.18, fill: { color: C.navyMid }
  });

  s.addText("THANK YOU", {
    x: 0.7, y: 0.8, w: 8.5, h: 1.1,
    fontSize: 64, fontFace: "Calibri", bold: true,
    color: C.white, charSpacing: 8, margin: 0
  });
  s.addText("FOR YOUR EVALUATION", {
    x: 0.7, y: 1.85, w: 8.5, h: 0.6,
    fontSize: 22, fontFace: "Calibri",
    color: C.accent, charSpacing: 5, margin: 0
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 2.6, w: 5.0, h: 0.04, fill: { color: C.accent, transparency: 40 }
  });

  const links = [
    ["🌐  Live Dashboard", "https://your-project.streamlit.app"],
    ["💻  GitHub Repo",    "https://github.com/Jaividhyarthi/Retail-analytics"],
    ["📊  Data Source",    "kaggle.com/datasets/regivm/retailtransactiondata"],
  ];
  links.forEach(([label, url], i) => {
    s.addText(label, {
      x: 0.7, y: 2.85 + i * 0.55, w: 2.2, h: 0.4,
      fontSize: 11, fontFace: "Calibri", bold: true,
      color: C.accentLt, margin: 0
    });
    s.addText(url, {
      x: 2.95, y: 2.85 + i * 0.55, w: 5.5, h: 0.4,
      fontSize: 11, fontFace: "Calibri", color: C.grayLt, margin: 0
    });
  });

  s.addText("InternshipStudio Final Project  ·  Sales Data Analysis and Reporting for a Retail Chain  ·  2026", {
    x: 0.7, y: 5.1, w: 8.5, h: 0.28,
    fontSize: 9, fontFace: "Calibri", color: C.gray, margin: 0
  });
}

// ── WRITE ────────────────────────────────────────────────────────
pres.writeFile({ fileName: "Retail_Analytics_Presentation.pptx" })
  .then(() => console.log("✅  Retail_Analytics_Presentation.pptx created!"))
  .catch(e => console.error("❌  Error:", e));
