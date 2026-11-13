"""Builds the PDF report from results.json and the PNG figures (run salary_analysis.py first)."""
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                Image, PageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

F = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", F + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVB", F + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DVI", F + "DejaVuSans-Oblique.ttf"))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily("DV", normal="DV", bold="DVB", italic="DVI", boldItalic="DVB")

R = json.load(open("results.json"))
NAVY, ACC, LIGHT = colors.HexColor("#1F3A5F"), colors.HexColor("#D9822B"), colors.HexColor("#EEF3F8")

body = ParagraphStyle("b", fontName="DV", fontSize=9.6, leading=13.6, alignment=TA_JUSTIFY, spaceAfter=6)
h1 = ParagraphStyle("h1", fontName="DVB", fontSize=13.5, leading=17, textColor=NAVY, spaceBefore=12, spaceAfter=6)
h2 = ParagraphStyle("h2", fontName="DVB", fontSize=10.5, leading=14, textColor=NAVY, spaceBefore=6, spaceAfter=4)
cap = ParagraphStyle("c", fontName="DVI", fontSize=8.3, leading=11, alignment=TA_CENTER,
                     textColor=colors.HexColor("#555555"), spaceAfter=8)
cell = ParagraphStyle("cell", fontName="DV", fontSize=8.8, leading=11.5)
cellb = ParagraphStyle("cellb", parent=cell, fontName="DVB", textColor=colors.white)
box = ParagraphStyle("box", parent=body, backColor=LIGHT, borderPadding=7, borderColor=NAVY,
                     borderWidth=0, spaceBefore=6, spaceAfter=10)

e = lambda v: f"{v:,.0f} €".replace(",", " ")       # 108 547 €
num = lambda v, d=0: f"{v:,.{d}f}".replace(",", " ")
pct = lambda v, d=1: f"{100*v:.{d}f} %"
P = lambda t, s=body: Paragraph(t, s)


def table(rows, widths, align_right_from=1):
    data = [[P(c, cellb) for c in rows[0]]] + [[P(str(c), cell) for c in r] for r in rows[1:]]
    t = Table(data, colWidths=widths, hAlign="CENTER")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("LINEBELOW", (0, -1), (-1, -1), 0.6, NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def fig(path, w_cm, caption):
    from reportlab.lib.utils import ImageReader
    iw, ih = ImageReader(path).getSize()
    w = w_cm * cm
    return KeepTogether([Image(path, width=w, height=w * ih / iw), P(caption, cap)])


def footer(c, d):
    c.saveState()
    c.setFont("DV", 7.5); c.setFillColor(colors.HexColor("#777777"))
    c.drawString(2 * cm, 1.2 * cm, "Univariate analysis of annual salaries — Proba Stat for Data Science, EDC Paris Business School")
    c.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"{d.page}")
    c.restoreState()


S = []
# ------------------------------------------------------------------ Title block
S += [Spacer(1, 0.4 * cm),
      P("Univariate Statistics Project", ParagraphStyle("t", fontName="DVB", fontSize=20, leading=24, textColor=NAVY)),
      P("Analysis of Annual Salaries", ParagraphStyle("st", fontName="DV", fontSize=13, leading=17, textColor=ACC, spaceAfter=4)),
      P("Proba Stat for Data Science · EDC Paris Business School · Author: Augustine",
        ParagraphStyle("m", fontName="DV", fontSize=9, textColor=colors.HexColor("#555555"), spaceAfter=10))]

S.append(P(
    f"<b>Key findings.</b> The {R['n']} salaries range from {e(R['min'])} to {e(R['max'])}. "
    f"The distribution is strongly <b>right-skewed</b>: the mean ({e(R['mean'])}) is {pct(R['mean']/R['median']-1,0)} above the "
    f"median ({e(R['median'])}), and two-thirds of employees ({pct(R['pct_below_mean'],0)}) earn less than the mean. "
    f"Dispersion is high (CV = {R['cv']:.2f}). The 1.5 × IQR rule flags {R['n_outliers']} high salaries "
    f"(≥ {e(min(R['outliers']))}); removing them lowers the mean by {pct(1-R['mean_clean']/R['mean'],0)} and the standard deviation by "
    f"{pct(1-R['sd_clean']/R['sd_sample'],0)}, while the median moves by only {pct(1-R['median_clean']/R['median'],0)}. "
    f"Inequality is substantial: Gini = {R['gini']:.2f}, and the top 10 % of earners receive {pct(R['share_top10'],0)} of total payroll.", box))

