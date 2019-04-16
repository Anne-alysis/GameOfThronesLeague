"""

This handles the input and output of the project.  This reads in the raw responses, reshapes them,
creates the structure of the answer sheet, and writes the results to a file.

"""

import datetime
import os

import numpy as np
import pandas as pd


def read_data(responses_file: str) -> pd.DataFrame:
    """
    This reads in the raw responses downloaded from Google forms and returns a reshaped data frame


    :param responses_file:  location of the file
    :return: reshaped dataframe
    """

    # reads in raw responses
    data_df: pd.DataFrame = pd.read_csv(responses_file).drop(columns=["Timestamp"])

    # change column names to something more managable
    col_names = data_df.columns

    # append numbers to questions
    enumerated_col_names = ['{:02d}'.format(i) + ". " + j for i, j in enumerate(col_names[4:], 1)]

    # rename columns
    col_names_new = ['name', 'team', 'pay_type', 'split_type'] + enumerated_col_names

    data_df.columns = col_names_new
    grouping_names = ["team", "pay_type"]
    dropped_names = ['name', 'split_type']

    data_melt_df: pd.DataFrame = pd.melt(data_df.drop(columns=dropped_names),
                                         id_vars=grouping_names,
                                         var_name="question_full",
                                         value_name="answer")

    data_melt_munged_df = data_melt_df.assign(
        question_full=lambda x: x.question_full.str.strip(),
        boolean_question=lambda x: x.question_full.str.contains("\\["),
        boolean_person=lambda x: np.where(x.boolean_question, " [" + x.question_full.str.split("[").str[1], ""),
        question=lambda x: x.question_full.str.split("(").str[0].str.strip() + x.boolean_person,
        points=lambda x: pd.to_numeric(x.question_full.str.split("(").str[1].str.strip().str.split(" ").str[0])
    )

    columns = grouping_names + ["question", "points", "answer"]

    almost_final_df = split_hybrid_question(data_melt_munged_df[columns])

    return almost_final_df


def split_hybrid_question(df: pd.DataFrame) -> pd.DataFrame:
    """
    helper function for reading in the data to split question 27 into separate questions
    for ease of scoring

    :param df: cleaned responses data frame
    :return:  data frame that has the hybrid question split into two rows for each response

    """

    df_hold = df[df.question != "27. Which TWO supporting characters kill which TWO supporting characters?"]
    df_support = df[df.question == "27. Which TWO supporting characters kill which TWO supporting characters?"] \
        .assign(answer1=lambda x: x.answer.str.split(".").str[0].str.strip(),
                answer2=lambda x: x.answer.str.split(".").str[1].str.strip()) \
        .drop(columns="answer")

    col_names = ["team", "pay_type", "question", "points"]

    df_concat = pd.concat([df_hold[col_names + ["answer"]],
                           df_support[col_names + ["answer1"]].rename(columns={'answer1': 'answer'}),
                           df_support[col_names + ["answer2"]].rename(columns={'answer2': 'answer'})],
                          ignore_index=True)
    return df_concat


def create_answer_csv(df: pd.DataFrame):
    """
    This writes out the structure of the answers, which is taken directly from the responses of the Google form.

    :param df: this is the cleaned responses data frame
    :return: None
    """

    # creates answer sheet from form
    df.groupby("team")["points"].sum()

    answer_early_df: pd.DataFrame = df[["question", "points"]].drop_duplicates()

    answer_early_df.to_csv("answer_structure.csv", index=False)

    return None


def combine_weeks_and_write_scores(df: pd.DataFrame, week: int, results_file: str) -> None:
    """
    This takes in the scores and writes them to a file.  This will append to previous
    results if they exist (week > 1).

    :param df: final scores
    :param week: episode week
    :param results_file: file name
    :return: None
    """

    now = datetime.datetime.now()
    today_date = now.strftime("%Y-%m-%d")

    if week > 1:
        # read in old results to append to
        old_results = pd.read_csv(results_file)  # read in old results
        results_file_split = results_file.split(".")
        old_results.to_csv(f"./archive/{results_file_split[0]}_{today_date}.csv")  # copy for posterity

        # drop movement column from old results, if exists
        mvmt_name = "Movement from Previous Episode"
        if mvmt_name in old_results.columns:
            old_results.drop(columns=mvmt_name, inplace=True)

        combined_results = pd.merge(df, old_results, "left", \
                                    ["Team", "Iron Bank"]).sort_values(f"Episode {week} Rank")
        combined_results[mvmt_name] = combined_results[f"Episode {week} Rank"] - \
                                      combined_results[f"Episode {week - 1} Rank"]

        col_names = list(combined_results.columns)
        rearranged_names = col_names[:3] + col_names[-1:] + col_names[3:(len(col_names) - 1)]

        combined_results[rearranged_names].to_csv(results_file, index=False)
    else:
        # check if old version of results exists
        exists = os.path.isfile(results_file)
        if exists:
            os.system(f"rm {results_file}")

        df.to_csv(results_file, index=False)

    return None



