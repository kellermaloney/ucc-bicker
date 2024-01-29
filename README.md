<h1 align="left">ucc-bicker</h1>

<p>
  <a href="https://github.com/kellermaloney/ucc-bicker/blob/main/LICENSE" target="_blank">
    <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-black.svg" />
  </a>
  <br/>
  <a href="https://github.com/kellermaloney" target="_blank">
    <img alt="Github" src="https://img.shields.io/badge/GitHub-@kellermaloney-facf22.svg" />
  </a>
  <a href="https://www.linkedin.com/in/keller-maloney-130856187/" target="_blank">
    <img alt="LinkedIn" src="https://img.shields.io/badge/LinkedIn-@keller--maloney-facf22.svg" />
  </a>
  <br/>
  <a href="https://github.com/scornz" target="_blank">
    <img alt="Github" src="https://img.shields.io/badge/GitHub-@scornz-9C2C42.svg" />
  </a>
  <a href="https://linkedin.com/in/mscornavacca" target="_blank">
    <img alt="LinkedIn" src="https://img.shields.io/badge/LinkedIn-@mscornavacca-9C2C42.svg" />
  </a>
</p>

> A simple, quick Python script to facilitate the normalization of bicker scores for University Cottage Club (UCC) at Princeton University used in S'23 and S'24.

## Overview

The `bicker.py` script is designed to process and normalize scores from bicker. It takes input from a CSV file containing member emails and their scores for each bickeree and produces a CSV file with detailed statistics for each bickeree to be used during discussions. The process is as follows:

1. Members submit forms with their bicker scores after each day of bicker.
2. On the last day of bicker, process the data into the format required by this script.
3. Run the script. Each row of the output represents a bickeree. Included info is their raw score, normalized score, highest score, lowest score, the member that assigned that score, and a list of every member that bickered them. This format is to be used during discussions.
4. Calculate the final score by averaging (after normalizing) the bicker score (range = 1-5) and the discussion score (range = -1, 0, 1). Traditionally, a weight of 2/3 has been applied to the bicker score and 1/3 to the discussion score.

## Requirements

- Python 3.12 ([download](https://www.python.org/downloads/))
- `pipenv` (call `pip install pipenv` globally)
- VSCode (note: select the Python interpreter used by `pipenv` so syntax highlighting is correct)

## How to Run

1. Ensure requirements are install correctly.
2. Navigate to project folder and call `pipenv install`, then `pipenv shell` to enter the virtual environment.
3. Place the input CSV file in the same directory as the `bicker.py` script.
4. Run the script using the command `python bicker.py`.
5. The output CSV file `bicker_output.csv` will be generated in the same directory.
6. Try running it with the 'mock_bicker_responses.csv' to get a mock output!

## For Bicker Chairs

This program adjusts the mean of every member's scores to 3 by adding or subtracting the same amount to each of their scores. This process of "normalizing" scores has pros and cons. Here are a few things to consider:

**Pros:**

1. Prevents intentional "sandbagging" by blocs within the club.
   - Without normalization, members of a male affiliation would benefit by, for example, giving low scores to all the male members whom they bicker. This lowers the overall male average and improves the chance that his affiliate is accepted. In the past few years, this problem has gone all but extinct. This program outputs the members with the highest average scores and the lowest average scores so that malicious intent can be exposed to the club.
2. Reduces score "inflation."
   - Some members tend to give only 4s and 5s for the sake of kindness. This reduces the impact of such members.
3. Compels members to give a wider range of scores.
   - By telling the membership that their scores will be normalized, many attempt to give a wider variation in scores.
4. Reduces bias while maintaining the original spacing between scores.

**Cons:**

1. Potentially punishes the good performance of some bickerees.
   - Each year, the average score for all bickerees is always above a 3.0. This means that when normalization is applied, scores decrease. If a member happens to have a lot of great conversations, then all of that member's scores will be decreased, and that member's bickerees will be penalized unfairly.
2. Gives undue voting power to members who had few bicker conversations.
   - Below a certain sample size (NORMALIZATION_MINIMUM in the code) of bicker conversations, normalization is not a good idea. Therefore, members who had single-digit conversations during bicker will not have their scores normalized. This might give them disproportionate voting power.
3. Gives undue voting power to members who have a wide variation in their scores.
4. Reduces the average mean score.
   - This has a psychological effect on the membership during discussions. The club will be less excited about a bickeree with a low normalized score despite a high relative score.

NOTE: FEEL FREE TO ADJUST THE PROCESS OF NORMALIZATION TO SUIT YOUR NEEDS, OR IGNORE THAT COLUMN ALL TOGETHER!

## Input Format

The input CSV file should have the following columns:

- Email Address of member
- Bickeree Number
- Score
- Gender

## Output Format

The output CSV file will have the following columns:

- Bickeree Number
- Average Raw Score
- Average Normalized Score
- All Scores (and the member who gave the score)
- Lowest Score/Member Name
- Highest Score/Member Name
- Scores Standard Deviation

The program also outputs the average male and female scores, the 5 lowest and highest scoring members.

## Notes

- The normalization process is only applied if a member has completed a minimum number of bicker conversations, as defined by `NORMALIZATION_MINIMUM`.
- Scores for non-binary individuals are not normalized in the current version of the script.
