import pandas as pd


class Responses:
    def __init__(self):
        pass

    @staticmethod
    def apply(df: pd.DataFrame, file_name: str) -> pd.DataFrame:
        renamed_df = Responses._rename_columns(df)
        melted_df = pd.melt(renamed_df.drop(columns=["name", "split_type"]),
                            ["team", "pay_type"],
                            var_name="question_number",
                            value_name="answer")

        final_df = Responses._split_hybrid_question(melted_df)

        final_df.to_csv(file_name, index=False)

        return final_df

    @staticmethod
    def _rename_columns(df: pd.DataFrame) -> pd.DataFrame:
        question_number_range = list(range(0, df.shape[1] - 4))

        numbered_question_names = ["Q" + '{:02d}'.format(i) for i in question_number_range]

        question_names = ["name", "team", "pay_type", "split_type"] + numbered_question_names

        df.columns = question_names

        return df

    @staticmethod
    def _split_hybrid_question(df: pd.DataFrame) -> pd.DataFrame:
        """
        Helper function for reading in the data to split question 27 into separate questions
        for ease of scoring.  This question has two write-in answers, and this splits into
        2 rows from 1 row.

        :param df: cleaned responses data frame
        :return:  data frame that has the hybrid question split into two rows for each response

        """

        # keep questions that don't need alteration
        df_hold = df[df.question_number != "Q26"]

        # filter out question that needs attention
        df_support = df[
            df.question_number == "Q26"] \
            .assign(answer1=lambda x: x.answer.str.split(".").str[0].str.strip(),
                    answer2=lambda x: x.answer.str.split(".").str[1].str.strip()) \
            .drop(columns="answer")

        col_names = ["team", "pay_type", "question_number"]

        # recombine data
        df_concat = pd.concat([df_hold[col_names + ["answer"]],
                               df_support[col_names + ["answer1"]].rename(columns={'answer1': 'answer'}),
                               df_support[col_names + ["answer2"]].rename(columns={'answer2': 'answer'})],
                              ignore_index=True)
        return df_concat
