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

import src.calculations.calculations_handling as calc
import src.io.input_handling as ih
import src.io.output_handling as oh
import src.plotting.score_plotting as sp

# set file names for in and out
dirpath = "XX"
dirpath_testing = f"{dirpath}/testing"
raw_responses_file = f"{dirpath}/Fantasy Game of Thrones Responses.csv"
answer_file = f"{dirpath_testing}/correct_answers.xlsx"
results_file = f"{dirpath_testing}/Results.csv"
pdf_results_file = f"{dirpath_testing}/Results.pdf"

reshaped_response_file = f"{dirpath_testing}/munged_responses.csv"
answer_structure_file = f"{dirpath_testing}/answer_structure.csv"


def main():

    print("This is the name of the script: ", sys.argv[0])
    print("Number of arguments: ", len(sys.argv))
    print("The arguments are: ", str(sys.argv))

    week: int = 1 if len(sys.argv) == 1 else int(sys.argv[1])

    print(f"This is episode: {week}")

    print("Reading in responses ...")

    response_df: pd.DataFrame = ih.InputHandling.apply(week,
                                                       raw_responses_file,
                                                       reshaped_response_file,
                                                       answer_structure_file)

    # produce aggregate statistical plots
    if week == 1:
        sp.generate_plots(response_df, pdf_results_file)

    # read in correct answer key
    answers_df: pd.DataFrame = pd.read_excel(answer_file)

    print("Scoring results against correct answers ...")
    scored_df: pd.DataFrame = calc.Calculations.apply(response_df, answers_df, week)

    print("Combining previous weeks' results ... (if applicable)")
    combined_weeks_df = oh.OutputHandling.combine_weeks(scored_df, week, results_file)

    print("Writing output file")
    oh.OutputHandling.write_scores(combined_weeks_df, week, results_file)

    print("Done!")


if __name__ == "__main__":
    main()
