"""
Univariate statistical analysis of annual salaries (salary_data.csv)
Proba Stat for Data Science - EDC Paris Business School

Computes all statistics required by the project, saves the figures as PNG,
and writes the results to results.json (used to build the PDF report).

Usage:  python salary_analysis.py path/to/salary_data.csv
"""
import sys, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

path = sys.argv[1] if len(sys.argv) > 1 else "salary_data.csv"
s = pd.read_csv(path)["salary"].dropna().astype(float)
x = s.to_numpy()
n = len(x)
R = {}

# ---------------------------------------------------------------- 1. Description
R["n"] = n
R["min"], R["max"] = x.min(), x.max()
R["range"] = x.max() - x.min()
R["n_unique"] = int(s.nunique())

# Frequency table: Sturges' rule k = 1 + log2(n) -> ~7.2, rounded up to 8 classes.
# Range 372,000 / 8 = 46,500 -> rounded to a readable width of 50,000,
# starting at 25,000 so that every class has round bounds and covers [28k, 400k].
k_sturges = 1 + np.log2(n)
width = 50_000
edges = np.arange(25_000, x.max() + width, width)          # 25k, 75k, ..., 425k
counts, _ = np.histogram(x, bins=edges)                    # [a, b) except last [a, b]
freq = counts / n
table = []
cum = 0
for i, c in enumerate(counts):
    cum += c
    table.append({
        "class": f"[{edges[i]/1000:.0f}k ; {edges[i+1]/1000:.0f}k[",
        "center": (edges[i] + edges[i + 1]) / 2,
        "n_i": int(c), "f_i": freq[i], "N_i": int(cum), "F_i": cum / n,
    })
R["k_sturges"] = k_sturges
R["class_width"] = width
R["freq_table"] = table

# ---------------------------------------------------------------- 3. Central tendency
R["mean"] = x.mean()
R["median"] = np.median(x)
# All values are distinct -> no raw mode. Estimate from the grouped data (modal class)
# with the interpolation formula  Mo = L + d1/(d1+d2) * h
i = int(np.argmax(counts))
d1 = counts[i] - (counts[i - 1] if i > 0 else 0)
d2 = counts[i] - (counts[i + 1] if i + 1 < len(counts) else 0)
R["modal_class"] = table[i]["class"]
R["mode_grouped"] = edges[i] + d1 / (d1 + d2) * width
# Finer check: modal class with 10k bins
c10, e10 = np.histogram(x, bins=np.arange(20_000, 410_001, 10_000))
j = int(np.argmax(c10))
R["modal_class_10k"] = f"[{e10[j]/1000:.0f}k ; {e10[j+1]/1000:.0f}k["
R["skew"] = pd.Series(x).skew()                  # adjusted Fisher-Pearson coefficient
R["pearson_skew2"] = 3 * (x.mean() - np.median(x)) / x.std(ddof=1)

# ---------------------------------------------------------------- 4. Dispersion
R["var_pop"] = x.var(ddof=0)
R["var_sample"] = x.var(ddof=1)
R["sd_pop"] = x.std(ddof=0)
R["sd_sample"] = x.std(ddof=1)
q1, q3 = np.percentile(x, [25, 75])                 # linear interpolation (numpy default)
R["q1"], R["q3"] = q1, q3
R["iqr"] = q3 - q1
R["cv"] = R["sd_sample"] / R["mean"]
R["p10"], R["p90"] = np.percentile(x, [10, 90])
R["d9_d1"] = R["p90"] / R["p10"]

# ---------------------------------------------------------------- 5. Outliers (1.5 x IQR)
lo, hi = q1 - 1.5 * R["iqr"], q3 + 1.5 * R["iqr"]
R["fence_low"], R["fence_high"] = lo, hi
out = x[(x < lo) | (x > hi)]
clean = x[(x >= lo) & (x <= hi)]
R["outliers"] = out.tolist()
R["n_outliers"] = len(out)
R["mean_clean"] = clean.mean()
R["sd_clean"] = clean.std(ddof=1)
R["median_clean"] = np.median(clean)
cq1, cq3 = np.percentile(clean, [25, 75])
R["iqr_clean"] = cq3 - cq1
R["cv_clean"] = R["sd_clean"] / R["mean_clean"]

# ---------------------------------------------------------------- 6. Inequality
xs = np.sort(x)
cum_share = np.cumsum(xs) / xs.sum()
R["gini"] = 1 - 2 * np.trapezoid(np.r_[0, cum_share], dx=1 / n) if hasattr(np, "trapezoid") \
    else 1 - 2 * np.trapz(np.r_[0, cum_share], dx=1 / n)
