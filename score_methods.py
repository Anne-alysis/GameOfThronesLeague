"""

This module scores the results and returns the score and rank for a given week.

"""

import pandas as pd
import string


def score_exact(df: pd.DataFrame) -> pd.DataFrame:
    # score questions with only one correct answer
    filter_df: pd.DataFrame = df[df.include] \
        .assign(correct=lambda x: x.answer == x.answer_truth,
                score=lambda x: x.correct * x.points)

    return filter_df


def score_multiple(df: pd.DataFrame) -> pd.DataFrame:
    # score questions with multiple correct answers
    filter_df: pd.DataFrame = df[df.include] \
        .assign(correct=False)

    for i in filter_df.index:

        answer = df.answer[i] \
            .lower() \
            .translate(str.maketrans('', '', string.punctuation))

        truth = filter_df.answer_truth[i] \
            .lower() \
            .translate(str.maketrans('', '', string.punctuation))

        if answer in truth:
            # filter_df.correct[i] = True # this doesn't do it correctly, with copying
            filter_df.at[i, 'correct'] = True

    filter_df["score"] = filter_df.correct * filter_df.points

    return filter_df


def aggregate_results(df: pd.DataFrame, week: int) -> pd.DataFrame:
    summed_df: pd.DataFrame = df \
        .groupby(["team", "pay_type"])["score"] \
        .sum().to_frame() \
        .sort_values("score", ascending=False) \
        .reset_index() \
        .assign(rank=lambda x: x.score.rank(ascending=False, method="max"))[['team', 'pay_type', 'rank', 'score']]

    summed_df.rename(columns={'score': f'Episode {week} Score',
                              'rank': f'Episode {week} Rank',
                              'team': 'Team',
                              'pay_type': 'Iron Bank'},
                     inplace=True)

    return summed_df


def score_results(response_df: pd.DataFrame, answer_df: pd.DataFrame, week: int) -> pd.DataFrame:
    merged_df: pd.DataFrame = pd.merge(response_df, answer_df.drop(columns="points"), "left", "question")

    # convert to boolean
    cols_to_bool = ["multiple_answers"]
    for i in ["include", cols_to_bool]:
        merged_df[i] = merged_df[i].astype(bool)

    # score exact
    exact_df = merged_df[~merged_df.multiple_answers].drop(columns=cols_to_bool)
    exact_scored_df = score_exact(exact_df)

    # score multiple possibilities
    multiple_df = merged_df[merged_df.multiple_answers].drop(columns=cols_to_bool)
    multiple_scored_df = score_multiple(multiple_df)

    # combine all scores
    combined_df = pd.concat([exact_scored_df, multiple_scored_df], ignore_index=True).drop(columns=["include"]) \
        .sort_values(["question", "team"])
    combined_df.to_csv("./archive/Results_unaggregated.csv")

    # aggregate raw scores
    summed_df = aggregate_results(combined_df, week)

    return summed_df
