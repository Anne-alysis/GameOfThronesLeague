"""

In honor of the final season of Game of Thrones, we put together a fantasy league! Each participant fills out a
form we developed, and the code to algorithmically score the results is in this repo. Example questions include:

- Whether a character lives or dies
- Who rides a dragon
- Who ends up on the Iron Throne (if it still exists)

See README.md for more details.


"""

import sys

import pandas as pd

from score_helpers import score_plotting as sp, score_methods as sm
from score_io import score_input_handling as si, score_output_handling as so

create_answer_flag = False


def main():
    # set file names for in and out
    dirpath = "./external-files"
    responses_file = f"{dirpath}/Fantasy Game of Thrones Responses.csv"
    answer_file = f"{dirpath}/answer_truth.xlsx"
    results_file = f"{dirpath}/Results.csv"
    pdf_results_file = f"{dirpath}/Results.pdf"

    print("This is the name of the script: ", sys.argv[0])
    print("Number of arguments: ", len(sys.argv))
    print("The arguments are: ", str(sys.argv))

    week: int = 1 if len(sys.argv) == 1 else int(sys.argv[1])

    print(f"This is episode: {week}")

    print("Reading in responses ...")
    response_df: pd.DataFrame = si.read_data(responses_file)

    # produce aggregate statistical plots
    if week == 1:
        sp.generate_plots(response_df, pdf_results_file)

    # write answers to csv, for forming correct answer sheet
    if create_answer_flag:
        si.create_answer_csv(response_df)

    # read in correct answer key
    answer_df: pd.DataFrame = pd.read_excel(answer_file)

    print("Scoring results against correct answers ...")
    summed_df: pd.DataFrame = sm.score_results(response_df, answer_df, week)

    print("Combining previous weeks' results ... (if applicable)")
    combined_weeks_df = so.combine_weeks(summed_df, week, results_file)

    print("Writing output file")
    so.write_scores(combined_weeks_df, week, results_file)

    print("Done!")


if __name__ == "__main__":
    main()