# ------------------------------------------------------------------ 1
S.append(P("1. Description of the variable", h1))
S.append(P("1.1 Nature of the variable", h2))
S.append(table([
    ["Characteristic", "Value"],
    ["Variable", "salary — gross annual salary of one employee"],
    ["Statistical type", "Quantitative, continuous (measured in money; in practice recorded in steps of 500–20 000 €)"],
    ["Unit", "Euro (€), gross, per year"],
    ["Population / sample size", f"n = {R['n']} employees (one row per employee), no missing values"],
    ["Range of values", f"min = {e(R['min'])}, max = {e(R['max'])}, range = {e(R['range'])}"],
    ["Distinct values", f"{R['n_unique']} (every salary is unique)"],
], [4.6 * cm, 11.4 * cm]))
S.append(Spacer(1, 6))
S.append(P("Salary is a ratio-scale variable: zero is meaningful and ratios are interpretable "
           "(e.g. the highest salary is " + f"{R['top_to_bottom']:.1f}" + " times the lowest). "
           "It is treated as continuous, which is why it is summarised with classes, a histogram and an ECDF rather than a bar chart."))

S.append(P("1.2 Frequency table grouped into classes", h2))
S.append(P(
    f"<b>Choice of classes.</b> Sturges' rule gives k = 1 + log<sub>2</sub>(n) = 1 + log<sub>2</sub>({R['n']}) ≈ {R['k_sturges']:.1f}, "
    f"i.e. 7–8 classes. Dividing the range by 8 gives ≈ {num(R['range']/8)} €, rounded to a readable width of "
    f"<b>{num(R['class_width'])} €</b>. Classes start at 25 000 € so that all bounds are round and the whole range "
    f"[{num(R['min'])} ; {num(R['max'])}] is covered by 8 equal-width classes. Equal widths keep the histogram "
    f"directly readable (bar height ∝ frequency). Classes are closed on the left and open on the right, [a ; b[."))
rows = [["Class (€)", "Centre", "n<sub>i</sub>", "f<sub>i</sub>", "N<sub>i</sub> (cum.)", "F<sub>i</sub> (cum.)"]]
for r in R["freq_table"]:
    rows.append([r["class"].replace("k", " 000").replace(" ;", " ;"), num(r["center"]), r["n_i"],
                 pct(r["f_i"]), r["N_i"], pct(r["F_i"])])
rows.append(["<b>Total</b>", "", f"<b>{R['n']}</b>", "<b>100.0 %</b>", "", ""])
S.append(table(rows, [3.6 * cm, 2.3 * cm, 1.6 * cm, 2.3 * cm, 2.6 * cm, 2.6 * cm]))
S.append(Spacer(1, 6))
S.append(P(
    f"More than half of the staff ({pct(R['freq_table'][0]['f_i'])}) is in the first class and "
    f"{pct(R['freq_table'][1]['F_i'],0)} earn less than 125 000 €; frequencies then fall quickly, leaving a long, thin tail "
    f"up to 400 000 €. The first class is very crowded, which is the price of equal widths on a skewed variable; "
    f"a finer 10 000 € grid is used below to locate the mode."))

# ------------------------------------------------------------------ 2
S.append(P("2. Graphical representations", h1))
S.append(fig("fig_histogram.png", 15.5, "Figure 1 — Histogram of salaries with the 8 classes of the frequency table."))
S.append(P("The histogram is asymmetric with a peak on the left and a long right tail: a typical shape for salaries. "
           "The mean line sits well to the right of the median, pulled by the few very high salaries."))
