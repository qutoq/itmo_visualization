import io
import pandas as pd
from aiogram.fsm.context import FSMContext


async def save_dataframe(state: FSMContext, df: pd.DataFrame):
    csv_data = df.to_csv(index=False)  # Конвертируем в CSV-строку
    await state.update_data(dataframe=csv_data)


async def load_dataframe(state: FSMContext):
    data = await state.get_data()
    if "dataframe" in data:
        df = pd.read_csv(io.StringIO(data["dataframe"]))
        return df
    return None


async def get_dataframe(state: FSMContext, input):
    if type(input) == str:
        df = pd.read_csv(io.StringIO(input))
    else:
        df = pd.read_csv(input)
    await save_dataframe(state, df)
