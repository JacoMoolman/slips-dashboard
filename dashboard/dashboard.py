"""
Monthly Spending Dashboard
Run: streamlit run G:/SLIPS/dashboard/dashboard.py
"""

import json
import io
from pathlib import Path
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATA_DIR = Path(__file__).parent / "data"
HEADER_IMAGE = Path(__file__).parent / "assets" / "jm2-dashboard-masthead.png"

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="JM² Shopping Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Light is deliberately the first-visit default, independent of the device's
# system theme. Streamlit re-runs the script after the user changes the toggle,
# so the palette and every Plotly chart update together.
st.session_state.setdefault("dark_mode", False)

THEMES = {
    "light": {
        "color_scheme": "light",
        "page": "#f6f7fb",
        "surface": "#ffffff",
        "surface_alt": "#eef2f7",
        "sidebar": "#edf1f6",
        "text": "#111827",
        "muted": "#475569",
        "border": "#d6dce7",
        "grid": "#dfe4ec",
        "input": "#ffffff",
        "button": "#ffffff",
        "button_hover": "#e9eef6",
    },
    "dark": {
        "color_scheme": "dark",
        "page": "#0d0f1a",
        "surface": "#171a2d",
        "surface_alt": "#1e2340",
        "sidebar": "#13162a",
        "text": "#f4f6ff",
        "muted": "#aeb8d4",
        "border": "#2a3155",
        "grid": "#2a3155",
        "input": "#171a2d",
        "button": "#1e2340",
        "button_hover": "#2a3155",
    },
}

ACTIVE_THEME = THEMES["dark" if st.session_state["dark_mode"] else "light"]

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    color-scheme: %(color_scheme)s;
    font-family: 'Inter', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: %(page)s;
    color: %(text)s;
}
[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"],
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] {
    color: %(text)s;
}
[data-testid="stSidebar"] {
    background: %(sidebar)s;
    border-right: 1px solid %(border)s;
}
[data-testid="stSidebar"] * { color: %(text)s !important; }
[data-testid="stHeader"] { background: %(page)s; }
[data-testid="stToolbar"] { color: %(text)s; }
[data-testid="stPopover"] > button {
    width: 100%%;
    min-height: 42px;
    background: %(surface)s !important;
    color: %(text)s !important;
    border: 1px solid %(border)s !important;
    border-radius: 10px !important;
}
[data-testid="stPopover"] > button:hover {
    background: %(button_hover)s !important;
    border-color: #5b78e5 !important;
}
[data-testid="stAppViewContainer"] .block-container {
    max-width: 100%%;
    padding-left: clamp(0.75rem, 3vw, 3rem);
    padding-right: clamp(0.75rem, 3vw, 3rem);
}
.block-container { overflow-x: hidden; }

hr { border-color: %(border)s !important; }

[data-baseweb="select"] > div,
[data-testid="stTextInput"] input,
[data-testid="stPassword"] input {
    background: %(input)s !important;
    color: %(text)s !important;
    border-color: %(border)s !important;
}
[data-baseweb="tag"] { background: %(surface_alt)s !important; }
[data-baseweb="tag"] span { color: %(text)s !important; }