S.append(fig("fig_ecdf.png", 15.5, "Figure 2 — Empirical cumulative distribution function F(x) = (number of salaries ≤ x) / n."))
S.append(P(
    f"The ECDF rises steeply up to about 90 000 € (≈ 64 % of employees) because salaries there are closely spaced "
    f"(steps of 1 000–2 000 €). Above that, the curve flattens and the steps widen (5 000, 10 000, then 20 000 €): "
    f"the upper part of the pay scale is sparse. Reading the curve: F(Q1) = 0.25 at {e(R['q1'])}, "
    f"F(Me) = 0.5 at {e(R['median'])}, F(Q3) = 0.75 at {e(R['q3'])}, and 90 % of salaries are below {e(R['p90'])}."))
S.append(fig("fig_boxplot.png", 15.5, "Figure 3 — Boxplot of salaries. Points beyond the dashed line are outliers by the 1.5 × IQR rule."))
S.append(P("The median is close to the left edge of the box and the right whisker is far longer than the left one — "
           "two more signs of right skewness. Seven points lie beyond the upper fence (section 5)."))

# ------------------------------------------------------------------ 3
S.append(P("3. Measures of central tendency", h1))
S.append(table([
    ["Measure", "Value", "How it is obtained"],
    ["Mean", e(R["mean"]), "x̄ = Σx<sub>i</sub> / n"],
    ["Median", e(R["median"]), f"Average of the 37th and 38th ordered values (n = {R['n']} is even)"],
    ["Mode (estimated)", f"≈ {e(R['mode_grouped'])}",
     f"No value repeats, so there is no raw mode. Modal class {R['modal_class'].replace('k',' 000')} with "
     f"Mo = L + d<sub>1</sub>/(d<sub>1</sub>+d<sub>2</sub>) × h. A 10 000 € grid places the peak in {R['modal_class_10k'].replace('k',' 000')}."],
], [3.4 * cm, 2.8 * cm, 9.8 * cm]))
S.append(Spacer(1, 6))
S.append(P(
    f"<b>Comparison and asymmetry.</b> We observe <b>Mode (≈ {num(R['mode_grouped']/1000,0)} k€) &lt; Median "
    f"({num(R['median']/1000,0)} k€) &lt; Mean ({num(R['mean']/1000,1)} k€)</b>, the classic ordering of a "
    f"<b>positively (right-) skewed</b> distribution. The mean exceeds the median by {e(R['mean']-R['median'])} "
    f"({pct(R['mean']/R['median']-1,0)}). Skewness confirms it: the Fisher coefficient is {R['skew']:.2f} and "
    f"Pearson's second coefficient 3(x̄ − Me)/s is {R['pearson_skew2']:.2f} (both clearly &gt; 0). "
    f"The mean is therefore <i>not</i> a good description of a “typical” salary: {pct(R['pct_below_mean'],0)} of employees earn less than it. "
    f"The median is the better summary of the typical employee; the mean remains useful for payroll budgeting "
    f"(total payroll = n × mean)."))

# ------------------------------------------------------------------ 4
S.append(P("4. Measures of dispersion", h1))
S.append(table([
    ["Measure", "Value", "Comment"],
    ["Variance (sample, n − 1)", f"{R['var_sample']:.3e} €²", f"Population version (n): {R['var_pop']:.3e} €². Unit is €², hard to read."],
    ["Standard deviation (sample)", e(R["sd_sample"]), f"Population version: {e(R['sd_pop'])}"],
    ["Q1 / Q3", f"{e(R['q1'])} / {e(R['q3'])}", "Linear-interpolation quartiles"],
    ["Interquartile range (IQR)", e(R["iqr"]), "Spread of the middle 50 % of employees"],
    ["Coefficient of variation", f"{R['cv']:.3f} ({pct(R['cv'])})", "CV = s / x̄"],
    ["D9 / D1 (interdecile ratio)", f"{R['d9_d1']:.1f}", f"D1 = {e(R['p10'])}, D9 = {e(R['p90'])}"],
], [4.6 * cm, 4.0 * cm, 7.4 * cm]))
S.append(Spacer(1, 6))
S.append(P(
    f"<b>Interpretation of the CV.</b> A CV of {R['cv']:.2f} means the standard deviation is about {pct(R['cv'],0)} of the mean. "
    f"Common rules of thumb treat CV &lt; 15 % as low and CV &gt; 30–50 % as high dispersion; at 85 % salaries in this company "
    f"are very heterogeneous and the mean is a poor representative value. Part of this is structural (a single company mixes "
    f"junior and executive roles) and part is driven by the extreme top salaries — section 5 separates the two effects. "
    f"The IQR ({e(R['iqr'])}) shows that even the middle half of staff spans a wide band, from {e(R['q1'])} to {e(R['q3'])}."))

