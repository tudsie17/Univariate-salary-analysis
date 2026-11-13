"""
Streamlit app — Univariate analysis of annual salaries
Proba Stat for Data Science, EDC Paris Business School

Run locally:  streamlit run streamlit_app.py
              streamlit run streamlit_app.py -- other_salaries.csv   (use another CSV)
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import streamlit as st

st.set_page_config(page_title="Salary Analysis", page_icon="📊", layout="wide")

BLUE, LIGHT, ORANGE, NAVY, RED, GREY = "#2E5A88", "#8FB0D3", "#D9822B", "#1F3A5F", "#B33A3A", "#555555"
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
kfmt = FuncFormatter(lambda v, _: f"{v/1000:.0f}k")
eur = lambda v: f"{v:,.0f} €".replace(",", " ")


# ------------------------------------------------------------------ data
@st.cache_data
def load_data(path_arg):
    """CSV path from the command line:  streamlit run streamlit_app.py -- my_file.csv
    Otherwise falls back to data/salary_data.csv or salary_data.csv in the repo."""
    here = Path(__file__).parent
    candidates = ([Path(path_arg)] if path_arg else []) + [here / "data" / "salary_data.csv", here / "salary_data.csv"]
    for p in candidates:
        if p.exists():
            return pd.read_csv(p), str(p.name)
    return None, None


csv_arg = sys.argv[1] if len(sys.argv) > 1 else None
df, source = load_data(csv_arg)
if df is None or "salary" not in df.columns:
    st.error("No data found. Run `streamlit run streamlit_app.py -- path/to/file.csv` "
             "or put salary_data.csv in the repo (root or data/). The file needs a 'salary' column.")
    st.stop()

st.sidebar.markdown("## ⚙️ Settings")
x = df["salary"].dropna().astype(float).to_numpy()
n = len(x)
xs = np.sort(x)

width = st.sidebar.slider("Class width (€)", 10_000, 100_000, 50_000, step=10_000)
st.sidebar.caption(f"Sturges' rule suggests k = 1 + log₂(n) ≈ {1 + np.log2(n):.1f} classes.")

# ------------------------------------------------------------------ statistics
mean, median = x.mean(), np.median(x)
sd = x.std(ddof=1)
var = x.var(ddof=1)
q1, q3 = np.percentile(x, [25, 75])
iqr = q3 - q1
cv = sd / mean
p10, p90 = np.percentile(x, [10, 90])
skew = pd.Series(x).skew()

start = np.floor(x.min() / 25_000) * 25_000
edges = np.arange(start, x.max() + width, width)
counts, _ = np.histogram(x, bins=edges)
i = int(np.argmax(counts))
d1 = counts[i] - (counts[i - 1] if i > 0 else 0)
d2 = counts[i] - (counts[i + 1] if i + 1 < len(counts) else 0)
mode = edges[i] + (d1 / (d1 + d2) if (d1 + d2) else 0.5) * width

lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
out = x[(x < lo) | (x > hi)]
clean = x[(x >= lo) & (x <= hi)]
cq1, cq3 = np.percentile(clean, [25, 75])

cum_share = np.r_[0, np.cumsum(xs) / xs.sum()]
pop_share = np.linspace(0, 1, n + 1)
gini = 1 - 2 * np.sum((cum_share[1:] + cum_share[:-1]) / 2) / n
top10 = xs[-int(round(0.1 * n)):].sum() / xs.sum()
bottom50 = xs[: n // 2].sum() / xs.sum()

# ------------------------------------------------------------------ theme / CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stMarkdown, .stDataFrame, button, input { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 3.2rem; max-width: 1250px; }
#MainMenu, footer { visibility: hidden; }

.hero {
  background: linear-gradient(120deg, #1F3A5F 0%, #2E5A88 60%, #3F74A8 100%);
  border-radius: 16px; padding: 28px 34px; color: #fff; margin-bottom: 22px;
  box-shadow: 0 8px 24px rgba(31,58,95,.18);
}
.hero h1 { color: #fff; font-size: 2.0rem; font-weight: 700; margin: 0 0 4px 0; padding: 0; }
.hero p  { color: #D6E2F0; margin: 0; font-size: .95rem; }
.hero .tag { display:inline-block; background: rgba(217,130,43,.95); color:#fff; font-size:.72rem;
  font-weight:600; letter-spacing:.06em; text-transform:uppercase; padding:4px 10px; border-radius:999px; margin-bottom:12px; }

div[data-testid="stMetric"] {
  background: #fff; border: 1px solid #E3E8EF; border-left: 4px solid #D9822B;
  border-radius: 12px; padding: 14px 18px; box-shadow: 0 2px 8px rgba(16,24,40,.05);
}
div[data-testid="stMetricLabel"] p { color: #5B6B7F; font-size: .8rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: .04em; }
div[data-testid="stMetricValue"] { color: #1F3A5F; font-weight: 700; font-size: 1.65rem; }

.stTabs [role="tablist"] { gap: 6px; border-bottom: 1px solid #E3E8EF; }
.stTabs button[role="tab"] { background: #fff; border: 1px solid #E3E8EF; border-bottom: none;
  border-radius: 10px 10px 0 0; padding: 10px 18px; color: #5B6B7F; }
.stTabs button[role="tab"] p { font-weight: 600; }
.stTabs button[role="tab"][aria-selected="true"] { background: #1F3A5F; color: #fff; }
.stTabs button[role="tab"][aria-selected="true"] p { color: #fff; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }
h2, h3 { color: #1F3A5F; font-weight: 700; }
div[data-testid="stImage"] img, div[data-testid="stPyplot"] img { border-radius: 12px; }
div[data-testid="stDataFrame"] { border: 1px solid #E3E8EF; border-radius: 12px; overflow: hidden; }
div[data-testid="stAlert"] { border-radius: 12px; }
section[data-testid="stSidebar"] { background: #E9EFF6; border-right: 1px solid #D5DEE9; }
section[data-testid="stSidebar"] h2 { color: #1F3A5F; }
.foot { text-align:center; color:#8A97A8; font-size:.8rem; margin-top: 30px; }
</style>
""", unsafe_allow_html=True)

