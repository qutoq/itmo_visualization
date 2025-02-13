import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from wordcloud import WordCloud


def validate_data(df: pd.DataFrame, chart_type: str) -> bool:
    """
    Проверяет корректность данных перед построением графика.
    """
    if df is None or df.empty:
        return False

    if chart_type in {'line', 'scatter', 'hist'} and df.shape[1] < 2:
        return False

    return True


def generate_plot(df: pd.DataFrame, title: str, chart_type: str, output_dir: str, operation_id: str) -> int:
    """
    Генерирует и сохраняет график по данным из DataFrame.

    :param df: pandas DataFrame с данными
    :param title: Название графика
    :param chart_type: Тип диаграммы ('line', 'pie', 'hist', 'cascade', 'scatter', 'wordcloud')
    :param output_dir: Директория для сохранения
    :param operation_id: id операции
    :return: 0 при успешном выполнении
    :return: 1 при неправильно указанном типе
    :return: 2 при неккоректных данных
    """
    if chart_type not in {'line', 'pie', 'hist', 'cascade', 'scatter', 'wordcloud'}:
        return 1

    if not validate_data(df, chart_type):
        return 2

    os.makedirs(output_dir, exist_ok=True)

    filename = os.path.join(output_dir, f"график_{chart_type}_{operation_id}.png")

    figsize = (12, 8) if chart_type != 'pie' else (8, 8)
    plt.figure(figsize=figsize)
    sns.set_style("darkgrid")

    if chart_type == 'line':
        sns.lineplot(x=df.iloc[:, 0], y=df.iloc[:, 1])
        plt.xlabel(df.columns[0])
        plt.ylabel(df.columns[1])
        plt.title(title)

    elif chart_type == 'pie':
        labels = df.iloc[:, 1] if df.shape[1] > 1 else None
        plt.pie(df.iloc[:, 0], labels=labels, autopct='%1.1f%%')
        plt.title(title)

    elif chart_type == 'hist':
        sns.histplot(df.iloc[:, 1], bins=20, kde=True)
        plt.xlabel(df.columns[1])
        plt.ylabel("Частота")
        plt.title(title)

    elif chart_type == 'cascade':
        x = np.arange(len(df.iloc[:, 0]))
        y = df.iloc[:, 0].cumsum()
        plt.bar(x, y)
        plt.xlabel(df.columns[0])
        plt.ylabel("Накопленное значение")
        plt.title(title)

    elif chart_type == 'scatter':
        sns.scatterplot(x=df.iloc[:, 0], y=df.iloc[:, 1])
        plt.xlabel(df.columns[0])
        plt.ylabel(df.columns[1])
        plt.title(title)

    elif chart_type == 'wordcloud':
        text = ' '.join(df.iloc[:, 0].astype(str))
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.title(title)

    plt.savefig(filename, bbox_inches='tight')
    plt.close()

    return 0