# ------------------------------------------------------------------ 5
S.append(P("5. Outliers and robustness", h1))
S.append(P(
    f"<b>1.5 × IQR rule.</b> Lower fence = Q1 − 1.5 × IQR = {num(R['q1'])} − 1.5 × {num(R['iqr'])} = {e(R['fence_low'])} "
    f"(negative, so no low outliers). Upper fence = Q3 + 1.5 × IQR = {num(R['q3'])} + 1.5 × {num(R['iqr'])} = "
    f"<b>{e(R['fence_high'])}</b>. The {R['n_outliers']} salaries above it, which are also the points plotted individually on the boxplot, are: "
    + ", ".join(num(v) for v in R["outliers"]) + f" € ({pct(R['n_outliers']/R['n'])} of employees)."))
S.append(table([
    ["Statistic", "All data (n = %d)" % R["n"], "Without outliers (n = %d)" % (R["n"] - R["n_outliers"]), "Change"],
    ["Mean", e(R["mean"]), e(R["mean_clean"]), pct(R["mean_clean"] / R["mean"] - 1)],
    ["Standard deviation", e(R["sd_sample"]), e(R["sd_clean"]), pct(R["sd_clean"] / R["sd_sample"] - 1)],
    ["CV", f"{R['cv']:.3f}", f"{R['cv_clean']:.3f}", pct(R["cv_clean"] / R["cv"] - 1)],
    ["Median", e(R["median"]), e(R["median_clean"]), pct(R["median_clean"] / R["median"] - 1)],
    ["IQR", e(R["iqr"]), e(R["iqr_clean"]), pct(R["iqr_clean"] / R["iqr"] - 1)],
], [3.6 * cm, 4.0 * cm, 4.6 * cm, 3.0 * cm]))
S.append(Spacer(1, 6))
S.append(P(
    f"<b>Robustness.</b> Removing fewer than 10 % of observations cuts the mean by {pct(1-R['mean_clean']/R['mean'],0)} and the "
    f"standard deviation by {pct(1-R['sd_clean']/R['sd_sample'],0)}. The standard deviation reacts most because it squares the "
    f"deviations, so a few distant values dominate it. The median changes by only {pct(1-R['median_clean']/R['median'],0)}: "
    f"it depends only on the rank of the central observations, and the change comes solely from n dropping from 74 to 67 "
    f"(the middle position moves), not from the size of the removed values. Replacing 400 000 € by 4 000 000 € would change "
    f"the mean and standard deviation dramatically but leave the median and IQR untouched. "
    f"The IQR also falls ({pct(1-R['iqr_clean']/R['iqr'],0)}), because Q3 lies in the sparse upper zone where the salaries are far apart, "
    f"but it is still bounded by the central 50 % of the data. <b>Conclusion:</b> median and IQR are robust (breakdown point 50 % and 25 %), "
    f"mean and standard deviation are not (breakdown point 0 %). For this distribution the median/IQR pair should be used to describe the "
    f"typical employee and the spread."))
S.append(P(
    "<b>Caution:</b> these points are statistical outliers, not errors. They are plausible executive or senior-expert salaries in a "
    "digital-services firm and are part of the real payroll. They should be kept for any cost or inequality analysis and only set aside to "
    "describe the “typical” employee. Note also that even without them the CV is still "
    f"{pct(R['cv_clean'],0)}: high dispersion is not only an outlier effect."))

