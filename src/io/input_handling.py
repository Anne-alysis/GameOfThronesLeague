import pandas as pd
import src.io.transformations.questions as q
import src.io.transformations.responses as r

"""
This class handles all the input and question wrangling (and writing answer structure to file)
"""


class InputHandling:
    def __init__(self):
        pass

    @staticmethod
    def apply(week: int, raw_responses_file: str, reshaped_response_file: str,
              answer_structure_file: str) -> pd.DataFrame:

        if week > 1:
            return pd.read_csv(reshaped_response_file)

        # read in raw responses
        raw_response_df = pd.read_csv(raw_responses_file).drop(columns="Timestamp")

        # parse out the questions and write their structure to the file
        q.Questions.apply(raw_response_df, answer_structure_file)

        # clean up the responses
        response_df = r.Responses.apply(raw_response_df, reshaped_response_file)

        return response_df
