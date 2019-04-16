# GameOfThronesLeague

# Introduction

In honor of the final season of Game of Thrones, we put together a fantasy league!  Each participant fills
out a form we developed, and the code to algorithmically score the results is in this repo.  Example questions
include:
 
 * Whether a character lives or dies
 * Who rides a dragon
 * Who ends up on the Iron Throne (if it still exists)

# General Code Structure

This code will be run weekly and scores recalculated based on new information in each week's episode.  Week by 
week the correct answers will be updated, and responses re-evaluated against changing information (e.g., 
a character dies).

1) The code reads in the responses from a downloaded CSV (`./external-files/Fantasy Game of Thrones Responses.csv')
2) Responses are reshaped to allow for ease of scoring
3) Answers from a Excel sheet are read in (`./external-files/answer_truth.xlsx`)
4) Aggregate responses are plotted to pdf (if week 1 only, `./external-files/Results.pdf`)
5) Scores are computed 
6) Scores are written to a CSV (`./external-files/Results.csv`), including the previous weeks' scores/ranks/rank movement, if applicable.  

Note, the algorithm was tested with a mock answer sheet as well (`./external-files/answer_testing.xlsx`)

# Running the code

Each week an argument is read in to indicate the value of the week (e.g., 1 - 6). 

`> python score.py ${week_value}`

# Modules
## `score.py`

This is the main module which includes all steps outlined above.  

## `score_io` package
### `score_input_handling.py`

This module handles all the input operations, such as:
 * Reading in responses and reshaping that data
 * Creating the structure of the answer sheet
 
 ### `score_output_handling.py`

This module handles all the output operations, such as:
* Combining previous weeks' results (if `week > 1`)
 * Writing out the results
 
 ## `score_helpers` package
### `score_methods.py`
This module includes the methods for scoring.  Most are exact match algorithms, but
some questions have multiple possible answers.  These are handled separately.  Grouping the final
results by team also happen in this module.  

### `score_plotting.py`

This takes in each question, aggregates the distinct responses, and plots each question to a pdf.  All 
individual plots are combined into a single pdf.



