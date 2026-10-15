# MAT2007_Steamgames_Final
MAT2007 project: analysing how Steam game prices relate to user review satisfaction.
# At what price are Steam players most satisfied?

Final project for **MAT2007 Introduction to Programming**, Maastricht University (MSP).
Author: Philippe Ritzen (i6249899)

## Research question

How does the price of a game on Steam relate to player satisfaction, measured as the
proportion of positive user reviews, and is there a price range in which satisfaction
is highest?

Satisfaction of one game is defined as:

```
satisfaction = positive / (positive + negative)
```

## Dataset

- **Source:** Sidorowicz, H. (2026). *Steam games dataset (daily updates)*. Kaggle.
  https://www.kaggle.com/datasets/hubertsidorowicz/steam-games-dataset-daily-updates
- **File used:** `steam_games.csv` (~1 GB, 160,873 rows, 42 columns).
  The other file in the dataset (`steam_games_reviews.csv`) is not used.
- The dataset is **not included in this repository** because it is too large for GitHub.

### How to get the data

1. Log in to Kaggle and open the link above.
2. Click **Download** and unzip the archive.
3. Put `steam_games.csv` in the same folder as `steam_analysis.py`
   (or give its path when running the script, see below).

### Cleaning

You do **not** need to clean the data yourself; the script does it automatically:

1. Remove games with no known price (`price_status == "unavailable"` or empty price).
2. Remove prices above $200 (treated as data errors).
3. Remove duplicate `app_id`s (the same game listed more than once).
4. Keep only games with at least 10 reviews (positive + negative), so the
   satisfaction value is not based on one or two reviews.

This leaves **55,894 games** (about 144 million reviews, 96% of all reviews in the data).

## Requirements

- Python 3.10 or newer
- Packages: `numpy`, `pandas`, `matplotlib` (version 3.9 or newer)

Install them with:

```bash
pip install numpy pandas "matplotlib>=3.9"
```

## How to run

From the project folder (for example in the VS Code terminal):

```bash
python steam_analysis.py
```

If the CSV file is somewhere else, give its path:

```bash
python steam_analysis.py path/to/steam_games.csv
```

Loading the 1 GB file can take up to a minute. Only the 6 needed columns are read
(`app_id`, `name`, `price`, `price_status`, `positive`, `negative`).

## What the script does

1. Loads and cleans the data (see above).
2. Groups games into 8 price bins: Free, 0.01-4.99, 5-9.99, 10-19.99, 20-29.99,
   30-39.99, 40-59.99, 60+ (USD).
3. Computes per bin: number of games, mean, median, standard deviation and the
   standard error of the mean (SEM = std / sqrt(N)), which is used as the uncertainty.
4. Compares the best bin with the Free, 0.01-4.99 and 60+ bins: the difference of
   the means with its uncertainty sigma = sqrt(SEM_a^2 + SEM_b^2), and how many
   sigma apart the two means are.
5. Robustness check: repeats the per-bin summary using only games with at least 50 reviews.
6. Saves three plots.

## Output

Results are printed in the terminal, and three figures are saved in the project folder:

- `satisfaction_vs_price.png` – mean satisfaction ± SEM (red) and median (grey) per price bin
- `price_distribution.png` – number of games per price bin
- `satisfaction_boxplot.png` – spread of satisfaction within each price bin

![Satisfaction vs price](satisfaction_vs_price.png)

## Repository contents

| File | Description |
|------|-------------|
| `steam_analysis.py` | Analysis code |
| `report.pdf` | Short report (2 pages, written in LaTeX on Overleaf) |
| `*.png` | Figures produced by the script |
| `README.md` | This file |