/* Streamlit 1.62+ multiselects use React Aria instead of BaseWeb. */
[data-testid="stMultiSelect"] .react-aria-ComboBox {
    max-height: 7.5rem;
}
[data-testid="stMultiSelect"] .react-aria-ComboBox > [role="group"] {
    min-height: 42px !important;
    max-height: 7.5rem !important;
    background: %(surface)s !important;
    color: %(text)s !important;
    border: 1px solid %(border)s !important;
    border-radius: 10px !important;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
    overflow: hidden !important;
    transition: border-color 140ms ease, box-shadow 140ms ease;
}
[data-testid="stMultiSelect"] .react-aria-ComboBox > [role="group"]:focus-within {
    border-color: #5b78e5 !important;
    box-shadow: 0 0 0 3px rgba(91, 120, 229, 0.16);
}
[data-testid="stMultiSelectTagsContainer"] {
    max-height: 7.35rem !important;
    overflow-y: auto !important;
    scrollbar-width: thin;
    scrollbar-color: %(border)s transparent;
}
[data-testid="stMultiSelect"] [data-tag] {
    background: %(surface_alt)s !important;
    color: %(text)s !important;
    border: 1px solid %(border)s !important;
    border-radius: 999px !important;
}
[data-testid="stMultiSelect"] [data-tag] span,
[data-testid="stMultiSelect"] [data-tag] button,
[data-testid="stMultiSelect"] input,
[data-testid="stMultiSelect"] button[aria-label="Clear all"],
[data-testid="stMultiSelect"] button[aria-label="Open"] {
    color: %(text)s !important;
}
[data-testid="stMultiSelect"] [data-tag]:hover {
    background: %(button_hover)s !important;
}
[data-testid="stMultiSelect"] button[aria-label="Clear all"],
[data-testid="stMultiSelect"] button[aria-label="Open"] {
    background: transparent !important;
}
div:has(> [role="listbox"]) {
    background: %(surface)s !important;
    color: %(text)s !important;
    border-color: %(border)s !important;
    border-radius: 10px !important;
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.14) !important;
}
[role="listbox"],
[role="listbox"] [role="option"] {
    color: %(text)s !important;
}
[role="listbox"] [role="option"]:hover,
[role="listbox"] [role="option"][aria-selected="true"] {
    background: %(surface_alt)s !important;
}
button[kind="secondary"],
[data-testid="stDownloadButton"] button,
[data-testid="stFormSubmitButton"] button {
    background: %(button)s !important;
    color: %(text)s !important;
    border-color: %(border)s !important;
}
button[kind="secondary"]:hover,
[data-testid="stDownloadButton"] button:hover,
[data-testid="stFormSubmitButton"] button:hover {
    background: %(button_hover)s !important;
    border-color: #5b78e5 !important;
}
[data-testid="stDataFrame"] {
    border: 1px solid %(border)s;
    border-radius: 10px;
    overflow: hidden;
}

