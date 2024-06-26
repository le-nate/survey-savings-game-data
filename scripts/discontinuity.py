"""
Identify change in purchase behavior before and after inflation phase changes

***Measure of discontinuity***
measure = mean([mean(after_430) - mean(before_430)], [mean(after_1012) - mean(before_1012)]),
where before_430 is mean(quantity months 28-30) / `decision quantity` at start of month 28
and after_430 is mean(quantity months 31-33) / `decision quantity` at start of month 2
"""

import logging

# from pathlib import Path
# from typing import List, Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# from tqdm.auto import tqdm

# from preprocess import final_df_dict
from calc_opp_costs import df_str

# * Output settings
logging.basicConfig(level="INFO")
pd.set_option("display.max_rows", None, "display.max_columns", None)

# * Define `decision quantity` measure
DECISION_QUANTITY = "cum_decision"

# * Define purchase window, i.e. how many months before and after inflation phase change to count
WINDOW = 3

# * Define phase change months to analyze
CHANGE_430 = 30
CHANGE_1012 = 12
CHANGE_1012_2 = 36

# * Define discontinuity measure for graph
Y = "avg_q"


def purchase_discontinuity(
    df: pd.DataFrame,
    decision_quantity: str,
    window: int,
) -> pd.DataFrame:
    """Generates dataframe with column for change in purchase behavior before
    and after inflation phase changes"""
    cols_430 = [
        m
        for n in range(1, 120 // CHANGE_430)
        for m in range(CHANGE_430 * n - window + 1, CHANGE_430 * n + window + 1)
    ]
    cols_1012 = [
        m
        for n in range(1, 120 // CHANGE_1012)
        for m in range(CHANGE_1012 * n - window + 1, CHANGE_1012 * n + window + 1)
    ]

    logging.info("Months for 4x30: %s", cols_430)
    logging.info("Months for 10x12: %s", cols_1012)

    ## Set `decision_quantity` to previous month's
    ## The `decision_quantity` at month=1 for each participant should be NaN
    df[decision_quantity] = df.groupby("participant.code")[decision_quantity].shift(1)

    ## Remove all `decision quantitys` except at first phase change (and third from 10x12)
    df[decision_quantity] = np.where(
        (
            (df["participant.inflation"] == 1012)
            & (df["month"] == CHANGE_1012 - (window - 1))
        )
        | (
            (df["participant.inflation"] == 1012)
            & (df["month"] == CHANGE_1012_2 - (window - 1))
        )
        | (
            (df["participant.inflation"] == 430)
            & (df["month"] == CHANGE_430 - (window - 1))
        ),
        df[decision_quantity],
        np.NaN,
    )

    ## Forward fill `decision quantity` with value at start of first month in window
    df[decision_quantity] = df.groupby("participant.code")[decision_quantity].ffill()

    ## Take rolling average of quantity purchased with window and then
    df["avg_q"] = df.groupby("participant.code")["decision"].transform(
        lambda x: x.rolling(window).mean()
    )

    ## Calculate percentage of initial decision_quantity at start of window
    df["avg_q_%"] = df["avg_q"] / df[decision_quantity] * 100

    return df


def main() -> None:
    """Run script"""
    df_disc = df_str[df_str.columns.to_list()[:12]].copy()
    print(df_disc.head())
    logging.debug(df_disc.shape)

    df_disc = purchase_discontinuity(
        df_disc, decision_quantity=DECISION_QUANTITY, window=WINDOW
    )
    print(df_disc.head())
    logging.debug(df_disc.shape)
    ## Assign starting month
    scatter_dict = {
        # 1012: {"month": CHANGE_1012, "title": "10x12 (1st inflation increase)"},
        # "1012_2": {"month": CHANGE_1012_2, "title": "10x12 (2nd inflation increase)"},
        430: {
            "month": CHANGE_430,
            "title": "4x30 (Pre-treatment)",
            "phase": "pre",
        },
        "430_2": {
            "month": CHANGE_430,
            "title": "4x30 (Post-treatment)",
            "phase": "post",
        },
    }

    sequence_layout = [
        # 1012,
        # "1012_2",
        430,
        "430_2",
    ]  ## Define which side each sequence should be on

    fig, axes = plt.subplots(ncols=len(sequence_layout), sharey=True, figsize=(10, 5))

    ## Define a custom palette with only black
    custom_palette = sns.color_palette(["black"])

    ## Loop through scatter_dict to generate dataframes for before & after figures for each sequence
    for seq, v in scatter_dict.items():
        before_after = [v["month"], (v["month"] + WINDOW)]
        if seq == 430 or seq == 1012:
            v["data"] = df_disc[
                (df_disc["participant.inflation"] == seq)
                & df_disc["month"].isin(before_after)
                & (df_disc["phase"] == v["phase"])
            ]
        elif seq == "430_2":
            v["data"] = df_disc[
                (df_disc["participant.inflation"] == 430)
                & df_disc["month"].isin(before_after)
                & (df_disc["phase"] == v["phase"])
            ]
        else:
            v["data"] = df_disc[
                (df_disc["participant.inflation"] == 1012)
                & df_disc["month"].isin(before_after)
                & (df_disc["phase"] == v["phase"])
            ]

    ## Loop through sequences and generate connected scatter plots
    for i, seq in enumerate(sequence_layout):
        data = scatter_dict[seq]["data"]
        start = scatter_dict[seq]["month"]
        end = start + WINDOW
        sns.violinplot(
            ax=axes[i],
            data=data,
            x="month",
            y=Y,
            split=True,
            palette="viridis",
            alpha=0.25,
            inner=None,
            dodge=True,
        )
        sns.stripplot(
            ax=axes[i],
            data=data,
            x="month",
            y=Y,
            jitter=0.015,
            palette="viridis",
            alpha=0.4,
            legend=None,
        )
        sns.pointplot(
            ax=axes[i],
            data=data,
            x="month",
            y=Y,
            estimator=np.mean,
            errorbar=None,
            dodge=0.0,
            palette=custom_palette,
        )
        ## Plot lines with connected points
        x1 = np.array(
            data["month"][data["month"] == start] - start
        )  ## Must shift leftward manually
        x2 = np.array(
            data["month"][data["month"] == end] - (end - 1)
        )  ## Must shift leftward manually
        y1 = np.array(data[Y][data["month"] == start])
        y2 = np.array(data[Y][data["month"] == end])
        for n, m in enumerate(x1):
            axes[i].plot(
                [x1[n], x2[n]],
                [y1[n], y2[n]],
                ## Define color
                color="grey",
                alpha=0.15,
            )
        ## Line for means
        before = data[(data["month"] == start)][Y].mean()
        after = data[(data["month"] == end)][Y].mean()
        axes[i].plot([0, 1], [before, after], color="black")

        ## Add title and labels
        title = scatter_dict[seq]["title"]
        axes[i].set_title(title)

        ## Change x-axis labels
        x_labels = ["Before" if m < end else "After" for m in data["month"].values]
        axes[i].set_xticklabels(x_labels)

        axes[i].set_xlabel("")  ## Remove x-axis subtitles
        axes[i].set_ylabel("")  ## Remove y-axis subtitles

    ## Common title
    fig.suptitle(
        f"Change in average quantity purchased in {WINDOW}-month window before and after inflation phase change"
    )
    ## Common x-axis title
    fig.text(0.5, 0.04, "Inflation phase change", ha="center")
    ## Common y-axis title
    fig.text(0.04, 0.5, "Average quantity purchased", va="center", rotation="vertical")
    plt.show()


if __name__ == "__main__":
    main()
