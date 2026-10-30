"""
A Problem with Presidents

Figures out how long each U.S. president lived, ranks them, runs some
basic stats, and puts it all into report.pdf.

To run it:  python3 analyze.py
"""

import textwrap
from datetime import date

import matplotlib
matplotlib.use("Agg")  # just save files, don't try to open a plot window
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
from dateutil.relativedelta import relativedelta

SOURCE = "U.S. Presidents Birth and Death Information - Sheet1.csv"
AUTHOR = "Zlata Kovrigina"
REPORT_DATE = date(2026, 10, 30)

# The CSV was pulled on this date, so anyone without a death date was still
# alive then. I measure their ages up to this day instead of today so the
# numbers match the data I was actually given.
DATA_DATE = date(2021, 9, 28)


def load_presidents():
    """Load the CSV and add year_of_birth, lived_years, lived_months, lived_days."""
    df = pd.read_csv(SOURCE)

    # The last "row" in the file is actually the source citation, not a
    # president, so I drop it.
    df = df[~df["PRESIDENT"].str.startswith("Reference")].copy()

    # The file mixes short and long month names ("Feb 22, 1732" vs
    # "July 4, 1826"). format="mixed" lets pandas handle both.
    df["birth"] = pd.to_datetime(df["BIRTH DATE"], format="mixed")
    df["death"] = pd.to_datetime(df["DEATH DATE"], format="mixed")

    # Blank death date = still alive when the data was collected.
    df["living"] = df["death"].isna()
    end = df["death"].fillna(pd.Timestamp(DATA_DATE))

    df["year_of_birth"] = df["birth"].dt.year
    df["lived_days"] = (end - df["birth"]).dt.days

    # Dividing days by 365 drifts because of leap years and uneven months,
    # so I use relativedelta, which counts real calendar years and months.
    years, months = [], []
    for born, ended in zip(df["birth"], end):
        gap = relativedelta(ended, born)
        years.append(gap.years)
        # Total months lived (e.g. 557 for JFK), not just the leftover 5.
        months.append(gap.years * 12 + gap.months)
    df["lived_years"] = years
    df["lived_months"] = months

    # Number the presidents in the order they appear in the CSV
    # (first row = 1). I use this for the weighted mean later.
    df["order"] = range(1, len(df) + 1)
    return df


def top_ten(df, longest):
    """Top 10 presidents by lifespan. longest=True for oldest first, False for youngest."""
    # Living presidents aren't done yet, so comparing their current age to
    # someone's full lifespan wouldn't be fair. I leave them out.
    dead = df[~df["living"]]
    ranked = dead.sort_values("lived_days", ascending=not longest).head(10)
    ranked = ranked[["PRESIDENT", "year_of_birth", "lived_years", "lived_months", "lived_days"]]
    ranked.insert(0, "rank", range(1, 11))
    return ranked


def statistics(df):
    """Mean, weighted mean, median, mode, max, min and std of lived_days."""
    dead = df[~df["living"]]
    days = dead["lived_days"]

    # The challenge doesn't say what the weights should be. If every
    # president gets the same weight you just get the regular mean again,
    # which isn't very interesting. So I weighted by order of presidency,
    # meaning more recent presidents count a bit more.
    weights = dead["order"]
    weighted_mean = (days * weights).sum() / weights.sum()

    # No two presidents lived the exact same number of days, so there's no
    # real mode. pandas would still hand back a value, so I check for that
    # and just say "none" instead.
    mode = days.mode()
    mode = "none (all values unique)" if len(mode) == len(days) else ", ".join(map(str, mode))

    return {
        "Mean": days.mean(),
        "Weighted mean (recent presidents count more)": weighted_mean,
        "Median": days.median(),
        "Mode": mode,
        "Max": days.max(),
        "Min": days.min(),
        "Standard deviation": days.std(),  # pandas uses n - 1 here (sample std)
    }


# ------------------------------------------------------------ building the PDF
# Each "page" is just a blank matplotlib figure the size of a sheet of paper.
# I place text and tables on it using x/y positions from 0 (bottom/left)
# to 1 (top/right), then save it as one page of the PDF.