# white figure background with card look
plt.rcParams.update({"figure.facecolor": "white", "axes.facecolor": "white",
                     "axes.edgecolor": "#9AA7B6", "axes.labelcolor": "#33475B",
                     "xtick.color": "#5B6B7F", "ytick.color": "#5B6B7F",
                     "axes.titleweight": "bold", "axes.titlecolor": "#1F3A5F",
                     "axes.grid": True, "grid.color": "#EEF2F6", "axes.axisbelow": True})

# ------------------------------------------------------------------ header
st.markdown(f"""
<div class="hero">
  <span class="tag">Univariate statistics · HR analytics</span>
  <h1>Analysis of Annual Salaries</h1>
  <p>{n} employees · fictional digital-services company · Proba Stat for Data Science, EDC Paris Business School</p>
</div>
""", unsafe_allow_html=True)

c = st.columns(5)
c[0].metric("Employees", n)
c[1].metric("Mean", f"{mean/1000:,.1f} k€")
c[2].metric("Median", f"{median/1000:,.1f} k€")
c[3].metric("Coefficient of variation", f"{cv:.2f}")
c[4].metric("Gini", f"{gini:.2f}")

tabs = st.tabs(["1 · Description", "2 · Graphs", "3 · Central tendency", "4 · Dispersion",
                "5 · Outliers", "6 · Inequality & HR"])