# ------------------------------------------------------------------ 6
S.append(P("6. Managerial interpretation", h1))
S.append(P("6.1 Level of salary inequality", h2))
S.append(table([
    ["Indicator", "Value", "Reading"],
    ["Gini coefficient", f"{R['gini']:.3f}", "0 = everybody earns the same, 1 = one person earns everything"],
    ["Share of payroll, top 10 % (7 people)", pct(R["share_top10"]), "Almost 3 times their headcount share"],
    ["Share of payroll, bottom 50 % (37 people)", pct(R["share_bottom50"]), "Less than half their headcount share"],
    ["D9 / D1", f"{R['d9_d1']:.1f}", "The 90th percentile earns 7 × the 10th percentile"],
    ["Max / Min", f"{R['top_to_bottom']:.1f}", "Highest vs lowest salary"],
    ["Employees below the mean", pct(R["pct_below_mean"]), "Mean is not representative"],
], [5.6 * cm, 2.4 * cm, 8.0 * cm]))
S.append(Spacer(1, 6))
S.append(fig("fig_lorenz.png", 8.5, "Figure 4 — Lorenz curve. The shaded area between the curve and the equality line is half the Gini coefficient."))
S.append(P(
    f"Salary inequality is <b>high for a single company</b>. The pay structure has two parts: a large, compact core "
    f"(half of employees between {e(R['min'])} and {e(R['median'])}, with closely spaced salaries) and a small, widely spread top tier "
    f"in which salaries jump in steps of 10 000–20 000 €. A Gini of {R['gini']:.2f} inside one firm, and a D9/D1 ratio of {R['d9_d1']:.0f}, "
    f"indicate that pay is concentrated at the top: the 7 highest earners cost the company more ({pct(R['share_top10'],0)} of payroll) "
    f"than the 37 lowest-paid employees combined ({pct(R['share_bottom50'],0)}). Some inequality is expected in a firm combining junior "
    f"technical staff and senior management, but the size of the gaps, in particular the absence of a gradual progression above about "
    f"150 000 €, deserves a review."))

S.append(P("6.2 HR and managerial recommendations", h2))
recs = [
    ("Build a formal salary-band (grading) structure.",
     "The ECDF shows a dense core and a sparse, irregular top. Define job families and grades with explicit min–mid–max ranges, "
     "position every employee within their band, and check that large gaps reflect real differences in role and responsibility. "
     "This also prepares the company for the EU Pay Transparency Directive (2023/970), which requires pay structures based on objective, "
     "gender-neutral criteria."),
    ("Create visible career paths out of the low-salary core.",
     f"{pct(R['freq_table'][0]['f_i'],0)} of staff earn under 75 000 € and there is a thin bridge between the core and the top tier. "
     "Clear promotion criteria, an intermediate senior/lead level and targeted raises for high performers in the core would reduce "
     "attrition risk among the majority of employees, who are those most exposed to competing offers."),
    ("Review and condition top-tier pay.",
     f"Ten percent of employees receive {pct(R['share_top10'],0)} of payroll. Benchmark these salaries against the market and shift part "
     "of them from fixed to variable, performance-linked pay (bonus, equity). This keeps the total cost aligned with results and limits "
     "fixed-cost growth."),
    ("Use robust indicators for HR reporting and monitoring.",
     f"Communicate the median ({e(R['median'])}) rather than the mean as the “typical salary”; use the mean only for budgeting. "
     "Track the Gini, D9/D1 and the top-10 % share each year, and extend the dataset (job level, seniority, gender, department) so that "
     "the next analysis can separate justified differences from unexplained pay gaps."),
]
for i, (t, d) in enumerate(recs, 1):
    S.append(P(f"<b>R{i}. {t}</b> {d}"))

S.append(P("Method note", h2))
S.append(P("All computations were done in Python (pandas, NumPy, Matplotlib) with the script <i>salary_analysis.py</i>, submitted "
           "with this report. Quartiles use linear interpolation (NumPy default); the sample standard deviation (n − 1) is used for the CV; "
           "the Gini coefficient is computed from the Lorenz curve with the trapezoid rule."))

doc = SimpleDocTemplate("Salary_Analysis_Report.pdf", pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                        topMargin=1.8 * cm, bottomMargin=2 * cm, title="Univariate Statistics Project — Analysis of Annual Salaries",
                        author="Augustine")
doc.build(S, onFirstPage=footer, onLaterPages=footer)
print("ok")
