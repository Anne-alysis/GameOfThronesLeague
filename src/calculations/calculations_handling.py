import pandas as pd
import string


class Calculations:
    def __init__(self):
        pass

    @staticmethod
    def apply(response_df: pd.DataFrame, answers_df: pd.DataFrame, week: int) -> pd.DataFrame:

        merged_df = pd.merge(response_df, answers_df, how="left", on="question_number") \
            .assign(
            correct=lambda x: Calculations._check_correct(x.include, x.multiple_answers, x.answer, x.correct_answer),
            score=lambda x: x.correct_answer * x.points
        )

        return Calculations._aggregate_results(merged_df, week)

    @staticmethod
    def _check_correct(include: bool, multiple_answers: bool, answer: str, correct_answer: str) -> bool:
        if ~include:
            return False

        if multiple_answers:
            munged_answer = Calculations._munge_answers(answer)
            munged_correct_answer = Calculations._munge_answers(correct_answer)
            return munged_answer in munged_correct_answer

        else:
            return answer == correct_answer

    @staticmethod
    def _munge_answers(s: str) -> str:
        return s.translate(str.maketrans('', '', string.punctuation))

    @staticmethod
    def _aggregate_results(df: pd.DataFrame, week: int) -> pd.DataFrame:
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