def text_page(pdf, title, paragraphs):
    """A page with a title and some paragraphs (used for the conclusions)."""
    fig = plt.figure(figsize=(8.5, 11))
    fig.text(0.08, 0.93, title, fontsize=18, weight="bold")
    y = 0.88
    for p in paragraphs:
        wrapped = textwrap.fill(p, 95)  # wrap long lines so they fit the page
        fig.text(0.08, y, wrapped, fontsize=10, va="top", linespacing=1.5)
        # Move down based on how many lines that paragraph took up.
        y -= 0.025 * (wrapped.count("\n") + 1) + 0.025
    pdf.savefig(fig)
    plt.close(fig)


def table_page(pdf, tables):
    """A page with one or more tables stacked on top of each other."""
    fig = plt.figure(figsize=(8.5, 11))
    y = 0.95
    for title, frame in tables:
        fig.text(0.08, y, title, fontsize=13, weight="bold")
        # Make a box for the table that's tall enough for all its rows.
        height = 0.022 * (len(frame) + 1)
        ax = fig.add_axes([0.08, y - 0.04 - height, 0.84, height])
        ax.axis("off")
        # Add commas to big numbers so 34504 shows as 34,504.
        cells = [[f"{v:,}" if isinstance(v, int) and v > 9999 else v for v in row]
                 for row in frame.astype(object).values.tolist()]
        t = ax.table(cellText=cells, colLabels=list(frame.columns), loc="upper center", cellLoc="center")
        t.auto_set_font_size(False)
        t.set_fontsize(8.5)
        y -= height + 0.09  # leave a gap before the next table
    pdf.savefig(fig)
    plt.close(fig)


