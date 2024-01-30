from typing import TypeVar, TypedDict
import pandas as pd
import numpy as np
import pandera as pa
import sys

from pandera.typing import DataFrame

from utils import cprint, clr


class ScoresSchema(pa.DataFrameModel):
    """The schema for the input data. Validates the data types, and mandates
    specific column names."""

    member_email: str = pa.Field()
    bickeree_number: int = pa.Field()
    score: int = pa.Field()
    gender: int = pa.Field()


class MembersSchema(pa.DataFrameModel):
    """The schema for the association between member and their email."""

    member_email: str = pa.Field()
    member_name: str = pa.Field()


class BickereesSchema(pa.DataFrameModel):
    """The schema for the association between bickeree and their number."""

    bickeree_number: int = pa.Field()
    bickeree_name: str = pa.Field()


class OutputDict(TypedDict):
    """The schema for the output data. Validates the data types, and mandates
    specific column names."""

    bickeree_number: int
    bickeree_name: str
    score: int


T = TypeVar("T", bound=pa.DataFrameModel)


def _grab_csv(filename: str, schema: type[T]) -> DataFrame[T]:
    """Reads the given CSV file into a pandas DataFrame."""

    # Read the CSV file into a pandas DataFrame and validate data types
    try:
        df = pd.read_csv(filename)
    except:
        cprint(f"Could not find file {filename}", clr.FAIL)
        sys.exit(1)

    # Attempt to validate the dataframe file that was loaded
    try:
        validated = DataFrame[T](df)
    except:
        cprint(f"Could not validate file {filename}", clr.FAIL)
        sys.exit(1)

    return validated


def load_input() -> (
    tuple[DataFrame[ScoresSchema], DataFrame[MembersSchema], DataFrame[BickereesSchema]]
):
    """
    Load the input data from a CSV file into a pandas DataFrame. Statically typed
    using pandera, so that we can validate the data types of the input data.

    filename : str
        The name of the CSV file to load.
    """

    args = sys.argv[1:]
    if len(args) != 3:
        cprint(
            "Usage: python bicker.py <scores-filename> <members-filename> <bickerees-filename>",
            clr.FAIL,
        )
        sys.exit(1)

    scores_filename = args[0]
    members_filename = args[1]
    bickerees_filename = args[2]

    # Read the CSV file into a pandas DataFrame and validate data types
    scores = _grab_csv(scores_filename, ScoresSchema)
    members = _grab_csv(members_filename, MembersSchema)
    bickerees = _grab_csv(bickerees_filename, BickereesSchema)

    return scores, members, bickerees
