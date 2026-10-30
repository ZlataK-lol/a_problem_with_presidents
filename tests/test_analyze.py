import os
import sys

import pytest

# Run from the project folder so analyze.py can find the CSV.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import analyze  # noqa: E402


@pytest.fixture(scope="module")
def df():
    return analyze.load_presidents()


def get(df, name):
    return df[df["PRESIDENT"] == name].iloc[0]


def test_citation_row_removed(df):
    assert len(df) == 45


def test_jfk_exact_lifespan(df):
    # May 29, 1917 -> Nov 22, 1963
    jfk = get(df, "John F. Kennedy")
    assert jfk["year_of_birth"] == 1917
    assert jfk["lived_years"] == 46
    assert jfk["lived_months"] == 557
    assert jfk["lived_days"] == 16978


def test_both_month_formats_parse(df):
    # "Apr 28, 1758" and "July 4, 1831"
    monroe = get(df, "James Monroe")
    assert str(monroe["birth"].date()) == "1758-04-28"
    assert str(monroe["death"].date()) == "1831-07-04"


def test_living_presidents(df):
    assert df["living"].sum() == 6
    assert get(df, "Jimmy Carter")["lived_years"] == 96  # age on Sep 28, 2021


def test_rankings(df):
    longest, shortest = analyze.top_ten(df, True), analyze.top_ten(df, False)
    assert len(longest) == 10
    assert longest.iloc[0]["PRESIDENT"] == "George Bush"
    assert shortest.iloc[0]["PRESIDENT"] == "John F. Kennedy"
    assert not set(longest["PRESIDENT"]) & set(df[df["living"]]["PRESIDENT"])


def test_statistics(df):
    import statistics
    days = list(df[~df["living"]]["lived_days"])
    stats = analyze.statistics(df)
    assert stats["Mean"] == pytest.approx(statistics.mean(days))
    assert stats["Median"] == statistics.median(days)
    assert stats["Standard deviation"] == pytest.approx(statistics.stdev(days))
    assert stats["Mode"].startswith("none")