top10 = xs[-int(round(0.1 * n)):]
bottom50 = xs[: n // 2]
R["share_top10"] = top10.sum() / xs.sum()
R["share_bottom50"] = bottom50.sum() / xs.sum()
R["pct_below_mean"] = (x < x.mean()).mean()
R["top_to_bottom"] = x.max() / x.min()

# ---------------------------------------------------------------- 2. Graphs
BLUE, ORANGE, GREY = "#2E5A88", "#D9822B", "#555555"
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
k = lambda v, _: f"{v/1000:.0f}k"
from matplotlib.ticker import FuncFormatter

# Histogram (same classes as the frequency table)
fig, ax = plt.subplots(figsize=(7.5, 4))
ax.hist(x, bins=edges, color="#8FB0D3", edgecolor="white")
ax.axvline(R["mean"], color=ORANGE, lw=2, label=f"Mean = {R['mean']:,.0f} €")
ax.axvline(R["median"], color="#1F3A5F", lw=2, ls="--", zorder=3, label=f"Median = {R['median']:,.0f} €")
ax.set_xticks(edges); ax.xaxis.set_major_formatter(FuncFormatter(k))
ax.set_xlabel("Gross annual salary (€)"); ax.set_ylabel("Number of employees")
ax.set_title("Histogram of salaries (class width 50k€)")
ax.legend(frameon=False)
fig.tight_layout(); fig.savefig("fig_histogram.png", dpi=200); plt.close(fig)

# ECDF
fig, ax = plt.subplots(figsize=(7.5, 4))
ax.step(xs, np.arange(1, n + 1) / n, where="post", color=BLUE, lw=2)
for q, lab in [(q1, "Q1"), (R["median"], "Median"), (q3, "Q3")]:
    ax.axvline(q, color=GREY, lw=1, ls=":")
    ax.text(q, 1.02, lab, ha="center", fontsize=8, color=GREY)
ax.xaxis.set_major_formatter(FuncFormatter(k))
ax.set_ylim(0, 1.06)
ax.set_xlabel("Gross annual salary (€)"); ax.set_ylabel("F(x) = proportion ≤ x")
ax.set_title("Empirical cumulative distribution function", pad=14)
fig.tight_layout(); fig.savefig("fig_ecdf.png", dpi=200); plt.close(fig)

# Boxplot
fig, ax = plt.subplots(figsize=(7.5, 2.8))
ax.boxplot(x, orientation="horizontal", widths=0.5, patch_artist=True,
           boxprops=dict(facecolor="#C9D8EA", color=BLUE),
           medianprops=dict(color=ORANGE, lw=2),
           whiskerprops=dict(color=BLUE), capprops=dict(color=BLUE),
           flierprops=dict(marker="o", markerfacecolor="#B33A3A", markeredgecolor="#B33A3A", ms=5))
ax.axvline(hi, color="#B33A3A", ls="--", lw=1)
ax.text(hi, 1.38, f"Upper fence\n{hi:,.0f} €", color="#B33A3A", fontsize=8, ha="left")
ax.set_yticks([]); ax.xaxis.set_major_formatter(FuncFormatter(k))
ax.set_xlabel("Gross annual salary (€)")
ax.set_title("Boxplot of salaries (outliers in red, 1.5 × IQR rule)")
fig.tight_layout(); fig.savefig("fig_boxplot.png", dpi=200); plt.close(fig)

# Lorenz curve (supporting the inequality discussion)
fig, ax = plt.subplots(figsize=(4.6, 4.2))
ax.plot(np.r_[0, np.arange(1, n + 1) / n], np.r_[0, cum_share], color=BLUE, lw=2, label="Lorenz curve")
ax.plot([0, 1], [0, 1], color=GREY, ls="--", lw=1, label="Perfect equality")
ax.fill_between(np.r_[0, np.arange(1, n + 1) / n], np.r_[0, cum_share], np.r_[0, np.arange(1, n + 1) / n],
                color=BLUE, alpha=0.12)
ax.set_xlabel("Cumulative share of employees"); ax.set_ylabel("Cumulative share of payroll")
ax.set_title(f"Lorenz curve (Gini = {R['gini']:.3f})")
ax.legend(frameon=False, loc="upper left")
fig.tight_layout(); fig.savefig("fig_lorenz.png", dpi=200); plt.close(fig)

# ---------------------------------------------------------------- Output
def conv(o):
    if isinstance(o, (np.floating, np.integer)): return o.item()
    raise TypeError
with open("results.json", "w") as f:
    json.dump(R, f, indent=2, default=conv)
for kk, v in R.items():
    if kk != "freq_table": print(f"{kk:16s} {v}")
print(pd.DataFrame(table).to_string(index=False))
