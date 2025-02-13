from celery import Celery
import pandas as pd
import matplotlib.pyplot as plt
import io

app = Celery("tasks")
app.config_from_object("config.celeryconfig")

@app.task
def add(x, y):
    return x + y


@app.task
def visualize(df_json, var: str) -> bytes:
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
