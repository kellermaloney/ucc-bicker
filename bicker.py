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

    # Initialize the output dictionary
    output: Dict[str, OutputDict] = {}

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

    return

    # create an empty array to store the output
    master = np.empty(
        (len(emails), 2), dtype=object
    )  # Initialize an empty array to store processed data

    # iterate through the unique emails
    for i, email in enumerate(emails):
        # find all instances of the current email in the input array
        mask: npt.NDArray[np.bool_] = (
            scores_df["member_email"] == email
        )  # Create a boolean mask for rows with the current email
        email_rows = scores_df[
            mask
        ]  # Apply the mask to extract all rows for the current email

        print(email_rows)
        return

        # create a list of tuples containing the bickeree name and score and gender for that bickeree
        bickeree_scores = [
            (row[1], row[2], row[3]) for row in email_rows
        ]  # Extract bickeree data for the current email

        # store the name and list of movies in the output array
        master[i, 0] = email  # Store the email in the first column of the master array
        master[
            i, 1
        ] = bickeree_scores  # Store the bickeree data in the second column of the master array

    # calculate member score averages for male and female bickerees,
    # and find the normalization to apply to their assigned scores
    emails = master[:, 0]  # Extract the list of emails from the master array
    female_mean = []  # Initialize a list to store average scores for female bickerees
    female_delta = (
        []
    )  # Initialize a list to store score normalization values for female bickerees
    male_mean = []  # Initialize a list to store average scores for male bickerees
    male_delta = (
        []
    )  # Initialize a list to store score normalization values for male bickerees
    avg_female_delta = (
        []
    )  # Initialize a list to store the average normalization values for female bickerees
    avg_male_delta = (
        []
    )  # Initialize a list to store the average normalization values for male bickerees

    # create a list of member std for women
    for row in master:
        female_scores = []  # List to store individual scores for female bickerees
        male_scores = []  # List to store individual scores for male bickerees
        for bickeree in row[1]:
            if int(bickeree[2]) == 0:  # Check if the bickeree is female
                female_scores.append(
                    int(bickeree[1])
                )  # Add the score to the female list
            else:
                male_scores.append(int(bickeree[1]))  # Add the score to the male list
        # Calculate the mean of the scores and determine the normalization delta
        female_mean.append(np.mean(female_scores))
        male_mean.append(np.mean(male_scores))
        if (
            len(female_scores) >= NORMALIZATION_MINIMUM
        ):  # Check if there are enough scores to normalize
            female_delta.append(
                DESIRED_FEMALE_AVERAGE - np.mean(female_scores)
            )  # Calculate the delta for normalization
        else:
            female_delta.append(0)  # If not enough scores, no normalization is applied
        if (
            len(male_scores) >= NORMALIZATION_MINIMUM
        ):  # Check if there are enough scores to normalize
            male_delta.append(
                DESIRED_MALE_AVERAGE - np.mean(male_scores)
            )  # Calculate the delta for normalization
        else:
            male_delta.append(0)  # If not enough scores, no normalization is applied

        avg_female_delta.append(
            np.mean(female_delta)
        )  # Calculate the average normalization delta for females
        avg_male_delta.append(
            np.mean(male_delta)
        )  # Calculate the average normalization delta for males

    print(
        "Avg female delta: " + str(np.mean(avg_female_delta))
    )  # Print the average normalization delta for females
    print(
        "Avg male delta: " + str(np.mean(avg_male_delta))
    )  # Print the average normalization delta for males
    print(
        "Avg female score: " + str(np.mean(female_mean))
    )  # Print the average score for females

    # creates a single n by 3 np array of every email, std for women, std for men
    stats = [
        emails,
        female_mean,
        female_delta,
        male_mean,
        male_delta,
    ]  # Combine the calculated data into a single list
    stats = np.transpose(
        stats
    )  # Transpose the list to create an array where each row represents a member
    max_col = np.argmax(
        stats, axis=0
    )  # Find the index of the maximum value in each column
    min_col = np.argmin(
        stats, axis=0
    )  # Find the index of the minimum value in each column
    print(
        "HIGHEST AVG. FEMALE SCORES: "
        + stats[max_col[1]][0]
        + " ("
        + str(stats[max_col[1]][1])
        + ")"
    )  # Print the member with the highest average score for females
    print(
        "HIGHEST AVG. MALE SCORES: "
        + stats[max_col[3]][0]
        + " ("
        + str(stats[max_col[3]][3])
        + ")"
    )  # Print the member with the highest average score for males
    print(
        "LOWEST AVG. FEMALE SCORES: "
        + stats[min_col[1]][0]
        + " ("
        + str(stats[min_col[1]][1])
        + ")"
    )  # Print the member with the lowest average score for females
    print(
        "LOWEST AVG. MALE SCORES: "
        + stats[min_col[3]][0]
        + " ("
        + str(stats[min_col[3]][3])
        + ")"
    )  # Print the member with the lowest average score for males

    # adjusted master replaces gender with a normalized score for that member
    master_adj = np.copy(master)  # Create a copy of the master array to adjust scores
    bickeree_output = (
        []
    )  # Initialize a list to store the final output data for each bickeree
    avg_male_raw = []  # Initialize a list to store raw scores for male bickerees
    avg_female_raw = []  # Initialize a list to store raw scores for female bickerees
    avg_male_norm = (
        []
    )  # Initialize a list to store normalized scores for male bickerees
    avg_female_norm = (
        []
    )  # Initialize a list to store normalized scores for female bickerees

    for row in master_adj:
        member_index = np.where(stats == row[0])[0][
            0
        ]  # Find the index of the current member in the stats array
        for bickeree in row[1]:  # Iterate over each bickeree's data
            score = int(bickeree[1])  # Extract the raw score
            gender = int(bickeree[2])  # Extract the gender
            female_delta = stats[member_index][
                2
            ]  # Get the normalization delta for female scores
            male_delta = stats[member_index][
                4
            ]  # Get the normalization delta for male scores
            if gender == 0:  # Check if the bickeree is female
                # calculate normed scores
                score_adj = score + female_delta  # Apply normalization to the score
                avg_female_raw.append(
                    score
                )  # Add the raw score to the list of female raw scores
                avg_female_norm.append(
                    score_adj
                )  # Add the normalized score to the list of female normalized scores
            else:  # if male
                score_adj = score + male_delta  # Apply normalization to the score
                avg_male_raw.append(
                    score
                )  # Add the raw score to the list of male raw scores
                avg_male_norm.append(
                    score_adj
                )  # Add the normalized score to the list of male normalized scores

            # Check if the bickeree is already in the output list and update their data
            if bickeree[0] not in [b[0] for b in bickeree_output]:
                bickeree_output.append(
                    [bickeree[0], [score], [score_adj], [row[0] + ": " + str(score)]]
                )
            else:
                b_idx = [b[0] for b in bickeree_output].index(
                    bickeree[0]
                )  # Find the index of the bickeree in the output list
                bickeree_output[b_idx][1].append(
                    score
                )  # Add the raw score to the bickeree's list of scores
                bickeree_output[b_idx][2].append(
                    score_adj
                )  # Add the normalized score to the bickeree's list of normalized scores
                bickeree_output[b_idx][3].append(
                    row[0] + ": " + str(score)
                )  # Add the member's name and score to the list of all scores

    print(
        "Avg female raw score: " + str(np.mean(avg_female_raw))
    )  # Print the average raw score for females
    print(
        "Avg Male raw score: " + str(np.mean(avg_male_raw))
    )  # Print the average raw score for males
    print(
        "Avg female norm score: " + str(np.mean(avg_female_norm))
    )  # Print the average normalized score for females
    print(
        "Female std: " + str(np.std(avg_female_norm))
    )  # Print the standard deviation of the normalized scores for females
    print(
        "Avg Male norm score: " + str(np.mean(avg_male_norm))
    )  # Print the average normalized score for males
    print(
        "Male std: " + str(np.std(avg_male_norm))
    )  # Print the standard deviation of the normalized scores for males

    # after processing all member-assigned scores, bickeree score table should be fully populated
    for idx in range(len(bickeree_output)):
        # get highest and lowest scores, and emails at corresponding idxs
        min_score = min(
            bickeree_output[idx][2]
        )  # Find the minimum normalized score for the current bickeree
        min_member = bickeree_output[idx][3][
            bickeree_output[idx][2].index(min_score)
        ]  # Find the member who gave the minimum score
        max_score = max(
            bickeree_output[idx][2]
        )  # Find the maximum normalized score for the current bickeree
        max_member = bickeree_output[idx][3][
            bickeree_output[idx][2].index(max_score)
        ]  # Find the member who gave the maximum score
        stddev_score = np.std(
            bickeree_output[idx][1]
        )  # Calculate the standard deviation of the raw scores
        bickeree_output[idx][1] = np.mean(
            bickeree_output[idx][1]
        )  # Calculate the average raw score
        bickeree_output[idx][2] = np.mean(
            bickeree_output[idx][2]
        )  # Calculate the average normalized score
        bickeree_output[idx][3] = ", ".join(
            bickeree_output[idx][3]
        )  # Join all member names and scores into a single string
        bickeree_output[idx].append(
            min_member
        )  # Append the member with the minimum score
        bickeree_output[idx].append(
            max_member
        )  # Append the member with the maximum score
        bickeree_output[idx].append(
            stddev_score
        )  # Append the standard deviation of the scores

    bickeree_output = np.array(
        bickeree_output, dtype="object"
    )  # Convert the output list to a NumPy array
    output = pd.DataFrame(
        bickeree_output
    )  # Convert the NumPy array to a pandas DataFrame
    output.columns = [
        "Bickeree Number",
        "Avg. Score",
        "Avg. Normalized Score",
        "All Scores",
        "Min Score",
        "Max Score",
        "Scores Std. Dev.",
    ]  # Set the column names of the DataFrame
    output.set_index(
        "Bickeree Number", inplace=True
    )  # Set the 'Bickeree Number' column as the index of the DataFrame
    output.to_csv("bicker_output.csv")  # Write the DataFrame to a CSV file


if __name__ == "__main__":
    main()
