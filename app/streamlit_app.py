# ===============================================================
# Macro Time Machine — Neo-FinTech UI + AI Interpretation
# ===============================================================

# ------------------ PATH FIX ------------------ #
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

# ------------------ IMPORTS ------------------ #
import os

import streamlit as st
import pandas as pd
import google.generativeai as genai

from src.metadata import build_metadata
from src.config import INDICATOR_CONFIG, METADATA_CSV_PATH
from src.slicer import slice_indicator


# ------------------ FORMATTER ------------------ #
def fmt(n):
    try:
        return f"{n:,.2f}"
    except Exception:
        return n


# ------------------ ENV + GEMINI INIT ------------------ #
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
GEMINI_AVAILABLE = bool(GEMINI_API_KEY)

if GEMINI_AVAILABLE:
    genai.configure(api_key=GEMINI_API_KEY)


# ------------------ PAGE CONFIG ------------------ #
st.set_page_config(
    page_title="Macro Time Machine",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------ THEME STYLING ------------------ #
st.markdown(
    """
<style>
/* GLOBAL */
body {
    background: radial-gradient(circle at top, #e6f0ff 0, #f6f9fc 50%, #f6f9fc 100%) !important;
}
.main {
    background-color: transparent;
    font-family: 'Inter', system-ui, sans-serif !important;
}

/* HEADERS */
h1, h2, h3 {
    color: #111827 !important;
    font-weight: 800 !important;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f3f4f6 100%);
    border-right: 1px solid #d1d5db;
}

/* METRIC CHIPS */
.metric-chip {
    padding: 10px 14px;
    border-radius: 12px;
    background: radial-gradient(circle at top left, #e0edff, #ffffff);
    border: 1px solid #d0d7e5;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
    margin-bottom: 10px;
}

/* VALUE COLORS */
.positive { color: #0066ff !important; }
.negative { color: #e11d48 !important; }

/* AI CARD */
.ai-card {
    margin-top: 20px;
    padding: 16px 18px;
    border-radius: 14px;
    background: linear-gradient(135deg, #eef2ff, #f9fafb);
    border: 1px solid #c7d2fe;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.12);
}

/* TABLE */
.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #e5e7eb;
}
</style>
""",
    unsafe_allow_html=True,
)

# ------------------ HEADER ------------------ #
st.title("🌐 Macro Time Machine")
st.caption("Analyze decades of macro data — with AI assistance.")


# ------------------ LOAD METADATA ------------------ #
if not METADATA_CSV_PATH.exists():
    build_metadata()
meta_df = pd.read_csv(METADATA_CSV_PATH)


# ------------------ SIDEBAR ------------------ #
st.sidebar.header("🔍 Select Indicator")

categories = sorted(meta_df["category"].unique())
category_select = st.sidebar.radio("Category:", categories)
filtered_meta = meta_df[meta_df["category"] == category_select]

indicator_display = st.sidebar.selectbox("Indicator:", filtered_meta["display"])
indicator_id = filtered_meta.loc[
    filtered_meta["display"] == indicator_display, "indicator_id"
].values[0]

st.sidebar.subheader("⏱️ Time Range")
time_ranges = ["1Y", "3Y", "5Y", "10Y", "20Y", "30Y"]
selected_window = st.sidebar.radio("Quick Select:", time_ranges)

st.sidebar.write("Or custom period:")
col1, col2 = st.sidebar.columns(2)
start_year = col1.text_input("Start (YYYY-MM)")
end_year = col2.text_input("End (YYYY-MM)")

load_btn = st.sidebar.button("Load Data 🔄")


# ------------------ GEMINI PROMPT BUILDER ------------------ #
def build_ai_prompt(indicator_id, indicator_display, summary, df_slice, start_str, end_str):
    """
    Build a STRICT, data-grounded prompt for Gemini.
    """
    s = summary
    base_desc_map = {
        "us_cpi": "US consumer price inflation (headline CPI).",
        "in_cpi": "India CPI inflation.",
        "fed_funds": "US Federal Funds Policy Rate (short-term policy rate).",
        "in_policy_rate": "India policy repo rate.",
        "us_10y": "US 10-year government bond yield.",
        "us_yield_curve_10y_2y": "US yield curve spread: 10-year minus 2-year Treasury yield.",
        "vix": "US equity volatility index (VIX), a proxy for market fear.",
        "crude_oil": "Global crude oil prices.",
        "dxy": "US Dollar Index (DXY).",
        "in_fx_spot": "INR per USD spot exchange rate.",
        "in_m3": "India broad money supply (M3).",
        "in_production": "India industrial production / output.",
        "us_hy_spread": "US high yield credit spread.",
    }
    base_desc = base_desc_map.get(indicator_id, "A macroeconomic or market time series.")

    # Compact sample: first 3, middle 3, last 3
    if len(df_slice) <= 9:
        sample = df_slice
    else:
        head = df_slice.head(3)
        tail = df_slice.tail(3)
        mid = df_slice.iloc[len(df_slice) // 2 - 1 : len(df_slice) // 2 + 2]
        sample = pd.concat([head, mid, tail]).drop_duplicates()

    sample_text_lines = ["Date,Value" + (",ChangePct" if "Change %" in df_slice.columns else "")]
    for _, row in sample.iterrows():
        line = f"{row['Date']},{row['Value']}"
        if "Change %" in df_slice.columns:
            line += f",{row['Change %']}"
        sample_text_lines.append(line)

    sample_block = "\n".join(sample_text_lines)

    prompt = f"""
You are a cautious macro and markets analyst.

You are given:
- Indicator: {indicator_display}
- Description: {base_desc}
- Date range: {start_str} to {end_str}

Summary over this window:
- Start value: {s['start_value']:.4f}
- End value: {s['end_value']:.4f}
- Absolute change: {s['abs_change']:.4f}
- Percent change: {s['pct_change']:.4f}%
- Minimum value: {s['min_value']:.4f}
- Maximum value: {s['max_value']:.4f}
- Average value: {s['avg_value']:.4f}

Sample of the time series (not full data, just representative points):
{sample_block}

TASK:
1. Describe the trend over this period strictly based on the numbers.
2. Identify obvious regimes or turning points (e.g., long flat, sharp spikes, persistent declines).
3. Comment on volatility (stable vs choppy).
4. Comment on what this might broadly mean for:
   - policy or rates (if it’s an interest rate or inflation series),
   - risk sentiment (if it’s VIX, spreads, or FX),
   - economic activity (if it’s production or money supply).
5. DO NOT:
   - invent specific external events (like wars or elections),
   - mention any data or dates not represented here,
   - give trading advice.

Keep it:
- 2–4 short paragraphs.
- Fact-based, no storytelling fluff.
- Very explicit that this is a backward-looking interpretation only.
"""
    return prompt


def call_gemini(prompt: str) -> str:
    if not GEMINI_AVAILABLE:
        return "Gemini API key not configured. Add GEMINI_API_KEY in your .env to enable AI interpretation."

    try:
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        resp = model.generate_content(prompt)
        txt = resp.text or ""
        return txt.strip()
    except Exception as e:
        return f"Error from Gemini: {e}"


# ------------------ LOAD DATA + SESSION STATE ------------------ #
result = None

if load_btn:
    try:
        if start_year and end_year:
            result = slice_indicator(indicator_id, start=start_year, end=end_year)
        else:
            result = slice_indicator(indicator_id, window=selected_window)

        # Persist result and reset AI when new data is loaded
        st.session_state["latest_result"] = result
        st.session_state["ai_text"] = ""
    except Exception as e:
        st.error(f"⚠ Error: {e}")

# If there is a stored result, reuse it when not pressing Load Data
if "latest_result" in st.session_state and result is None:
    result = st.session_state["latest_result"]


# ===============================================================
# DISPLAY SECTION
# ===============================================================

if result is not None:
    st.markdown(f"### 📌 {indicator_display}")
    date_start = result.start_date.strftime("%Y-%m")
    date_end = result.end_date.strftime("%Y-%m")
    st.write(f"**Date Range: {date_start} → {date_end}**")

    s = result.summary
    df_display = result.data.copy()
    df_display["Date"] = df_display["Date"].dt.strftime("%Y-%m")

    special_case = indicator_id in ["us_yield_curve_10y_2y", "vix"]

    # ===== SUMMARY BLOCKS ===== #
    if not special_case:
        colA, colB, colC, colD = st.columns(4)
        colA.markdown(
            f"<div class='metric-chip'><b>Start</b><br>{fmt(s['start_value'])}</div>",
            unsafe_allow_html=True,
        )
        colB.markdown(
            f"<div class='metric-chip'><b>End</b><br>{fmt(s['end_value'])}</div>",
            unsafe_allow_html=True,
        )
        colC.markdown(
            f"<div class='metric-chip'><b>Change</b><br>{fmt(s['abs_change'])}</div>",
            unsafe_allow_html=True,
        )

        pct = s["pct_change"]
        color_class = "positive" if pct >= 0 else "negative"
        colD.markdown(
            f"<div class='metric-chip'><b>Change %</b><br>"
            f"<span class='{color_class}'>{pct:.2f}%</span></div>",
            unsafe_allow_html=True,
        )

    elif indicator_id == "us_yield_curve_10y_2y":
        # Yield Curve: vertical-style summary
        spread_min = result.data["Value"].min()
        inverted_months = int((result.data["Value"] < 0).sum())

        st.markdown("#### Yield Curve Structure")
        for label, val in [
            ("Start Spread", fmt(s["start_value"]) + "%"),
            ("End Spread", fmt(s["end_value"]) + "%"),
            ("Most Inverted", fmt(spread_min) + "%"),
            ("Months Inverted", f"{inverted_months} months"),
        ]:
            st.markdown(
                f"<div class='metric-chip'><b>{label}</b><br>{val}</div>",
                unsafe_allow_html=True,
            )

    elif indicator_id == "vix":
        vix_values = result.data["Value"]
        vix_max = vix_values.max()
        max_date = result.data.loc[vix_values.idxmax(), "Date"].strftime("%Y-%m")
        vix_avg = vix_values.mean()
        signal = "Fear Spike" if vix_max > 40 else "Normal"

        st.markdown("#### Volatility Profile (VIX)")
        for label, val in [
            ("Max Spike", fmt(vix_max)),
            ("Spike Month", max_date),
            ("Avg VIX", fmt(vix_avg)),
            ("Signal", signal),
        ]:
            st.markdown(
                f"<div class='metric-chip'><b>{label}</b><br>{val}</div>",
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ===== TABLE ===== #
    st.subheader("📅 Monthly Data")

    df_display["Value"] = df_display["Value"].apply(fmt)

    # For special cases, drop Change % column
    if special_case and "Change %" in df_display.columns:
        df_display = df_display.drop(columns=["Change %"])

    def highlight_change(val):
        try:
            v = float(str(val).replace(",", "").replace("%", ""))
            if v > 0:
                return "color: #0066ff; font-weight:600"
            if v < 0:
                return "color: #e11d48; font-weight:600"
        except Exception:
            return ""

    if "Change %" in df_display.columns:
        styled = df_display.style.applymap(highlight_change, subset=["Change %"])
        st.dataframe(styled, use_container_width=True)
    else:
        st.dataframe(df_display, use_container_width=True)

    # ===== AI INTERPRETATION (BELOW TABLE) ===== #
    st.markdown("---")
    st.subheader("🧠 AI Interpretation (Experimental)")

    if not GEMINI_AVAILABLE:
        st.info("Add GEMINI_API_KEY to your .env file to enable AI interpretation.")
    else:
        if st.button("🔍 Interpret this period with AI"):
            with st.spinner("Analyzing this macro slice with Gemini..."):
                prompt = build_ai_prompt(
                    indicator_id,
                    indicator_display,
                    s,
                    result.data.copy(),  # use numeric data
                    date_start,
                    date_end,
                )
                ai_text = call_gemini(prompt)
                st.session_state["ai_text"] = ai_text

        ai_text = st.session_state.get("ai_text", "")
        if ai_text:
            st.markdown(
                f"<div class='ai-card'><b>📘 AI Interpretation — Data Grounded Analysis</b><br><br>{ai_text}</div>",
                unsafe_allow_html=True,
            )

else:
    st.info("⬅ Select an indicator and click **Load Data**")
