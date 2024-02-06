import numpy as np
import pandas as pd
from data import MembersSchema, ScoresSchema
from utils import clr, cprint
import time

from pandera.typing import DataFrame
from typing import List


def remove_duplicates_and_na_scores(
    scores: DataFrame[ScoresSchema],
) -> DataFrame[ScoresSchema]:
    """
    Remove any duplicate rows and rows with missing values from the scores DataFrame.
    Returns a new DataFrame with the duplicates and missing values removed.

        `scores` (DataFrame[ScoresSchema]): The scores DataFrame.
    """

    cprint(
        f"Removing duplicates and missing values from scores... ({scores.shape[0]} rows)",
        clr.OKCYAN,
    )
    df = scores.copy(deep=True)
    df.dropna(inplace=True)
    time.sleep(0.5)
    cprint(
        f"Sucessfully removed {scores.shape[0] - df.shape[0]} NA rows. ({df.shape[0]} rows)",
        clr.OKGREEN,
    )

    non_na_rows = df.shape[0]
    # Invert the array to remove the first instance of the duplicate
    df = df[::-1]
    df.drop_duplicates(subset=["member_email", "bickeree_number"], inplace=True)
    df = df[::-1]

    time.sleep(0.5)
    cprint(
        f"Sucessfully removed {non_na_rows - df.shape[0]} rows. ({df.shape[0]} rows)",
        clr.OKGREEN,
    )
    return DataFrame[ScoresSchema](df)


def replace_emails(
    members: DataFrame[MembersSchema],
    output: pd.DataFrame,
    columns: List[str] = ["member_lowest_score", "member_highest_score"],
):
    """
    Replace emails in the members DataFrame with the member's name. Returns a new
    DataFrame with the emails replaced with the member's name.

        `members` (DataFrame[MembersSchema]): The members DataFrame.
        `output` (pd.DataFrame): The output DataFrame.
        `columns` (List[str]): The columns to replace the emails with the member's name.
    """
    df = output.copy(deep=True)

    for column in columns:
        if column in df.columns:
            df = df.merge(
                members[["member_email", "member_name"]],
                left_on=column,
                right_on="member_email",
                how="left",
            )
            # Replace the original column with the name
            df[column] = df["member_name"]
            # Drop the extra columns added by the merge
            df.drop(["member_name", "member_email"], axis=1, inplace=True)

    return df
