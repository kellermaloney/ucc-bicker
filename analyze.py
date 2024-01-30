import pandas as pd
from utils import clr, cprint


def calculate_ranks_and_percentiles(df: pd.DataFrame):
    """Calculate ranks and percentiles for each bickeree, and return a new DataFrame
    with these columns added. This is based on weighted scores."""

    # If the weighted score column doesn't exist, return the original
    if "weighted_score" not in df.columns:
        cprint(
            "Cannot calculate ranks and percentiles without weighted scores.", clr.FAIL
        )
        # Return the original
        return df

    modified = df.copy(deep=True)
    # Rank the bickerees by their weighted score, where 1 is the best and N is the worst
    modified["rank"] = (
        df["weighted_score"].rank(ascending=False, method="min").astype(int)
    )
    # Calculate percentiles, where 0.99 means the bickeree is in the top 1% of all bickerees,
    # and 0.01 means the bickeree is in the bottom 1% of all bickerees
    modified["percentile"] = df["weighted_score"].rank(pct=True, ascending=True)
    return modified
