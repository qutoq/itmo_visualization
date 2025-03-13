import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import pandas as pd
import json
import io

from src.tasks import generate_plot
from src.states import Stage
from src.keyboards import keyboard_visual_vars, keyboard_start, keyboard_again, back, back_again
from src.utils import save_dataframe, load_dataframe
from src.utils import get_cols, escape_md_v2
from src import texts
from src.errors import MyError

router: Router = Router()


@router.message(Command("start"))
async def process_any_message(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(texts.start, reply_markup=keyboard_start(), parse_mode="MarkdownV2")

@router.message(F.text == texts.btn_rules) 
async def visual(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(texts.txt_rules, reply_markup=keyboard_start(), parse_mode="MarkdownV2")

@router.message(Command("visual"))
@router.message(F.text == texts.visual) 
async def visual(message: Message, state: FSMContext):
    await state.set_state(Stage.input)
    await message.answer(texts.await_csv, reply_markup=back)


@router.message(F.text == texts.again_stage_2) 
async def again(message: Message, state: FSMContext):
    df = await load_dataframe(state)
    if type(df) == str: 
        return await message.answer(df)
    await message.answer(texts.choice, reply_markup=keyboard_visual_vars()) 
    await state.set_state(Stage.choice)


@router.message(Command("cancel"))
@router.message(F.text.lower() == "отмена")
@router.message(F.text.lower() == "в главное меню")
async def cancel(message: Message, state: FSMContext):
    await message.answer(texts.cancel, reply_markup=keyboard_start())
    await state.clear()
    return
    

@router.message(F.text == texts.btn_legend) 
async def lega(message: Message, state: FSMContext):
    await message.answer(texts.legend, parse_mode="MarkdownV2")


@router.message(Stage.input)
async def stage_1(message: Message, state: FSMContext):
    try:
        if message.text:
            df = pd.read_csv(io.StringIO(message.text))
        elif message.document:
            bot = message.bot
            file = await bot.get_file(message.document.file_id) 
            file_bytes = await bot.download_file(file.file_path)
            df = pd.read_csv(io.BytesIO(file_bytes.getvalue())) 
        else:
            await message.answer(texts.err_again)
            await state.clear()
            return
    except Exception as e:
        await message.answer(texts.err_again)
        return
    
    res = await save_dataframe(state, df)
    if res:
        await message.answer(res)
        return
    
    await message.answer(texts.choice, reply_markup=keyboard_visual_vars()) 
    await state.set_state(Stage.choice)


@router.message(Stage.choice)
async def pre_stage_2(message: Message, state: FSMContext):
    if message.text in texts.choice_types.keys(): 
        await state.update_data(choice=message.text)
    else:
        return
    
    df = await load_dataframe(state)
    if type(df) == str:
        return await message.answer(df)
    
    rows = min(7, len(df))
    text = f"*Полученая информация:*\nСписок столбцов: {df.columns.tolist()} \n"
    text += f'Часть данных:```{df.sample(rows)}```'
    await message.answer(text, parse_mode="MarkdownV2", reply_markup=back_again())  
    await message.answer(texts.choice_types[message.text], parse_mode="MarkdownV2")
    await message.answer(texts.await_columns)
    await state.set_state(Stage.columns)


@router.message(Stage.columns)
async def stage_3(message: Message, state: FSMContext):
    df = await load_dataframe(state)
    if type(df) == str: 
        return await message.answer(df)
    
    cols = get_cols(message.text)
    if cols == -1: 
        return await message.answer(texts.err_again)

    try:
        vis_df = df[cols]
    except Exception as e:
        return await message.answer(texts.err_again)

    rows = min(7, len(df))
    text = f"*Общая информация:* \n```{escape_md_v2(vis_df.sample(rows))}```"
    await message.answer(text, parse_mode="MarkdownV2", reply_markup=back)  

    data = await state.get_data()
    task = generate_plot.delay(vis_df.to_json(), data['choice'])
    await message.answer(f"Задача запущена! ID: {task.id}")
    try:
        loop = asyncio.get_running_loop()
        image_bytes = await loop.run_in_executor(None, task.get, 10)
    except MyError as err:
        return await message.answer(err.message)
    except Exception as e:
        return await message.answer(texts.err_plot)

    await message.answer_photo(BufferedInputFile(image_bytes, filename="chart.png"))
    await message.answer(texts.final, reply_markup=keyboard_again())
    