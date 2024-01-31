import numpy as np
import pandas as pd

from utils import clr, cprint

# Typing
from data import ScoresSchema, BickereesSchema
from pandera.typing import DataFrame


"""
A list of quantiles that will be used to determine the cutoffs for each percentile.
If someone is in the 50th percentile, they will be assigned a score modifier of 1.0.
If someone is in the 75th percentile, they will be assigned a score modifier of 0.9.
If someone is in the 85th percentile, they will be assigned a score modifier of 0.8, and so on.
"""
PERCENTILE_CUTOFFS = {0.5: 1.0, 0.75: 0.9, 0.85: 0.8, 0.9: 0.7, 0.95: 0.6, 0.99: 0.4}


def calculate_scores(
    scores: DataFrame[ScoresSchema], bickerees: DataFrame[BickereesSchema]
):
    """
    Calculate the weighted score for each bickeree, and return a new DataFrame
    with these columns added.

        `scores` (DataFrame[ScoresSchema]): The scores DataFrame.
        `output` (pd.DataFrame): The output DataFrame.
    """

    # Group the scores by member email
    # Then count each member's score up, and normalize them (take percentage
    # Take the value of this index, using unstack, and create new dataframe
    score_percentages = (
        scores.groupby(["member_email", "gender"])["score"]
        .value_counts(normalize=True)
        .unstack(fill_value=0)
    )

    # Calculate the average percentage by gender
    average_percentages_by_gender = score_percentages.groupby("gender").mean()

    # Calculate total_diff for each member within each gender group
    def calculate_total_diff(row: pd.Series, averages: pd.DataFrame):
        # row.name[0] is the member_email, and 1 is the gender
        return row.sub(averages.loc[row.name[1]], axis=0).abs().sum()  # type: ignore

    # The absolute
    score_percentages["total_diff"] = score_percentages.apply(
        calculate_total_diff, axis=1, averages=average_percentages_by_gender
    )

    # Calculate the percentile values
    percentile_values = {
        p: score_percentages["total_diff"].quantile(p) for p in PERCENTILE_CUTOFFS
    }

    # Function to determine the weight for a given Total_Difference value
    def determine_weight(value):
        for percentile, weight in sorted(PERCENTILE_CUTOFFS.items()):
            if value <= percentile_values[percentile]:
                return weight
        return PERCENTILE_CUTOFFS[max(PERCENTILE_CUTOFFS)]

    score_percentages["weight"] = score_percentages["total_diff"].apply(
        determine_weight
    )

    avg_scores = (
        scores.groupby("bickeree_number")["score"]
        .mean()
        .reset_index()
        .rename(columns={"score": "avg_score"})
    )
    score_percentages.reset_index(inplace=True)
    # Add weight to original scores
    weighted_scores = (
        pd.merge(
            scores, score_percentages[["member_email", "weight"]], on="member_email"
        )
        .groupby("bickeree_number")
        .apply(lambda x: np.sum(x["score"] * x["weight"]) / np.sum(x["weight"]))  # type: ignore
        .reset_index()
        .rename(columns={0: "weighted_score"})
    )

    return pd.merge(weighted_scores, bickerees, on="bickeree_number").merge(
        avg_scores, on="bickeree_number"
    )


def calculate_ranks_and_percentiles(output: pd.DataFrame):
    """Calculate ranks and percentiles for each bickeree, and return a new DataFrame
    with these columns added. This is based on weighted scores."""

    # If the weighted score column doesn't exist, return the original
    if "weighted_score" not in output.columns:
        cprint(
            "Cannot calculate ranks and percentiles without weighted scores.", clr.FAIL
        )
        # Return the original
        return output

    modified = output.copy(deep=True)
    # Rank the bickerees by their weighted score, where 1 is the best and N is the worst
    modified["rank"] = (
        output["weighted_score"].rank(ascending=False, method="min").astype(int)
    )
    # Calculate percentiles, where 0.99 means the bickeree is in the top 1% of all bickerees,
    # and 0.01 means the bickeree is in the bottom 1% of all bickerees
    modified["percentile"] = output["weighted_score"].rank(pct=True, ascending=True)
    return modified


def grab_lowest_and_highest_scores(scores: pd.DataFrame, output: pd.DataFrame):
    """Given a DataFrame of scores, return a new DataFrame with the lowest and highest
    scores for each bickeree merged on bickeree_number. If there are multiple members
    with the same lowest/highest score, randomly select one of them."""

    if "bickeree_number" not in scores.columns or "score" not in scores.columns:
        cprint(
            "Cannot grab lowest and highest scores without bickeree_number and/or score columns.",
            clr.FAIL,
        )
        # Return the original
        return output

    # Function to randomly select one member from those who gave the lowest/highest score
    def select_random_member(sub_df):
        return np.random.choice(sub_df["member_email"])

    # Group by bickeree_number and apply a custom function to find the member with the lowest and highest score
    bickeree_stats = (
        scores.groupby("bickeree_number")
        .apply(
            lambda x: pd.Series(
                {
                    "member_lowest_score": select_random_member(
                        x[x["score"] == x["score"].min()]  # type: ignore
                    ),
                    "member_highest_score": select_random_member(
                        x[x["score"] == x["score"].max()]  # type: ignore
                    ),
                }
            )
        )
        .reset_index()
    )

    return output.merge(bickeree_stats, on="bickeree_number")
