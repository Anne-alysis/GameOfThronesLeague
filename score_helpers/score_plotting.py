"""

This module plots all aggregate data by question, so one can
see the split of unique answers.

"""

import math
import string

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages


def generate_plots(df: pd.DataFrame, pdf_results_file: str):
    """
    This will generate pie plots for the responses.
    :param df: raw cleaned responses
    :param pdf_results_file: path for output pdf
    :return: None
    """

    # reshape free form questions
    reshaped_df = reshape_data_for_plots(df)

    # find unique questions to plot
    questions = list(reshaped_df["question"].drop_duplicates())

    with PdfPages(pdf_results_file) as pdf:
        [plot_function(reshaped_df, i, pdf) for i in questions]

    return None


def plot_function(df: pd.DataFrame, question: str, pdf):
    """
    Function to plot the split of a single question in a pie chart.

    :param df: aggregate df
    :param question: question to use to filter aggregate data
    :param pdf: place to save data
    :return: None
    """

    plt.clf()
    # filter data for a single question per plot
    df_plot = df[df.question == question]

    fig1, ax1 = plt.subplots()
    ax1.pie(df_plot.perc,
            labels=df_plot.answer_mod,
            autopct='%1.1f%%',
            shadow=True,
            startangle=90)
    ax1.axis('equal')

    # for questions that are super long, change the font and split the text
    font_size, question = munge_title(question)

    fig1.suptitle(question, fontsize=font_size)
    pdf.savefig()
    plt.close()
    return None


def reshape_data_for_plots(df: pd.DataFrame) -> pd.DataFrame:
    """
    Data needs to be aggregated by unique response to calculate the percentage
    of people who choose each response.  Some questions are free form and need
    to have their responses as standardized as possible...
    :param df: raw cleaned data frame
    :return: aggregated data frame, even cleaner!
    """

    # lower strings and remove punctuation for write-in questions
    df['answer_mod'] = df['answer']
    for i in range(df.shape[0]):
        if "26" in df.loc[i, "question"] or "27" in df.loc[i, "question"]:
            df.at[i, 'answer_mod'] = df.loc[i, "answer"].lower().translate(str.maketrans('', '', string.punctuation))

    pick_out_cols = ["question", "answer_mod"]

    # aggregate unique responses
    agg_df = df[pick_out_cols].groupby(pick_out_cols, as_index=False).size().reset_index(name='counts')

    # aggregate responses
    agg_total_df = df[["question"]].groupby(["question"], as_index=False).size().reset_index(name='total')

    # join so can calculate percentages of unique answers
    agg_combined_df = pd.merge(agg_df, agg_total_df, "left", "question") \
        .assign(perc=lambda x: x.counts / x.total * 100.0)

    return agg_combined_df


def munge_title(question: str):
    """
    Set font size based on length of question, add newline in long questions to break it up

    :param question: input question for plot
    :return: font size as int and reformed question string
    """

    n = len(question)
    font_size = 16 if n < 20 else 13

    # for long question titles, split up with newline "\n"
    if n > 35:
        middle = math.floor(n / 2)
        while question[middle] != " " and middle < (n - 1):
            middle += 1

        if middle < (n - 1):
            question = question[:middle] + "\n" + question[middle:]

    return font_size, question


def remove_punctuations(text):
    """
    Remove punctutation from write-in answers

    :param text: free form answer
    :return: cleaned answered
    """

    for punctuation in string.punctuation:
        text = text.replace(punctuation, '')
    return text
