"""
MAT2007 project: At what price are Steam players most satisfied?

Satisfaction of a game = positive reviews / (positive + negative reviews).
Games are grouped into price bins and the bins are compared.

Usage:
    python steam_analysis.py                 # looks for steam_games.csv in this folder
    python steam_analysis.py path/to/file.csv
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
DATA_FILE = sys.argv[1] if len(sys.argv) > 1 else "steam_games.csv"
MIN_REVIEWS = 10          # ignore games with fewer reviews than this
MAX_PRICE = 200           # prices above this are treated as data errors
PRICE_BINS = [-0.01, 0, 4.99, 9.99, 19.99, 29.99, 39.99, 59.99, MAX_PRICE]
BIN_LABELS = ["Free", "0.01-4.99", "5-9.99", "10-19.99",
              "20-29.99", "30-39.99", "40-59.99", "60+"]


# ---------------------------------------------------------------------------
# 1. Load and clean
# ---------------------------------------------------------------------------
def load_and_clean(path, min_reviews):
    # Only load the columns we need (the full file is ~1 GB)
    cols = ["app_id", "name", "price", "price_status", "positive", "negative"]
    df = pd.read_csv(path, usecols=cols)
    n_start = len(df)

    df = df[df["price_status"] != "unavailable"]      # no price known
    df = df.dropna(subset=["price"])
    df = df[df["price"] <= MAX_PRICE]                  # remove absurd prices
    df = df.drop_duplicates(subset="app_id")

    df["n_reviews"] = df["positive"] + df["negative"]
    df = df[df["n_reviews"] >= min_reviews].copy()

    df["satisfaction"] = df["positive"] / df["n_reviews"]
    df["price_bin"] = pd.cut(df["price"], bins=PRICE_BINS, labels=BIN_LABELS)

    print(f"Loaded {n_start} games, kept {len(df)} after cleaning "
          f"(min {min_reviews} reviews, price <= {MAX_PRICE}).")
    return df


# ---------------------------------------------------------------------------
# 2. Statistics per price bin
# ---------------------------------------------------------------------------
def summarise_bins(df):
    g = df.groupby("price_bin", observed=True)["satisfaction"]
    summary = pd.DataFrame({
        "n_games": g.size(),
        "mean": g.mean(),
        "std": g.std(),
        "median": g.median(),
    })
    # Standard error of the mean = std / sqrt(N)
    summary["sem"] = summary["std"] / np.sqrt(summary["n_games"])
    return summary


def compare_bins(df, bin_a, bin_b):
    a = df.loc[df["price_bin"] == bin_a, "satisfaction"]
    b = df.loc[df["price_bin"] == bin_b, "satisfaction"]
    diff = a.mean() - b.mean()
    # Uncertainty of a difference of two independent means
    sigma = np.sqrt(a.sem() ** 2 + b.sem() ** 2)
    # diff / sigma = how many uncertainties apart the two means are
    print(f"  {bin_a} vs {bin_b}: difference = {100*diff:.2f} "
          f"+/- {100*sigma:.2f} percentage points "
          f"({diff/sigma:.2f} sigma)")


# ---------------------------------------------------------------------------
# 3. Plots
# ---------------------------------------------------------------------------
def plot_price_distribution(df):
    plt.figure(figsize=(8, 5))
    counts = df["price_bin"].value_counts().reindex(BIN_LABELS)
    plt.bar(counts.index, counts.values, color="steelblue")
    plt.xlabel("Price (USD)")
    plt.ylabel("Number of games")
    plt.title(f"Steam games per price range (>= {MIN_REVIEWS} reviews)")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig("price_distribution.png", dpi=200)
    plt.close()


def plot_satisfaction(summary):
    plt.figure(figsize=(8, 5))
    x = np.arange(len(summary))
    plt.errorbar(x, 100 * summary["mean"], yerr=100 * summary["sem"],
                 fmt="o-", capsize=5, color="darkred", label="Mean ± SEM")
    plt.plot(x, 100 * summary["median"], "s--", color="gray",
             alpha=0.7, label="Median")
    plt.xticks(x, summary.index, rotation=30)
    plt.xlabel("Price (USD)")
    plt.ylabel("Positive reviews (%)")
    plt.title("Player satisfaction vs. price on Steam")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("satisfaction_vs_price.png", dpi=200)
    plt.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    df = load_and_clean(DATA_FILE, MIN_REVIEWS)

    summary = summarise_bins(df)
    print("\nSatisfaction per price bin (in %):")
    print((summary[["mean", "std", "sem", "median"]] * 100).round(2)
          .assign(n_games=summary["n_games"]).to_string())

    best = summary["mean"].idxmax()
    print(f"\nHighest mean satisfaction: {best}")
    print("Comparisons with the best bin:")
    for other in ["Free", "0.01-4.99", "60+"]:
        if other != best:
            compare_bins(df, best, other)

    plot_price_distribution(df)
    plot_satisfaction(summary)
    print("\nSaved: price_distribution.png, satisfaction_vs_price.png")