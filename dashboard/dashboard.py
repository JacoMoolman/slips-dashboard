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

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="JM² Shopping Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

[data-testid="stAppViewContainer"] { background: #0d0f1a; }
[data-testid="stSidebar"] { background: #13162a; border-right: 1px solid #1e2340; }
[data-testid="stSidebar"] * { color: #c8d0e7 !important; }
[data-testid="stHeader"] { background: transparent; }

.kpi-grid { display: flex; gap: 16px; margin-bottom: 24px; }
.kpi-card {
    flex: 1;
    background: linear-gradient(135deg, #1a1d35 0%, #1e2340 100%);
    border: 1px solid #2a2f55;
    border-radius: 14px;
    padding: 20px 22px;
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

.kpi-value { font-size: 1.8rem; font-weight: 700; color: #e8ecff; line-height: 1.1; margin-bottom: 4px; }
.kpi-label { font-size: 0.78rem; color: #7a85aa; text-transform: uppercase; letter-spacing: 0.06em; }

.section-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: #7a85aa;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 24px 0 8px;
    padding-bottom: 6px;
    border-bottom: 1px solid #1e2340;
}

.chart-card {
    background: #13162a;
    border: 1px solid #1e2340;
    border-radius: 14px;
    padding: 16px;
}
</style>
""", unsafe_allow_html=True)

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
    "Other":             "#7a85aa",
}

STORE_COLORS = {
    "Woolworths":   "#00b16a",
    "Pick n Pay":   "#e84393",
    "Checkers":     "#f39c12",
    "Dis-Chem":     "#3498db",
    "Clicks":       "#e74c3c",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#c8d0e7", family="Inter"),
    margin=dict(t=20, b=20, l=10, r=10),
)

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


# ── Sidebar ───────────────────────────────────────────────────────────────────
def build_sidebar(df_s, df_i):
    with st.sidebar:
        st.markdown("## JM² Shopping Dashboard")
        st.markdown("---")

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

        st.markdown("---")
        st.caption("Add new data: see WORKFLOW.md")

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
        marker=dict(colors=colors, line=dict(color="#0d0f1a", width=2)),
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>R %{value:,.2f}<br>%{percent}<extra></extra>",
        textfont=dict(size=11),
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=340, showlegend=False)
    return fig


def chart_store_bar(df_s):
    agg = df_s.groupby("store")["total"].sum().reset_index().sort_values("total")
    colors = [STORE_COLORS.get(s, "#7a85aa") for s in agg["store"]]
    fig = go.Figure(go.Bar(
        x=agg["total"], y=agg["store"], orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"R {v:,.0f}" for v in agg["total"]],
        textposition="outside",
        textfont=dict(color="#c8d0e7"),
        hovertemplate="<b>%{y}</b><br>R %{x:,.2f}<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=340,
        xaxis=dict(showgrid=True, gridcolor="#1e2340", tickformat=",.0f", title="Amount (R)", color="#7a85aa"),
        yaxis=dict(showgrid=False, color="#c8d0e7"),
    )
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
        marker=dict(size=9, color="#6c8aff", line=dict(color="#0d0f1a", width=2)),
        text=[f"R {v:,.0f}" for v in agg["total"]],
        textposition="top center",
        textfont=dict(color="#c8d0e7", size=11),
        fill="tozeroy",
        fillcolor="rgba(108,138,255,0.08)",
        hovertemplate="<b>%{x}</b><br>R %{y:,.2f}<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=260,
        xaxis=dict(showgrid=True, gridcolor="#1e2340", color="#7a85aa"),
        yaxis=dict(showgrid=True, gridcolor="#1e2340", tickformat=",.0f", title="R", color="#7a85aa"),
    )
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
    fig.update_layout(
        **PLOTLY_LAYOUT,
        barmode="stack",
        height=max(420, 36 * len(pivot) + 280),
        margin=dict(t=28, b=120, l=64, r=28),
        xaxis=dict(showgrid=False, color="#c8d0e7", tickfont=dict(size=11), automargin=True),
        yaxis=dict(showgrid=True, gridcolor="#1e2340", tickformat=",.0f", title="R", color="#7a85aa"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor="rgba(0,0,0,0)",
            bordercolor="#1e2340",
            font=dict(size=10),
        ),
        hoverlabel=dict(
            bgcolor="#ffffff",
            bordercolor="#111827",
            font=dict(color="#111827", size=13),
        ),
    )
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
        st.error("No data found. See WORKFLOW.md — Step 3.")
        st.stop()

    df_s_all, df_i_all = load_all_data()
    if df_s_all.empty:
        st.error("No data found.")
        st.stop()

    sel_months, sel_stores, sel_cats = build_sidebar(df_s_all, df_i_all)

    mask_s = df_s_all["month"].isin(sel_months) & df_s_all["store"].isin(sel_stores)
    mask_i = (df_i_all["month"].isin(sel_months) &
              df_i_all["store"].isin(sel_stores) &
              df_i_all["category"].isin(sel_cats))
    df_s = df_s_all[mask_s]
    df_i = df_i_all[mask_i]

    # ── Title ──────────────────────────────────────────────────────────────────
    month_label = ", ".join(sel_months) if sel_months else "All months"
    st.markdown(f"# JM² Shopping Dashboard — {month_label}")

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
            st.plotly_chart(chart_category_donut(df_i), use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No item data for selection.")
    with col2:
        st.markdown("**By Store**")
        if not df_s.empty:
            st.plotly_chart(chart_store_bar(df_s), use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No store data.")

    # ── Monthly trend (if multiple months exist) ──────────────────────────────
    all_months = sorted(df_s_all["month"].unique())
    if len(all_months) > 1:
        st.markdown('<div class="section-title">Monthly Trend</div>', unsafe_allow_html=True)
        st.plotly_chart(chart_monthly_trend(df_s_all, sel_stores), use_container_width=True, config={"displayModeBar": False})

    # ── Stacked bar: category by store ────────────────────────────────────────
    if not df_i.empty and df_i["store"].nunique() > 1:
        st.markdown('<div class="section-title">Category Mix by Store</div>', unsafe_allow_html=True)
        st.plotly_chart(chart_stacked_store_cat(df_i), use_container_width=True, config={"displayModeBar": False})

    # ── Items table ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">All Items</div>', unsafe_allow_html=True)
    search = st.text_input("", placeholder="Search items...", label_visibility="collapsed")
    tbl = df_i[["date", "store", "category", "description", "price"]].copy()
    tbl["date"] = tbl["date"].dt.strftime("%Y-%m-%d").fillna("")
    tbl = tbl.sort_values(["date", "store"], ascending=False)
    if search:
        tbl = tbl[tbl["description"].str.contains(search, case=False, na=False)]
    tbl.columns = ["Date", "Store", "Category", "Item", "Price (R)"]
    st.dataframe(tbl, use_container_width=True, hide_index=True)

    # ── Exports ───────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Export</div>', unsafe_allow_html=True)
    e1, e2, e3 = st.columns(3)

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

    with e3:
        try:
            cat_fig = chart_category_donut(df_i)
            img_bytes = cat_fig.to_image(format="png", width=900, height=500, scale=2)
            st.download_button(
                "Download Chart PNG",
                data=img_bytes,
                file_name=f"spending_chart_{'_'.join(sel_months)}.png",
                mime="image/png",
                use_container_width=True,
            )
        except Exception:
            st.caption("Install kaleido for PNG: pip install kaleido")


if __name__ == "__main__":
    main()
