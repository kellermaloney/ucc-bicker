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


"""
A list of cutoffs for the total difference between a member's scores and the average scores,
which will be used to determine the score modifier for each member. If a member's total difference
is less than or equal to the value, they will be assigned the score modifier. If a member's total
difference is greater than the last value, they will be assigned the score modifier of the last value.
These values were calculated using 2023 data.

"""
TOTAL_DIFF_CUTOFFS = {
    0.5512: 1.0,
    0.6862: 0.9,
    0.8023: 0.85,
    1.0166: 0.6,
    1.2798: 0.45,
    1.3746: 0.30,
}


def calculate_scores(
    scores: DataFrame[ScoresSchema], bickerees: DataFrame[BickereesSchema]
):
    """
    Calculate the weighted score for each bickeree, and return two new
    dataframes which are the scores and the member info respectively.

        `scores` (DataFrame[ScoresSchema]): The scores DataFrame.
        `output` (pd.DataFrame): The output DataFrame.
    """

    score_percentages = scores.merge(
        bickerees[["bickeree_number", "bickeree_gender"]], on="bickeree_number"
    )

    # Group the scores by member email
    # Then count each member's score up, and normalize them (take percentage
    # Take the value of this index, using unstack, and create new dataframe
    score_percentages = (
        score_percentages.groupby(["member_email", "bickeree_gender"])["score"]
        .value_counts(normalize=True)
        .unstack(fill_value=0)
    )

    # Calculate the average percentage by gender
    average_percentages_by_gender = score_percentages.groupby("bickeree_gender").mean()

    # Calculate total_diff for each member within each gender group
    def calculate_total_diff(row: pd.Series, averages: pd.DataFrame):
        # row.name[0] is the member_email, and 1 is the gender
        return row.sub(averages.loc[row.name[1]], axis=0).abs().sum()  # type: ignore

    # The absolute
    score_percentages["total_diff"] = score_percentages.apply(
        calculate_total_diff, axis=1, averages=average_percentages_by_gender
    )

    # Function to determine the weight for a given Total_Difference value
    def determine_weight(value):
        for cutoff, weight in sorted(TOTAL_DIFF_CUTOFFS.items()):
            if value <= cutoff:
                return weight
        return TOTAL_DIFF_CUTOFFS[max(TOTAL_DIFF_CUTOFFS)]

    score_percentages["weight"] = score_percentages["total_diff"].apply(
        determine_weight
    )

    unweighted_scores = (
        scores.groupby("bickeree_number")["score"]
        .mean()
        .reset_index()
        .rename(columns={"score": "unweighted_score"})
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

    avg_scores_by_member = (
        scores.groupby("member_email")["score"]
        .mean()
        .reset_index()
        .rename(columns={"score": "avg_score"})
    )
    score_percentages = score_percentages.merge(avg_scores_by_member, on="member_email")

    # Add column with the number of members who bickered each bickeree
    num_members_per_bickeree = (
        scores.groupby("bickeree_number")["member_email"]
        .nunique()
        .reset_index()
        .rename(columns={"member_email": "num_members"})
    )
    bickeree_scoring_info = bickerees.merge(
        num_members_per_bickeree[["bickeree_number", "num_members"]],
        on="bickeree_number",
    )

    return (
        pd.merge(weighted_scores, bickeree_scoring_info, on="bickeree_number").merge(
            unweighted_scores, on="bickeree_number"
        ),
        score_percentages,
    )


def calculate_ranks_and_percentiles(output: pd.DataFrame):
    """Calculate ranks and percentiles for each bickeree, and return a new DataFrame
    with these columns added. This is based on weighted scores."""

    # If the weighted score column doesn't exist, return the original
    if (
        "weighted_score" not in output.columns
        or "unweighted_score" not in output.columns
    ):
        cprint(
            "Cannot calculate ranks and percentiles without weighted/unweighted scores.",
            clr.FAIL,
        )
        # Return the original
        return output

    modified = output.copy(deep=True)
    # Rank the bickerees by their weighted score, where 1 is the best and N is the worst
    modified["rank"] = (
        output["weighted_score"].rank(ascending=False, method="min").astype(int)
    )

    modified["unweighted_rank"] = (
        output["unweighted_score"].rank(ascending=False, method="min").astype(int)
    )

    # Get difference between weighted and unweighted rank
    modified["rank_diff"] = modified["unweighted_rank"] - modified["rank"]

    # Calculate percentiles, where 0.99 means the bickeree is in the top 1% of all bickerees,
    # and 0.01 means the bickeree is in the bottom 1% of all bickerees
    modified["percentile"] = output["weighted_score"].rank(pct=True, ascending=True)
    # Calculate rank by gender
    modified["rank_by_gender"] = (
        modified.groupby("bickeree_gender")["weighted_score"]
        .rank(ascending=False, method="min")
        .astype(int)
    )
    # Calculate percentile by gender
    modified["percentile_by_gender"] = modified.groupby("bickeree_gender")[
        "weighted_score"
    ].rank(pct=True, ascending=True)

    modified["unweighted_rank_by_gender"] = (
        modified.groupby("bickeree_gender")["unweighted_score"]
        .rank(ascending=False, method="min")
        .astype(int)
    )
    modified["rank_diff_by_gender"] = (
        modified["unweighted_rank_by_gender"] - modified["rank_by_gender"]
    )

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
        return output  # Return the original if required columns are missing

    def select_random_member_and_score(sub_df):
        selected_row = sub_df.sample(n=1)  # Randomly select one row
        member_email = selected_row["member_email"].iloc[0]
        score = selected_row["score"].iloc[0]
        return member_email, score

    # Group by bickeree_number and apply custom functions to find the member and score
    def group_func(x):
        lowest = x[x["score"] == x["score"].min()]
        highest = x[x["score"] == x["score"].max()]
        member_lowest, score_lowest = select_random_member_and_score(lowest)
        member_highest, score_highest = select_random_member_and_score(highest)
        return pd.Series(
            {
                "member_lowest_score": member_lowest,
                "lowest_score": score_lowest,
                "member_highest_score": member_highest,
                "highest_score": score_highest,
            }
        )

    bickeree_stats = scores.groupby("bickeree_number").apply(group_func).reset_index()

    # Merge the new stats back into the output DataFrame
    return output.merge(bickeree_stats, on="bickeree_number")
