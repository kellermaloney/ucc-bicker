import numpy as np

from . import BickereesSchema, MembersSchema, ScoresSchema
from utils import clr, cprint

# Typing
import numpy.typing as npt
from pandera.typing import DataFrame


def check_all_input(
    scores_df: DataFrame[ScoresSchema],
    members_df: DataFrame[MembersSchema],
    bickerees_df: DataFrame[BickereesSchema],
) -> bool:
    """
    Validate the input data, ensuring that all emails in scores_df are in members_df,
    and all bickeree numbers in scores_df are in bickerees_df. Returns True if the
    input data is valid, False otherwise.

        `scores_df` (DataFrame[ScoresSchema]): The scores DataFrame.
        `members_df` (DataFrame[MembersSchema]): The members DataFrame.
        `bickerees_df` (DataFrame[BickereesSchema]): The bickerees DataFrame.
    """

    # Get all unique emails
    emails: npt.NDArray[np.str_] = scores_df["member_email"].unique()

    # Check if all emails in scores_df are in members_df without for loop
    contains_emails = np.isin(emails, members_df["member_email"].unique())
    if not contains_emails.all():
        cprint("Not all emails in scores_df are in members_df", clr.FAIL)
        cprint(f"Emails not included: {emails[~contains_emails]}", clr.WARNING)
        return False

    # Check if all bickeree numbers in scores_df are in bickerees_df
    bickeree_numbers: npt.NDArray[np.int_] = scores_df["bickeree_number"].unique()
    contains_bickerees = np.isin(
        bickeree_numbers, bickerees_df["bickeree_number"].unique()
    )
    if not contains_bickerees.all():
        cprint("Not all bickeree numbers in scores_df are in bickerees_df", clr.FAIL)
        cprint(
            f"Bickeree numbers not included: {bickeree_numbers[~contains_bickerees]}",
            clr.WARNING,
        )
        return False

    return True
