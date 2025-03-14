from celery import Celery
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import io

from src import texts
from src.errors import MyError

app = Celery("tasks")
app.config_from_object("config.celeryconfig")


def validate_data(df: pd.DataFrame, chart_type: str) -> bool:
    """
    Проверяет корректность данных перед построением графика.
    """
    if df is None or df.empty:
        return False

    if chart_type in {'line', 'scatter'} and df.shape[1] < 2:
        return False

    return True

@app.task
def generate_plot(df_json, chart_type: str):
    """
    Генерирует и сохраняет график по данным из DataFrame.
    :param df_json: pandas DataFrame с данными
    :param chart_type: Тип диаграммы ('line', 'pie', 'hist', 'cascade', 'scatter', 'wordcloud')
    :return: bytecode при успешном выполнении"""
    #:return: 'err' при неправильно указанном типе    """
    
    title = chart_type
    df = pd.read_json(df_json)

    if chart_type not in texts.choice_types:
        raise MyError(f"Недопустимый тип диаграммы {chart_type}. Доступные типы: {', '.join(texts.choice_types.keys())}.")

    if not validate_data(df, chart_type):
        raise MyError(f"Ошибка валидации данных для типа диаграммы {chart_type}. Убедитесь, что данные соответствуют формату для выбранного типа.")

    figsize = (12, 8) if chart_type != 'pie' else (8, 8)
    plt.figure(figsize=figsize)
    sns.set_style("whitegrid")

    if chart_type == 'line':
        sns.lineplot(x=df.iloc[:, 0], y=df.iloc[:, 1])
        plt.xlabel(df.columns[0], fontsize=10)
        plt.ylabel(df.columns[1], fontsize=10)
        #plt.title(title, fontsize=18)

    elif chart_type == 'pie':
        labels = df.iloc[:, 1] if df.shape[1] > 1 else None
        plt.pie(df.iloc[:, 0], labels=labels, autopct='%1.1f%%', textprops={'fontsize': 16})
        #plt.title(title, fontsize=18)

    elif chart_type == 'hist':
        sns.histplot(df.iloc[:, 0], bins=len(df.iloc[:, 0].unique()), discrete=True)
        plt.xlabel(df.columns[0], fontsize=10)
        plt.ylabel("Частота", fontsize=10)
        #plt.title(title, fontsize=18)

    elif chart_type == 'cascade':
        x = np.arange(len(df.iloc[:, 0]))
        y = df.iloc[:, 0]
        start_points = np.zeros_like(y)
        start_points[1:] = np.cumsum(y[:-1])
        colors = ['green' if v >= 0 else 'red' for v in y]
        plt.bar(x, y, bottom=start_points, color=colors)
        plt.xlabel(df.columns[0], fontsize=10)
        plt.ylabel("Изменение", fontsize=10)
        #plt.title(title, fontsize=18)

    elif chart_type == 'scatter':
        sns.scatterplot(x=df.iloc[:, 0], y=df.iloc[:, 1])
        plt.xlabel(df.columns[0], fontsize=10)
        plt.ylabel(df.columns[1], fontsize=10)
        #plt.title(title, fontsize=18)

    elif chart_type == 'wordcloud':
        text = ' '.join(df.iloc[:, 0].astype(str))
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        #plt.title(title, fontsize=18)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)

    return buf.getvalue() 

#@app.task
def visualize_old(df_json, var: str) -> bytes:
    df = pd.read_json(df_json)

    if df.shape[1] < 2:
        raise ValueError("DataFrame должен содержать как минимум 2 столбца")

    x = df.iloc[:, 0]
    y = df.iloc[:, 1]

    plt.figure(figsize=(8, 5))
    plt.bar(x, y, color='skyblue')
    plt.xlabel(x.name)
    plt.ylabel(y.name)
    plt.title(var)
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)

    return buf.getvalue()  # Возвращаем байты, а не io.BytesIO
