# Univariate Analysis of Annual Salaries

A complete univariate statistical analysis of the gross annual salaries (in €) of 74 employees at a fictional digital-services company. The analysis looks at the shape of the distribution, its dispersion, outliers, robustness and salary inequality, and ends with HR recommendations.

*Project for **Proba Stat for Data Science**, EDC Paris Business School.*

---

## Key results

| Measure | Value |
|---|---|
| Employees (n) | 74 |
| Range | 28 000 € – 400 000 € |
| Mean | 108 547 € |
| Median | 71 000 € |
| Estimated mode (grouped data) | ≈ 55 469 € |
| Standard deviation (sample) | 92 345 € |
| IQR (Q3 − Q1) | 86 500 € (47 250 → 133 750 €) |
| Coefficient of variation | 0.85 |
| Skewness (Fisher) | 1.69 |
| Outliers (1.5 × IQR rule) | 7 salaries ≥ 280 000 € |
| Gini coefficient | 0.42 |
| Payroll share of top 10 % | 29.6 % |
| D9 / D1 | 7.0 |

**Takeaways**

- **Strong right skew:** mode < median < mean, and 68 % of employees earn less than the mean.
- **High dispersion:** CV = 0.85. The CV is still 0.65 after removing the outliers, so the high spread is not only an outlier effect.
- **Robustness:** removing the 7 outliers cuts the mean by 22 % and the standard deviation by 41 %, while the median falls only 10 %.
- **Inequality:** the 7 highest earners receive more of the payroll (30 %) than the 37 lowest-paid employees combined (22 %).

## Contents of the analysis

1. **Description of the variable:** type, unit and range, plus a frequency table with 8 classes of 50 000 € (Sturges' rule).
2. **Graphs:** histogram, empirical CDF, boxplot and Lorenz curve.
3. **Central tendency:** mean, median, and the mode estimated from the modal class.
4. **Dispersion:** variance, standard deviation, IQR, coefficient of variation and D9/D1.
5. **Outliers and robustness:** detection with the 1.5 × IQR rule, statistics recomputed without the outliers, and a comparison of robust and non-robust measures.
6. **Managerial interpretation:** level of inequality and four HR recommendations.

## Repository structure

```
├── data/
│   └── salary_data.csv          # input data (one column: salary)
├── salary_analysis.py           # computes all statistics, saves figures + results.json
├── build_report.py              # builds the PDF report from results.json and figures
├── Salary_Analysis_Report.pdf   # final report
└── README.md
```

## How to run

```bash
pip install pandas numpy matplotlib reportlab

python salary_analysis.py data/salary_data.csv   # → fig_*.png, results.json
python build_report.py                           # → Salary_Analysis_Report.pdf
```

> `build_report.py` uses the DejaVu Sans font from `/usr/share/fonts/truetype/dejavu/` (standard on Linux).
> On Windows or macOS, change the font path at the top of the script.

## Methodological notes

- Quartiles use linear interpolation (the NumPy default).
- The CV uses the sample standard deviation (n − 1). Population values are also reported.
- The mode is estimated with the grouped-data formula Mo = L + d₁/(d₁+d₂) × h, because no salary value repeats.
- Outliers are removed once, without repeating the rule on the reduced data. They are kept for the inequality analysis because they are plausible real salaries, not data errors.
- The Gini coefficient is computed from the Lorenz curve with the trapezoid rule.

## Tools

Python · pandas · NumPy · Matplotlib · ReportLab