# ------------------------------------------------------------------ 1
with tabs[0]:
    st.subheader("Nature of the variable")
    st.markdown(f"""
- **Variable:** `salary`, the gross annual salary of one employee
- **Type:** quantitative, continuous (ratio scale)
- **Unit:** euros (€), gross, per year
- **Range:** {eur(x.min())} → {eur(x.max())} (range = {eur(x.max() - x.min())}), {df['salary'].nunique()} distinct values
""")
    st.subheader("Frequency table")
    st.markdown(f"Sturges' rule gives **k ≈ {1 + np.log2(n):.1f}** classes. With a width of **{eur(width)}**, "
                f"this gives **{len(counts)}** classes with round bounds. Classes are of the form [a ; b[.")
    cum = np.cumsum(counts)
    ft = pd.DataFrame({
        "Class": [f"[{edges[j]:,.0f} ; {edges[j+1]:,.0f}[".replace(",", " ") for j in range(len(counts))],
        "Centre": (edges[:-1] + edges[1:]) / 2,
        "nᵢ": counts, "fᵢ (%)": 100 * counts / n,
        "Nᵢ (cum.)": cum, "Fᵢ (cum. %)": 100 * cum / n,
    })
    st.dataframe(ft.style.format({"Centre": "{:,.0f}", "fᵢ (%)": "{:.1f}", "Fᵢ (cum. %)": "{:.1f}"}),
                 hide_index=True, width="stretch")

# ------------------------------------------------------------------ 2
with tabs[1]:
    a, b = st.columns(2)
    with a:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.hist(x, bins=edges, color=LIGHT, edgecolor="white")
        ax.axvline(mean, color=ORANGE, lw=2, label=f"Mean = {eur(mean)}")
        ax.axvline(median, color=NAVY, lw=2, ls="--", label=f"Median = {eur(median)}", zorder=3)
        ax.xaxis.set_major_formatter(kfmt)
        ax.set_xlabel("Gross annual salary (€)"); ax.set_ylabel("Employees"); ax.set_title("Histogram")
        ax.legend(frameon=False)
        st.pyplot(fig)
    with b:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.step(xs, np.arange(1, n + 1) / n, where="post", color=BLUE, lw=2)
        for q, lab in [(q1, "Q1"), (median, "Me"), (q3, "Q3")]:
            ax.axvline(q, color=GREY, lw=1, ls=":"); ax.text(q, 1.02, lab, ha="center", fontsize=8, color=GREY)
        ax.xaxis.set_major_formatter(kfmt); ax.set_ylim(0, 1.07)
        ax.set_xlabel("Gross annual salary (€)"); ax.set_ylabel("F(x)"); ax.set_title("Empirical CDF", pad=14)
        st.pyplot(fig)
    fig, ax = plt.subplots(figsize=(12, 2.6))
    ax.boxplot(x, orientation="horizontal", widths=0.5, patch_artist=True,
               boxprops=dict(facecolor="#C9D8EA", color=BLUE), medianprops=dict(color=ORANGE, lw=2),
               whiskerprops=dict(color=BLUE), capprops=dict(color=BLUE),
               flierprops=dict(marker="o", markerfacecolor=RED, markeredgecolor=RED, ms=5))
    ax.axvline(hi, color=RED, ls="--", lw=1)
    ax.set_yticks([]); ax.xaxis.set_major_formatter(kfmt)
    ax.set_xlabel("Gross annual salary (€)"); ax.set_title("Boxplot (outliers in red, 1.5 × IQR rule)")
    st.pyplot(fig)
    st.info("All three graphs show a **right-skewed** distribution: a dense block of salaries on the left and a long, sparse tail toward high salaries.")

# ------------------------------------------------------------------ 3
with tabs[2]:
    c = st.columns(3)
    c[0].metric("Mean", eur(mean))
    c[1].metric("Median", eur(median))
    c[2].metric("Mode (estimated, grouped)", f"≈ {eur(mode)}")
    st.markdown(f"""
**Mode < Median < Mean**: this ordering is typical of a **positively skewed** distribution.

- The mean is **{100*(mean/median-1):.0f} %** above the median.
- Skewness (Fisher) = **{skew:.2f}**; Pearson's coefficient 3(x̄ − Me)/s = **{3*(mean-median)/sd:.2f}**.
- **{100*(x < mean).mean():.0f} %** of employees earn less than the mean.

The median describes the typical employee better. The mean is still useful for budgeting (total payroll = n × mean).
""")