.dashboard-title {
    color: %(text)s;
    font-size: clamp(2rem, 7vw, 3.2rem);
    font-weight: 700;
    line-height: 1.05;
    margin: 0 0 1.1rem;
    overflow-wrap: anywhere;
}
.dashboard-title span {
    display: block;
    color: %(muted)s;
    font-size: 0.78em;
    margin-top: 0.25rem;
}
[data-testid="stImage"] {
    max-width: 720px;
    margin: 0 auto;
}
[data-testid="stImage"] img {
    width: 100%%;
    height: auto;
    display: block;
}
.brand-month {
    margin: 0.15rem 0 1.45rem;
    color: %(muted)s;
    font-size: clamp(1.05rem, 2.4vw, 1.35rem);
    font-weight: 700;
    letter-spacing: 0.14em;
    line-height: 1.2;
    text-align: center;
}
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}
h1 {
    font-size: clamp(2rem, 7vw, 3.2rem) !important;
    line-height: 1.08 !important;
    overflow-wrap: anywhere;
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(145px, 1fr));
    gap: 12px;
    margin-bottom: 24px;
}
.kpi-card {
    min-width: 0;
    background: %(surface)s;
    border: 1px solid %(border)s;
    border-radius: 12px;
    padding: 16px 14px;
    text-align: center;
    animation: fadeUp 0.5s ease both;
}
.kpi-card:nth-child(1) { animation-delay: 0.0s; border-top: 3px solid #6c8aff; }
.kpi-card:nth-child(2) { animation-delay: 0.1s; border-top: 3px solid #4ecdc4; }
.kpi-card:nth-child(3) { animation-delay: 0.2s; border-top: 3px solid #f7b731; }
.kpi-card:nth-child(4) { animation-delay: 0.3s; border-top: 3px solid #fc5c7d; }
.kpi-card:nth-child(5) { animation-delay: 0.4s; border-top: 3px solid #6bcb77; }

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

.kpi-value {
    font-size: clamp(1.35rem, 6vw, 1.8rem);
    font-weight: 700;
    color: %(text)s;
    line-height: 1.1;
    margin-bottom: 4px;
    overflow-wrap: anywhere;
}
.kpi-label {
    font-size: clamp(0.64rem, 2.6vw, 0.78rem);
    color: %(muted)s;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}

.section-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: %(muted)s;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 24px 0 8px;
    padding-bottom: 6px;
    border-bottom: 1px solid %(border)s;
}

.chart-card {
    background: %(surface)s;
    border: 1px solid %(border)s;
    border-radius: 14px;
    padding: 16px;
}

@media (max-width: 640px) {
    [data-testid="stAppViewContainer"] .block-container {
        padding-top: 4.5rem;
        padding-left: 0.75rem;
        padding-right: 0.75rem;
    }
    .dashboard-title {
        font-size: 2rem;
        line-height: 1.08;
        margin-bottom: 0.85rem;
    }
    h1 { font-size: 2rem !important; }
    .kpi-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
    }
    .kpi-card {
        min-height: 116px;
        padding: 14px 10px;
    }
    .section-title {
        margin-top: 18px;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
    }
}

@media (max-width: 380px) {
    .kpi-grid { grid-template-columns: 1fr; }
}
</style>
""" % ACTIVE_THEME, unsafe_allow_html=True)

# ── Colour palette per category ───────────────────────────────────────────────
CATEGORY_COLORS = {
    "Produce":           "#6bcb77",
    "Meat & Deli":       "#fc5c7d",
    "Dairy & Eggs":      "#f7b731",
    "Pantry & Dry Goods":"#ff9f43",
    "Snacks & Treats":   "#e056fd",
    "Beverages":         "#4ecdc4",
    "Household":         "#6c8aff",
    "Health & Beauty":   "#48dbfb",
    "Vegetables":        "#a4b0d4",
    "Fruit":             "#8f9bbd",
    "Other":             "#7a85aa",
}

STORE_COLORS = {
    "Woolworths":   "#00b16a",
    "Pick n Pay":   "#e84393",
    "Checkers":     "#f39c12",
    "Dis-Chem":     "#3498db",
    "Clicks":       "#e74c3c",
}

INTERACTIVE_CHART_CONFIG = {"displayModeBar": False, "scrollZoom": False}


def plotly_layout(**overrides):
    layout = dict(
        template="none",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=ACTIVE_THEME["text"], family="Inter"),
        margin=dict(t=20, b=20, l=10, r=10),
        dragmode=False,
        hoverlabel=dict(
            bgcolor=ACTIVE_THEME["surface"],
            bordercolor=ACTIVE_THEME["border"],
            font=dict(color=ACTIVE_THEME["text"], size=13),
        ),
    )
    layout.update(overrides)
    return layout


# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_all_data():
    item_rows, slip_rows = [], []
    for jf in sorted(DATA_DIR.glob("*.json")):
        with open(jf) as f:
            data = json.load(f)
        for slip in data.get("slips", []):
            slip_rows.append({
                "month":     slip.get("month", data["month"]),
                "date":      slip.get("date", ""),
                "store":     slip.get("store", "Unknown"),
                "total":     float(slip.get("total", 0) or 0),
                "discounts": float(slip.get("discounts", 0) or 0),
                "source_file": slip.get("source_file", ""),
            })
            for item in slip.get("items", []):
                item_rows.append({
                    "month":       slip.get("month", data["month"]),
                    "date":        slip.get("date", ""),
                    "store":       slip.get("store", "Unknown"),
                    "description": item.get("description", ""),
                    "price":       float(item.get("price", 0) or 0),
                    "category":    item.get("category", "Other"),
                })
    df_s = pd.DataFrame(slip_rows)
    df_i = pd.DataFrame(item_rows)
    if not df_s.empty:
        df_s["date"] = pd.to_datetime(df_s["date"], errors="coerce")
    if not df_i.empty:
        df_i["date"] = pd.to_datetime(df_i["date"], errors="coerce")
    return df_s, df_i


# ── Filters ───────────────────────────────────────────────────────────────────
def build_filters(df_s, df_i):
    with st.popover("Filters", use_container_width=True):
        months = sorted(df_s["month"].unique(), reverse=True)
        sel_months = st.multiselect("Month", months, default=months[:1])
        if not sel_months:
            sel_months = months

        stores = sorted(df_s["store"].unique())
        sel_stores = st.multiselect("Store", stores, default=stores)
        if not sel_stores:
            sel_stores = stores

        cats = sorted(df_i["category"].unique())
        sel_cats = st.multiselect("Category", cats, default=cats)
        if not sel_cats:
            sel_cats = cats

    return sel_months, sel_stores, sel_cats


# ── Charts ────────────────────────────────────────────────────────────────────
def chart_category_donut(df_i):
    agg = df_i.groupby("category")["price"].sum().reset_index()
    agg = agg.sort_values("price", ascending=False)
    colors = [CATEGORY_COLORS.get(c, "#7a85aa") for c in agg["category"]]
    fig = go.Figure(go.Pie(
        labels=agg["category"],
        values=agg["price"],
        hole=0.55,
        marker=dict(colors=colors, line=dict(color=ACTIVE_THEME["page"], width=2)),
        textinfo="percent",
        textposition="inside",
        insidetextorientation="radial",
        hovertemplate="<b>%{label}</b><br>R %{value:,.2f}<br>%{percent}<extra></extra>",
        textfont=dict(size=11),
    ))
    fig.update_layout(**plotly_layout(
        height=330,
        showlegend=True,
        margin=dict(t=8, b=80, l=4, r=4),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.08,
            xanchor="left",
            x=0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=ACTIVE_THEME["text"], size=10),
        ),
        uniformtext_minsize=10,
        uniformtext_mode="hide",
    ))
    return fig


def chart_store_bar(df_s):
    agg = df_s.groupby("store")["total"].sum().reset_index().sort_values("total")
    xmax = float(agg["total"].max()) if not agg.empty else 1.0
    colors = [STORE_COLORS.get(s, "#7a85aa") for s in agg["store"]]
    fig = go.Figure(go.Bar(
        x=agg["total"], y=agg["store"], orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"R {v:,.0f}" for v in agg["total"]],
        textposition="outside",
        textfont=dict(color=ACTIVE_THEME["text"]),
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>R %{x:,.2f}<extra></extra>",
    ))
    fig.update_layout(**plotly_layout(
        height=max(320, 34 * len(agg) + 130),
        margin=dict(t=10, b=42, l=8, r=80),
        xaxis=dict(showgrid=True, gridcolor=ACTIVE_THEME["grid"], tickformat=",.0f", title="Amount (R)", color=ACTIVE_THEME["muted"], range=[0, xmax * 1.25], fixedrange=True),
        yaxis=dict(showgrid=False, color=ACTIVE_THEME["text"], automargin=True, fixedrange=True),
    ))
    return fig


def chart_monthly_trend(df_s_all, sel_stores):
    agg = (df_s_all[df_s_all["store"].isin(sel_stores)]
           .groupby("month")["total"].sum()
           .reset_index().sort_values("month"))
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=agg["month"], y=agg["total"],
        mode="lines+markers+text",
        line=dict(color="#6c8aff", width=3),
        marker=dict(size=9, color="#6c8aff", line=dict(color=ACTIVE_THEME["page"], width=2)),
        text=[f"R {v:,.0f}" for v in agg["total"]],
        textposition="top center",
        textfont=dict(color=ACTIVE_THEME["text"], size=11),
        cliponaxis=False,
        fill="tozeroy",
        fillcolor="rgba(108,138,255,0.08)",
        hovertemplate="<b>%{x}</b><br>R %{y:,.2f}<extra></extra>",
    ))
    fig.update_layout(**plotly_layout(
        height=260,
        margin=dict(t=34, b=42, l=54, r=54),
        xaxis=dict(
            type="category",
            categoryorder="array",
            categoryarray=agg["month"].tolist(),
            range=[-0.35, len(agg) - 0.65],
            showgrid=True,
            gridcolor=ACTIVE_THEME["grid"],
            color=ACTIVE_THEME["muted"],
            fixedrange=True,
        ),
        yaxis=dict(showgrid=True, gridcolor=ACTIVE_THEME["grid"], tickformat=",.0f", title="R", color=ACTIVE_THEME["muted"], fixedrange=True),
    ))
    return fig


def chart_category_by_month(df_i):
    pivot = df_i.pivot_table(
        values="price",
        index="month",
        columns="category",
        aggfunc="sum",
        fill_value=0,
    ).sort_index()
    months = pivot.index.astype(str).tolist()
    category_order = [c for c in CATEGORY_COLORS if c in pivot.columns]
    category_order.extend(sorted(c for c in pivot.columns if c not in category_order))

    fig = go.Figure()
    for cat in category_order:
        fig.add_trace(go.Scatter(
            name=cat,
            x=months,
            y=pivot[cat].tolist(),
            mode="lines+markers",
            line=dict(color=CATEGORY_COLORS.get(cat, "#7a85aa"), width=3),
            marker=dict(size=8, color=CATEGORY_COLORS.get(cat, "#7a85aa"), line=dict(color=ACTIVE_THEME["page"], width=2)),
            hovertemplate=f"<b>{cat}</b><br>%{{x}}<br>R %{{y:,.2f}}<extra></extra>",
        ))

    fig.update_layout(**plotly_layout(
        height=max(360, 38 * len(category_order) + 260),
        margin=dict(t=28, b=72, l=64, r=28),
        xaxis=dict(
            type="category",
            categoryorder="array",
            categoryarray=months,
            showgrid=True,
            gridcolor=ACTIVE_THEME["grid"],
            color=ACTIVE_THEME["text"],
            fixedrange=True,
        ),
        yaxis=dict(showgrid=True, gridcolor=ACTIVE_THEME["grid"], tickformat=",.0f", title="R", color=ACTIVE_THEME["muted"], fixedrange=True),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor="rgba(0,0,0,0)",
            bordercolor=ACTIVE_THEME["border"],
            font=dict(color=ACTIVE_THEME["text"], size=10),
        ),
    ))
    return fig


def chart_stacked_store_cat(df_i):
    pivot = (df_i.pivot_table(values="price", index="store", columns="category", aggfunc="sum", fill_value=0)
             .reset_index())
    pivot["store_label"] = pivot["store"].str.replace(" & ", " &<br>", regex=False)
    fig = go.Figure()
    cats_present = [c for c in CATEGORY_COLORS if c in df_i["category"].unique()]
    for cat in cats_present:
        if cat in pivot.columns:
            fig.add_trace(go.Bar(
                name=cat, x=pivot["store_label"], y=pivot[cat],
                customdata=pivot["store"],
                marker_color=CATEGORY_COLORS[cat],
                hovertemplate=f"<b>{cat}</b><br>%{{customdata}}<br>R %{{y:,.2f}}<extra></extra>",
            ))
    fig.update_layout(**plotly_layout(
        barmode="stack",
        height=max(420, 36 * len(pivot) + 280),
        margin=dict(t=28, b=120, l=64, r=28),
        xaxis=dict(showgrid=False, color=ACTIVE_THEME["text"], tickfont=dict(size=11), automargin=True, fixedrange=True),
        yaxis=dict(showgrid=True, gridcolor=ACTIVE_THEME["grid"], tickformat=",.0f", title="R", color=ACTIVE_THEME["muted"], fixedrange=True),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor="rgba(0,0,0,0)",
            bordercolor=ACTIVE_THEME["border"],
            font=dict(color=ACTIVE_THEME["text"], size=10),
        ),
    ))
    return fig


# ── PDF export ────────────────────────────────────────────────────────────────
def generate_pdf(df_s, df_i, months):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "Monthly Spending Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Period: {', '.join(months)}", ln=True, align="C")
    pdf.cell(0, 7, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
    pdf.ln(6)

    # KPIs
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 9, "Summary", ln=True)
    pdf.set_font("Helvetica", "", 10)
    total_spend = df_s["total"].sum()
    pdf.cell(0, 6, f"Total Spent:          R {total_spend:,.2f}", ln=True)
    pdf.cell(0, 6, f"Shopping Trips:       {df_s.shape[0]}", ln=True)
    pdf.cell(0, 6, f"Items Purchased:      {df_i.shape[0]}", ln=True)
    pdf.cell(0, 6, f"Avg per Trip:         R {total_spend / max(df_s.shape[0], 1):,.2f}", ln=True)
    pdf.cell(0, 6, f"Total Saved:          R {df_s['discounts'].sum():,.2f}", ln=True)
    pdf.ln(4)

    # By category
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 9, "Spending by Category", ln=True)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(110, 7, "Category", border=1)
    pdf.cell(40, 7, "Amount", border=1)
    pdf.cell(40, 7, "% of Total", border=1, ln=True)
    pdf.set_font("Helvetica", "", 9)
    cat_agg = df_i.groupby("category")["price"].sum().sort_values(ascending=False)
    for cat, amt in cat_agg.items():
        pct = amt / df_i["price"].sum() * 100
        pdf.cell(110, 6, str(cat), border=1)
        pdf.cell(40, 6, f"R {amt:,.2f}", border=1)
        pdf.cell(40, 6, f"{pct:.1f}%", border=1, ln=True)
    pdf.ln(4)

    # By store
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 9, "Spending by Store", ln=True)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(110, 7, "Store", border=1)
    pdf.cell(40, 7, "Amount", border=1)
    pdf.cell(40, 7, "Trips", border=1, ln=True)
    pdf.set_font("Helvetica", "", 9)
    store_agg = df_s.groupby("store").agg(total=("total", "sum"), trips=("total", "count"))
    store_agg = store_agg.sort_values("total", ascending=False)
    for store, row in store_agg.iterrows():
        pdf.cell(110, 6, str(store), border=1)
        pdf.cell(40, 6, f"R {row['total']:,.2f}", border=1)
        pdf.cell(40, 6, str(row["trips"]), border=1, ln=True)

    return bytes(pdf.output())


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if not DATA_DIR.exists() or not list(DATA_DIR.glob("*.json")):
        st.error("No shopping data found.")
        st.stop()

    df_s_all, df_i_all = load_all_data()
    if df_s_all.empty:
        st.error("No data found.")
        st.stop()

    theme_col, filters_col = st.columns(2)
    with theme_col:
        st.toggle(
            "Dark mode",
            key="dark_mode",
            help="Light mode is the default. Turn this on for the dark theme.",
        )
    with filters_col:
        sel_months, sel_stores, sel_cats = build_filters(df_s_all, df_i_all)

    mask_s = df_s_all["month"].isin(sel_months) & df_s_all["store"].isin(sel_stores)
    mask_i = (df_i_all["month"].isin(sel_months) &
              df_i_all["store"].isin(sel_stores) &
              df_i_all["category"].isin(sel_cats))
    df_s = df_s_all[mask_s]
    df_i = df_i_all[mask_i]

    # ── Masthead ───────────────────────────────────────────────────────────────
    month_label = ", ".join(sel_months) if sel_months else "All months"
    st.image(str(HEADER_IMAGE), use_container_width=True)
    st.markdown(
        f'<h1 class="sr-only">JM² Shopping Dashboard — {month_label}</h1>'
        f'<div class="brand-month">{month_label}</div>',
        unsafe_allow_html=True,
    )

    # ── KPI cards ─────────────────────────────────────────────────────────────
    total_spend  = df_s["total"].sum()
    total_trips  = len(df_s)
    total_items  = len(df_i)
    avg_trip     = total_spend / max(total_trips, 1)
    total_saved  = df_s["discounts"].sum()

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-value">R {total_spend:,.0f}</div>
        <div class="kpi-label">Total Spent</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-value">{total_trips}</div>
        <div class="kpi-label">Shopping Trips</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-value">{total_items}</div>
        <div class="kpi-label">Items Purchased</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-value">R {avg_trip:,.0f}</div>
        <div class="kpi-label">Avg per Trip</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-value">R {total_saved:,.0f}</div>
        <div class="kpi-label">Total Saved</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Row 1: Donut + Store bar ───────────────────────────────────────────────
    st.markdown('<div class="section-title">Breakdown</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**By Category**")
        if not df_i.empty:
            st.plotly_chart(chart_category_donut(df_i), use_container_width=True, theme=None, config=INTERACTIVE_CHART_CONFIG)
        else:
            st.info("No item data for selection.")
    with col2:
        st.markdown("**By Store**")
        if not df_s.empty:
            st.plotly_chart(chart_store_bar(df_s), use_container_width=True, theme=None, config=INTERACTIVE_CHART_CONFIG)
        else:
            st.info("No store data.")

    # ── Monthly trend (if multiple months exist) ──────────────────────────────
    all_months = sorted(df_s_all["month"].unique())
    if len(all_months) > 1:
        st.markdown('<div class="section-title">Monthly Trend</div>', unsafe_allow_html=True)
        st.plotly_chart(chart_monthly_trend(df_s_all, sel_stores), use_container_width=True, theme=None, config=INTERACTIVE_CHART_CONFIG)

    if not df_i.empty and len(sel_months) > 1:
        st.markdown('<div class="section-title">Category by Month</div>', unsafe_allow_html=True)
        st.plotly_chart(chart_category_by_month(df_i), use_container_width=True, theme=None, config=INTERACTIVE_CHART_CONFIG)

    # ── Stacked bar: category by store ────────────────────────────────────────
    if not df_i.empty and df_i["store"].nunique() > 1:
        st.markdown('<div class="section-title">Category Mix by Store</div>', unsafe_allow_html=True)
        st.plotly_chart(chart_stacked_store_cat(df_i), use_container_width=True, theme=None, config=INTERACTIVE_CHART_CONFIG)

    # ── Items table ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">All Items</div>', unsafe_allow_html=True)
    search = st.text_input("Search items", placeholder="Search items...", label_visibility="collapsed")
    tbl = df_i[["date", "store", "category", "description", "price"]].copy()
    tbl["date"] = tbl["date"].dt.strftime("%Y-%m-%d").fillna("")
    tbl = tbl.sort_values(["date", "store"], ascending=False)
    if search:
        tbl = tbl[tbl["description"].str.contains(search, case=False, na=False)]
    tbl.columns = ["Date", "Store", "Category", "Item", "Price (R)"]
    st.dataframe(tbl, use_container_width=True, hide_index=True)

    # ── Exports ───────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Export</div>', unsafe_allow_html=True)
    e1, e2 = st.columns(2)

    with e1:
        csv_df = df_i[["month", "date", "store", "category", "description", "price"]].copy()
        csv_df["date"] = csv_df["date"].dt.strftime("%Y-%m-%d")
        csv_bytes = csv_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV",
            data=csv_bytes,
            file_name=f"spending_{'_'.join(sel_months)}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with e2:
        if st.button("Generate PDF", use_container_width=True):
            try:
                pdf_bytes = generate_pdf(df_s, df_i, sel_months)
                st.download_button(
                    "Download PDF",
                    data=pdf_bytes,
                    file_name=f"spending_report_{'_'.join(sel_months)}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="dl_pdf",
                )
            except ImportError:
                st.error("Install fpdf2: pip install fpdf2")


if __name__ == "__main__":
    main()
