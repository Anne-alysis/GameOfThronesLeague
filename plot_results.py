"""

This module plots all aggregate data by question, so one can
see the split of unique answers.

"""

import math
import string

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages


def remove_punctuations(text):
    for punctuation in string.punctuation:
        text = text.replace(punctuation, '')
    return text


def plot_function(df: pd.DataFrame, question: str, pdf):
    plt.clf()
    df_plot = df[df.question == question]

    fig1, ax1 = plt.subplots()
    ax1.pie(df_plot.perc,
            # explode=df_plot.explode,
            labels=df_plot.answer_mod,
            autopct='%1.1f%%',
            shadow=True,
            startangle=90)
    ax1.axis('equal')
    n = len(question)
    font_size = 16 if n < 20 else 13

    if n > 35:
        middle = math.floor(n / 2)
        while question[middle] != " " and middle < (n - 1):
            middle += 1

        if middle < (n - 1):
            question = question[:middle] + "\n" + question[middle:]

    fig1.suptitle(question, fontsize=font_size)
    pdf.savefig()
    plt.close()
    return None


def reshape_data_for_plots(df: pd.DataFrame) -> pd.DataFrame:
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
        .assign(perc=lambda x: x.counts / x.total * 100.0
                # correct=lambda x: x.answer == x.answer_truth
                )
    # agg_combined_df["explode"] = np.where(agg_combined_df.correct, 0.1, 0.0)

    return agg_combined_df


def generate_plots(df: pd.DataFrame, pdf_results_file: str):

    # reshape free form questions
    reshaped_df = reshape_data_for_plots(df)

    # find unique questions to plot
    questions = list(reshaped_df["question"].drop_duplicates())

    with PdfPages(pdf_results_file) as pdf:
        [plot_function(reshaped_df, i, pdf) for i in questions]

    return None