# ------------------------------------------------------------------ 4
with tabs[3]:
    c = st.columns(4)
    c[0].metric("Standard deviation", eur(sd))
    c[1].metric("Variance", f"{var:.3e} €²")
    c[2].metric("IQR", eur(iqr), help=f"Q1 = {eur(q1)}, Q3 = {eur(q3)}")
    c[3].metric("CV", f"{100*cv:.1f} %")
    level = "low" if cv < 0.15 else "moderate" if cv < 0.3 else "high"
    st.markdown(f"""
A CV of **{100*cv:.0f} %** means **{level} dispersion**: salaries are very heterogeneous, and the mean is not a reliable summary of a typical salary.
The middle 50 % of employees earn between **{eur(q1)}** and **{eur(q3)}**. D9/D1 = **{p90/p10:.1f}**.
""")

# ------------------------------------------------------------------ 5
with tabs[4]:
    st.markdown(f"""
**1.5 × IQR rule**
- Lower fence = Q1 − 1.5 × IQR = **{eur(lo)}**
- Upper fence = Q3 + 1.5 × IQR = **{eur(hi)}**

**{len(out)} outlier(s)** ({100*len(out)/n:.1f} % of employees): {", ".join(eur(v) for v in np.sort(out)) or "none"}
""")
    comp = pd.DataFrame({
        "Statistic": ["Mean", "Standard deviation", "Median", "IQR"],
        "All data": [mean, sd, median, iqr],
        "Without outliers": [clean.mean(), clean.std(ddof=1), np.median(clean), cq3 - cq1],
    })
    comp["Change (%)"] = 100 * (comp["Without outliers"] / comp["All data"] - 1)
    st.dataframe(comp.style.format({"All data": "{:,.0f} €", "Without outliers": "{:,.0f} €", "Change (%)": "{:+.1f}"}),
                 hide_index=True, width="stretch")
    st.markdown("""
**Robustness.** The mean and standard deviation react strongly to a few extreme values; the standard deviation reacts most, because it squares the deviations.
The median and IQR depend only on ranks, so they change little. **Use median and IQR to describe the typical employee.**

The outliers are most likely real senior or executive salaries, not errors, so keep them in any payroll or inequality analysis.
""")

# ------------------------------------------------------------------ 6
with tabs[5]:
    a, b = st.columns([1, 1.3])
    with a:
        fig, ax = plt.subplots(figsize=(5, 4.6))
        ax.plot(pop_share, cum_share, color=BLUE, lw=2, label="Lorenz curve")
        ax.plot([0, 1], [0, 1], color=GREY, ls="--", lw=1, label="Perfect equality")
        ax.fill_between(pop_share, cum_share, pop_share, color=BLUE, alpha=0.12)
        ax.set_xlabel("Cumulative share of employees"); ax.set_ylabel("Cumulative share of payroll")
        ax.set_title(f"Lorenz curve (Gini = {gini:.3f})"); ax.legend(frameon=False, loc="upper left")
        st.pyplot(fig)
    with b:
        st.metric("Payroll share of top 10 %", f"{100*top10:.1f} %")
        st.metric("Payroll share of bottom 50 %", f"{100*bottom50:.1f} %")
        st.metric("Max / Min", f"{x.max()/x.min():.1f}×")
        st.markdown(f"Inequality is **high for a single company**. The top 10 % of earners receive **{100*top10:.0f} %** "
                    f"of payroll, and the bottom half receives **{100*bottom50:.0f} %**.")
    st.subheader("HR recommendations")
    st.markdown(f"""
1. **Formal salary bands.** Define job grades with min–mid–max ranges, so that large pay gaps reflect real differences in role and responsibility.
2. **Career paths for the core.** {100*(x < 75_000).mean():.0f} % of staff earn under 75 000 €. Clear promotion criteria and an intermediate senior level reduce attrition.
3. **Performance-linked top pay.** Shift part of the highest salaries to variable pay to keep fixed costs aligned with results.
4. **Robust HR reporting.** Communicate the median ({eur(median)}) as the typical salary. Track Gini, D9/D1 and the top-10 % share every year.
""")

with st.expander("Raw data"):
    st.dataframe(df, width="stretch")

st.markdown('<div class="foot">Built with Python · pandas · NumPy · Matplotlib · Streamlit</div>', unsafe_allow_html=True)
