import io
import pandas as pd
from aiogram.fsm.context import FSMContext
import re

from src import texts

async def save_dataframe(state: FSMContext, df: pd.DataFrame):
    try:
        csv_data = df.to_csv(index=False)
        await state.update_data(dataframe=csv_data)
    except Exception as e:
        return texts.err_df


async def load_dataframe(state: FSMContext):
    try:
        data = await state.get_data()
        if "dataframe" in data:
            df = pd.read_csv(io.StringIO(data["dataframe"]))
            return df
        await state.clear()
        return texts.err_df
    except Exception as e:
        await state.clear()
        return texts.err_df
    

def get_cols(text):
    cols = []
    for col in text.split():
        if col.startswith("'") and col.endswith("'"):
            cols.append(col[1:-1])
        else:
            return -1
    return cols


def escape_md_v2(text) -> str:
    text = str(text)
    special_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(r"([" + re.escape(special_chars) + r"])", r"\\\1", text)
