import numpy as np
import pandas as pd
from data import MembersSchema
from utils import clr, cprint

from pandera.typing import DataFrame
from typing import List


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
