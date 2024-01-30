from typing import Dict
import pandas as pd
import numpy as np

from data import BickereesSchema, MembersSchema, OutputDict, ScoresSchema, load_input
from data.validate import check_all_input
from utils import clr, cprint

# Typing
import numpy.typing as npt
from pandera.typing import DataFrame

DESIRED_FEMALE_AVERAGE = 3.5  # Each member's desired average for female bickerees
DESIRED_MALE_AVERAGE = 3.5  # Each member's desired average for male bickerees
NORMALIZATION_MINIMUM = 5  # the minimum number of bicker conversations (of one gender) that a member must complete in order for their scores to be normalized


"""
A list of quantiles that will be used to determine the cutoffs for each percentile.
If someone is in the 50th percentile, they will be assigned a score modifier of 1.0.
If someone is in the 75th percentile, they will be assigned a score modifier of 0.9.
If someone is in the 85th percentile, they will be assigned a score modifier of 0.8, and so on.
"""
PERCENTILE_CUTOFFS = {0.5: 1.0, 0.75: 0.9, 0.85: 0.8, 0.9: 0.7, 0.95: 0.6, 0.99: 0.4}

#############################################################################################################
# INPUT:    csv of with the following columns: member emails, bicker numbers, bicker scores, and gender
# OUTPUT:   csv with the following columns: bickeree, average raw score, average normalized score,
#           lowest score/member name, highest score/member name, and a list of all members who bickered them.
#
# Scores are normalized according to member averages, by female/male (non-binary not normalized).
# If a member assigns an average score of 4 to female bickerees, their scores will be normalized
# down to an average of 3 (subtract 1 from that member's assigned score for all female bickerees).
# This is conducted separately for males/females.
#
# Standard deviation can be a useful metric for which scores to look at more closely etc. If a person has a
# high standard deviation and a high average score, they may not have had many conversations, or may be
# more controversial in discussions. Conversely, a bickeree with a high average score and low standard
# deviation will likely have an uncontroversial discussion.
#############################################################################################################


def main():
    # Change the name of the document
    scores, members, bickerees = load_input()
    if not check_all_input(scores, members, bickerees):
        cprint("Could not validate input, exiting.", clr.FAIL)
        return

    # All member emails
    emails: npt.NDArray[np.str_] = members["member_email"].unique()

    # Group the scores by member email
    # Then count each member's score up, and normalize them (take percentage
    # Take the value of this index, using unstack, and create new dataframe
    score_percentages = (
        scores.groupby("member_email")["score"]
        .value_counts(normalize=True)
        .unstack(fill_value=0)
    )

    # The average score distribution of all members
    avg_score_percentage = score_percentages.mean()

    # The absolute
    score_percentages["total_diff"] = (
        score_percentages.subtract(avg_score_percentage, axis=1).abs().sum(axis=1)
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

    output = pd.merge(weighted_scores, bickerees, on="bickeree_number").merge(
        avg_scores, on="bickeree_number"
    )

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

    output = output.merge(bickeree_stats, on="bickeree_number")

    # Rank the bickerees by their weighted score, where 1 is the best and N is the worst
    output["rank"] = (
        output["weighted_score"].rank(ascending=False, method="min").astype(int)
    )
    # Calculate percentiles, where 0.99 means the bickeree is in the top 1% of all bickerees,
    # and 0.01 means the bickeree is in the bottom 1% of all bickerees
    output["percentile"] = output["weighted_score"].rank(pct=True, ascending=True)
    output.to_csv("bicker_output.csv")


if __name__ == "__main__":
    main()
