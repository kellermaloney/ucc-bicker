import numpy as np
import pandas as pd
from utils import clr, cprint


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
