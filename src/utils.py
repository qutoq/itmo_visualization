import io
import pandas as pd
from aiogram.fsm.context import FSMContext


async def save_dataframe(state: FSMContext, df: pd.DataFrame):
    csv_data = df.to_csv(index=False)
    await state.update_data(dataframe=csv_data)


async def load_dataframe(state: FSMContext):
    data = await state.get_data()
    if "dataframe" in data:
        df = pd.read_csv(io.StringIO(data["dataframe"]))
        return df
    return None
