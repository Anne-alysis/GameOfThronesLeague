import sys

import pandas as pd

import plot_results as pr
import score_io as sio
import score_methods as sm

create_answer_flag = False


def main():

    # set file names for in and out
    dirpath = "./external-files"
    responses_file = f"{dirpath}/Fantasy Game of Thrones Responses.csv"
    answer_file =  f"{dirpath}/answer_truth.xlsx"
    results_file =  f"{dirpath}/Results.csv"
    pdf_results_file =  f"{dirpath}/Results.pdf"

    print("This is the name of the script: ", sys.argv[0])
    print("Number of arguments: ", len(sys.argv))
    print("The arguments are: ", str(sys.argv))

    week: int = 1 if len(sys.argv) == 1 else int(sys.argv[1])

    print(f"This is episode: {week}")

    # read in responses
    print("Reading in responses ...")
    response_df: pd.DataFrame = sio.read_data(responses_file)

    # produce aggregate statistical plots
    if week == 1:
        pr.generate_plots(response_df, pdf_results_file)

    # write answers to csv, for forming correct answer sheet
    if create_answer_flag:
        sio.create_answer_csv(response_df, True)

    # read in correct answer key
    answer_df: pd.DataFrame = pd.read_excel(answer_file)

    # score the results against the answer key
    print("Scoring results ...")
    summed_df: pd.DataFrame = sm.score_results(response_df, answer_df, week, pdf_results_file)

    print("Writing results ...")
    sio.combine_weeks_and_write_scores(summed_df, week, results_file)

    print("Done!")


if __name__ == "__main__":
    main()
