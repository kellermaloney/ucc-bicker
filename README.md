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
2. Navigate to project folder and call `pipenv install`.
3. Place the necessary CSV files (members, bickerees, and scores) in the project folder.
4. Run the script with `pipenv run bicker <scores-filename> <members-filename> <bickerees-filename>`. Alternatively, use `pipenv run mock` to run with the provided mock data.

## Explanation

### Spring '24 (current)

#### Steps

1. Calculate club average distribution for scores given, that is, what percentage of all scores given were ones, twos, etc. for the entire club.
2. Take each individual member's score distribution (that is, what percentage of a particular member's scores given were ones, twos, etc.) and get the difference from the club average. Sum these differences for each score category (one, two, three) to produce an unfairness score. The closer this unfairness score is to 0, the more "fair" the member's scores are, as they relate closer to the club's average distribution.
   Let $F_i$ represent the unfairness score for member $i$, let $P_{ij}$ represent the percentage of score $j$ given out by member $i$, and $A_j$ be the average percentage of score $j$ across the entire club.

$$U_i = \sum_{j=1}^{n} |P_{ij} - A_j|$$

3. Given these unfairness scores, attribute a weight to each member where less weight is assigned to members who have higher unfairness scores, and more weight assigned to members who have a lower unfairness score. This weight for member $i$, $W_i$, is determined by a function based on last year's distribution of scores, $f(x)$.

$$W_i = f(U_i)$$

4. We take the weighted members, and compute a weighted sum for each bickeree, where $S_{ik}$ is the raw score from 1-5 given by member $i$ to bickeree $k$ and $W_i$ is that member's weight determined by their unfairness score.

$$T_k = \frac{\sum_{i=1}^{m} (S_{ik} \times W_i)}{\sum_{i=1}^{m} W_i}$$

5. These scores and averages are typically seperated by gender in order to account for natural discrepancies in normal voting practices.

#### Example

From a glance, the above steps can appear a bit complicated, but it's actually a lot simpler with an example. Let's say that the score distribution across the club is as follows:

<div align="center">

|  1  | 2   | 3   | 4   | 5   |
| :-: | --- | --- | --- | --- |
| 10% | 15% | 30% | 35% | 10% |

</div>

This means that out of ALL scores given out by members of the club, 10% of them were ones, 15% twos, 30% threes, 35% fours, and 10% fives. Now, let's consider these (purely hypothetical) members that have given out a bunch of scores during bicker:

<div align="center">

| Member | 1   | 2   | 3   | 4   | 5   |
| :----: | --- | --- | --- | --- | --- |
| Caleb  | 15% | 10% | 35% | 15% | 20% |
| Stevie | 0%  | 0%  | 10% | 30% | 60% |
|   MC   | 70% | 10% | 0%  | 0%  | 20% |
| Carrie | 30% | 25% | 30% | 10% | 5%  |
| Hunter | 0%  | 20% | 15% | 35% | 30% |

</div>

So we can see that Caleb, Carrie, and Hunter are relatively fair voters (with a spread distribution), while Stevie skews heavily towards 3+ ratings and MC skews heavily towards 2- ratings. Let's calculate their unfairness scores, by taking the absolute difference between each member's score distributions and the club's average.

<div align="center">

| Member | 1    | 2    | 3    | 4    | 5    | Unfairness |
| :----: | ---- | ---- | ---- | ---- | ---- | ---------- |
| Caleb  | 0.05 | 0.05 | 0.05 | 0.2  | 0.1  | 0.45       |
| Stevie | 0.10 | 0.15 | 0.2  | 0.05 | 0.5  | 1.00       |
|   MC   | 0.6  | 0.05 | 0.3  | 0.35 | 0.1  | 1.40       |
| Carrie | 0.2  | 0.1  | 0    | 0.25 | 0.05 | 0.60       |
| Hunter | 0.1  | 0.05 | 0.15 | 0    | 0.2  | 0.50       |

</div>

As we can see, Stevie and MC have 1.00+ unfairness scores, while the other three members hover around ~0.5. We then take this score, and according to a function from last year's data, convert that into the member's "weight". That is, when calculating a bickeree's scores, how "much" does this member's score matter in the bickeree's final score. Here are the calculated weights based on the listed unfairness scores:

<div align="center">

| Member | Unfairness | Weight |
| :----: | ---------- | ------ |
| Caleb  | 0.45       | 1.0    |
| Stevie | 1.00       | 0.6    |
|   MC   | 1.40       | 0.4    |
| Carrie | 0.60       | 0.95   |
| Hunter | 0.50       | 1.0    |

</div>

To demonstrate how this works, let's consider some example bickerees:

<div align="center">

| Member | Bickeree 1 | Bickeree 2 | Bickeree 3 |
| :----: | ---------- | ---------- | ---------- |
| Caleb  | 5          | N/A        | 4          |
| Stevie | N/A        | 5          | 5          |
|   MC   | 1          | 5          | 1          |
| Carrie | N/A        | N/A        | 3          |
| Hunter | N/A        | N/A        | 3          |

</div>

For bickeree 1, we see that MC gave a score of a 1, and Caleb gave a score of a 5. The score is calculated as a weighted average, as follows:

$$\frac{5(1.0) + 1(0.4)}{1.0 + 0.4} \approx 3.857$$

We see that since Caleb has a higher weight (due to his fair score distribution) his 5 means more than MC's 1, thus the final bickeree's score tends towards a 5.

For bickeree 2, we see that both MC and Stevie gave a score of 5. In a weighted sum this would work out as $\frac{5(0.6) + 5(0.4)}{0.6 + 0.4} = 5$. This example is important to demonstrate that despite Stevie and MC having high unfairness values (and thus lower weights), the "value" of their fives does not actually change. Thus, receiving high scores from a notoriously low-score giver will not boost the value of a 5, and vice-versa for high-score givers.

For bickeree 3, this is a normal score distribution, and we can see that despite receiving a high grade from Stevie, and a low grade from MC, the weighted average falls onto the members with higher weight, and ends up being $\approx 3.3$.

### Spring '23 (deprecated)

TO DO.

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