def make_report(df, longest, shortest, stats):
    """Write everything into report.pdf (4 pages)."""
    dead, living = df[~df["living"]], df[df["living"]]
    days = dead["lived_days"]
    yrs = 365.2425  # average length of a year; only used to show days as years

    # Turn the stats into a small table with days and the same value in years.
    stats_rows = []
    for name, value in stats.items():
        if isinstance(value, str):
            stats_rows.append([name, value, "—"])
        else:
            stats_rows.append([name, f"{value:,.1f}", f"{value / yrs:.1f}"])
    stats_table = pd.DataFrame(stats_rows, columns=["Measure", "lived_days", "years"])

    # The numbers in the written parts come straight from the data, so if
    # anything changes, the text updates with it.
    oldest, youngest = longest.iloc[0], shortest.iloc[0]
    summary = (
        f"Of the {len(df)} presidents in the data set, {len(dead)} had died. They lived "
        f"{days.mean():,.0f} days ({days.mean() / yrs:.1f} years) on average, with a median of "
        f"{days.median() / yrs:.1f} years and a standard deviation of {days.std() / yrs:.1f} years. "
        f"{oldest.PRESIDENT} lived longest ({oldest.lived_years} years) and {youngest.PRESIDENT} "
        f"shortest ({youngest.lived_years} years)."
    )
    methods = [
        "Data: the CSV from the challenge repository (PresidentsUSA.Net, collected "
        f"{DATA_DATE:%B %d, %Y}), used exactly as given. The last row is a citation, so it was removed.",
        "Date math: pandas and dateutil's relativedelta count real calendar years and months, so "
        "leap years and month lengths are correct. lived_years = completed years, lived_months = "
        "total completed months, lived_days = exact days from birth to death.",
        f"Living presidents ({', '.join(living['PRESIDENT'])}) have no death date. Their ages are "
        f"measured to the date the data was collected. Their lifespans aren't finished, so they are "
        f"left out of the rankings and statistics.",
        "Weighted mean: the challenge doesn't say what to weight by, and equal weights just give the "
        "mean. Each president is weighted by their position in the CSV (first row = 1), so later presidents count more.",
        "Mode: no two presidents lived the same number of days, so there is no mode.",
        "Standard deviation: sample version (divides by n - 1).",
    ]
    # Compare the first 20 presidents in the file to the rest, to see if
    # lifespans changed over time.
    first_20 = dead[dead["order"] <= 20]["lived_days"].mean() / yrs
    the_rest = dead[dead["order"] > 20]["lived_days"].mean() / yrs
    top3 = ", ".join(f"{r.PRESIDENT} ({r.year_of_birth})" for r in longest.head(3).itertuples())

    conclusions = [
        f"The typical president lived about {days.median() / yrs:.0f} to {days.mean() / yrs:.0f} "
        f"years, give or take about {days.std() / yrs:.0f} years.",
        f"The three longest lives were {top3}. Over time, though, the change is small: the first "
        f"20 presidents averaged {first_20:.1f} years and the rest averaged {the_rest:.1f} years.",
        f"Lifespans vary a lot: the gap between the longest and shortest life is "
        f"{(days.max() - days.min()) / yrs:.0f} years.",
        f"{len(living)} presidents had no death date in the data, so they are not included in "
        "these results.",
    ]

    with PdfPages("report.pdf") as pdf:
        # Page 1: title, summary, and how I did it
        fig = plt.figure(figsize=(8.5, 11))
        fig.text(0.08, 0.94, "A Problem with Presidents", fontsize=22, weight="bold")
        fig.text(0.08, 0.915, f"{AUTHOR}  ·  {REPORT_DATE:%B %d, %Y}", fontsize=10, color="gray")
        y = 0.87
        for heading, paragraphs in [("Summary", [summary]), ("Methods and assumptions", methods)]:
            fig.text(0.08, y, heading, fontsize=13, weight="bold")
            y -= 0.03
            for p in paragraphs:
                wrapped = textwrap.fill(p, 95)
                fig.text(0.08, y, wrapped, fontsize=10, va="top", linespacing=1.5)
                y -= 0.021 * (wrapped.count("\n") + 1) + 0.015
            y -= 0.02
        pdf.savefig(fig)
        plt.close(fig)

        # Page 2: the two top-10 tables
        table_page(pdf, [("Top 10 longest-lived presidents", longest),
                         ("Top 10 shortest-lived presidents", shortest)])

        # Page 3: stats table + histogram
        fig = plt.figure(figsize=(8.5, 11))
        fig.text(0.08, 0.95, "Statistics of lived_days", fontsize=13, weight="bold")
        ax = fig.add_axes([0.08, 0.72, 0.84, 0.2])
        ax.axis("off")
        t = ax.table(cellText=stats_table.values.tolist(), colLabels=list(stats_table.columns),
                     loc="upper center", cellLoc="center", colWidths=[0.55, 0.25, 0.2])
        t.auto_set_font_size(False)
        t.set_fontsize(9)

        # I went with a histogram because it shows the shape of the data:
        # where most presidents fall and how spread out they are. Each bar
        # covers 5 years (converted to days so the axis is in lived_days).
        ax = fig.add_axes([0.1, 0.33, 0.82, 0.32])
        bins = [y * yrs for y in range(45, 100, 5)]
        ax.hist(days, bins=bins, color="#2563eb", edgecolor="white")
        # Mean and median lines, so you can see they're pretty close.
        ax.axvline(days.mean(), color="black", label=f"mean ({days.mean() / yrs:.1f} y)")
        ax.axvline(days.median(), color="black", ls="--", label=f"median ({days.median() / yrs:.1f} y)")
        # Label the ticks in days with years underneath, since days alone are hard to picture.
        ax.set_xticks(bins)
        ax.set_xticklabels([f"{int(b):,}\n({round(b / yrs)} y)" for b in bins], fontsize=7)
        ax.set_xlabel("lived_days (years)")
        ax.set_ylabel("Number of presidents")
        ax.set_title("Distribution of lived_days", loc="left", weight="bold")
        ax.legend(frameon=False)
        ax.spines[["top", "right"]].set_visible(False)

        q1, q3 = days.quantile(0.25) / yrs, days.quantile(0.75) / yrs
        note = (f"A histogram shows how lifespans are spread out: the middle half of presidents died "
                f"between about {q1:.0f} and {q3:.0f}, with fewer at the very young and very old ends. "
                f"The mean and median are close, so the shape is roughly symmetric.")
        fig.text(0.08, 0.25, textwrap.fill(note, 95), fontsize=10, va="top", linespacing=1.5)
        pdf.savefig(fig)
        plt.close(fig)

        # Page 4: conclusions
        text_page(pdf, "Conclusions", ["• " + c for c in conclusions])


def main():
    df = load_presidents()
    longest, shortest = top_ten(df, True), top_ten(df, False)
    stats = statistics(df)
    # Also save the full table with the new columns in case anyone wants the raw numbers.
    df.drop(columns=["birth", "death"]).to_csv("presidents_with_lifespans.csv", index=False)
    make_report(df, longest, shortest, stats)
    print("Created report.pdf and presidents_with_lifespans.csv")


if __name__ == "__main__":
    main()