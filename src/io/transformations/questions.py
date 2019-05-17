import pandas as pd

"""
This class wrangles the questions from their somewhat messy format into a more standard format, 
with question numbers and points extracted.  Writes structure of questions to file.  
"""


class Questions:
    def __init__(self):
        pass

    @staticmethod
    def apply(df: pd.DataFrame, output_file: str) -> None:
        question_stripped_df = Questions._get_questions_from_raw_responses(df)

        question_with_pts_df = Questions._get_points(question_stripped_df)

        arranged_col_names = ["question_number", "question_full", "question", "points"]
        question_df = Questions._rearrange_character_name(question_with_pts_df, arranged_col_names)

        question_df.to_csv(output_file, index=False)

        return

    @staticmethod
    def _get_questions_from_raw_responses(df: pd.DataFrame) -> pd.DataFrame:
        col_names = df.columns[4:]
        question_df = pd.DataFrame(list(enumerate(col_names)), columns=["id", "question_full"]) \
            .assign(
            question_fragment=lambda x: x.question_full.str.split("(").str[0],
            contains_character=lambda x: x.question_full.str.contains("\\[")
        )
        question_df['question_number'] = question_df.id.apply(lambda x: 'Q{0:0>2}'.format(x))
        return question_df.drop(columns="id")

    @staticmethod
    def _get_points(df: pd.DataFrame) -> pd.DataFrame:
        """
        Extracts the point values from df.
        :param df:
        :return:
        """
        temp_df = df.assign(
            tmp=lambda x: x.question_full.str.split("(").str[1],
            points_string=lambda x: x.tmp.str.split(" ").str[0]
        )
        temp_df['points'] = temp_df.points_string.fillna("0").astype(int)

        return temp_df.drop(columns=["points_string", "tmp"])

    @staticmethod
    def _rearrange_character_name(df: pd.DataFrame, arranged_col_names: list) -> pd.DataFrame:
        non_character_df = df[~df.contains_character] \
            .rename(columns={"question_fragment": "question"}, inplace=False)[arranged_col_names]

        character_df = df[df.contains_character] \
            .drop(columns="contains_character") \
            .assign(character=lambda x: "[" + x.question_full.str.split("[").str[1],
                    question=lambda x: f"{x.question_fragment} {x.character}")

        return pd.concat((non_character_df, character_df[arranged_col_names])) \
            .sort_values("question_number")
