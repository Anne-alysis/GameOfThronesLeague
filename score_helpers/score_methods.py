"""

This module scores the results and returns the score and rank for a given week for
any questions for which a correct answer can be rendered ("include").

"""

import pandas as pd
import string


def score_results(response_df: pd.DataFrame, answer_df: pd.DataFrame, week: int) -> pd.DataFrame:
    """
    This reads in the cleaned responses and scores them, if they should be included in scoring "include".

    :param response_df: cleaned responses df
    :param answer_df: source of truth for correct answers
    :param week: episode number
    :return: teams with scores and ranks for the given week
    """

    # join responses to correct answers
    merged_df: pd.DataFrame = pd.merge(response_df, answer_df.drop(columns="points"), "left", "question")

    # convert some columns to boolean
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


def score_exact(df: pd.DataFrame) -> pd.DataFrame:
    """
    Score questions that should be matched exactly.

    :param df: previously filtered df only exact match questions
    :return: df with score

    """

    filter_df: pd.DataFrame = df[df.include] \
        .assign(correct=lambda x: x.answer == x.answer_truth,
                score=lambda x: x.correct * x.points)

    return filter_df


def score_multiple(df: pd.DataFrame) -> pd.DataFrame:
    """
    Score questions that are not matched exactly (multiple correct answers possible).
    A string with a comma separated list of correct answers is what is being
    compared to.

    :param df: previously filtered df for non-exact match questions
    :return: df with score
    """

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
    """
    Takes in the scored data frame and groups by team, etc, ranks each player,
    and renames columns for better aesthetics when shared to participants in a Google doc.

    :param df: scored df
    :param week: episode number
    :return: final rankings and scores
    """

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
