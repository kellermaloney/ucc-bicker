from analyze import (
    calculate_ranks_and_percentiles,
    calculate_scores,
    grab_lowest_and_highest_scores,
)
from cleanup import replace_emails

from data import load_input
from data.validate import check_all_input
from utils import clr, cprint

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

    output, members_info = calculate_scores(scores, bickerees)
    # Add the lowest/highest scoring members
    output = grab_lowest_and_highest_scores(scores, output)
    # Append the rank and percentile columns
    output = calculate_ranks_and_percentiles(output)
    # Replace the emails with the member's name
    output = replace_emails(members, output)

    output.set_index("bickeree_number", inplace=True)
    output.to_csv("bicker_output.csv")

    members_info.set_index("member_email", inplace=True)
    members_info.to_csv("bicker_members_info.csv")


if __name__ == "__main__":
    main()
