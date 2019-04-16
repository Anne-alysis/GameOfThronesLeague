"""

This handles output of the project.  This combines results from previous weeks
 and writes the results to a file (appended if > week 1).

"""

import datetime
import os

import pandas as pd


def combine_weeks(df: pd.DataFrame, week: int, results_file: str) -> pd.DataFrame:
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

        return combined_results[rearranged_names]
    else:
        return df


def write_scores(df: pd.DataFrame, week: int, results_file: str) -> None:
    """
    This takes in the scores and writes them to a file.  This will append to previous
    results if they exist (week > 1).

    :param df: final scores
    :param week: episode week
    :param results_file: file name
    :return: None
    """

    if week == 1:
        # check if old version of results exists
        exists = os.path.isfile(results_file)
        if exists:
            os.system(f"rm {results_file}")

    df.to_csv(results_file, index=False)

    return None





