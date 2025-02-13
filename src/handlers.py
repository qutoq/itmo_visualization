import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import pandas as pd
import json
import io

from src.tasks import add, generate_plot
from src.states import Stage
from src.keyboards import keyboard_vizual_vars, back
from src.utils import save_dataframe, load_dataframe
from src.utils import get_cols, escape_md_v2
from src import texts

router: Router = Router()


@router.message(Command("start"))
async def process_any_message(message: Message, state: FSMContext):
    await state.clear()
    await message.reply('Вводный текст')


@router.message(Command("visual"))
async def test(message: Message, state: FSMContext):
    await state.set_state(Stage.input)
    await message.reply('Введите текст', reply_markup=back)


@router.message(F.text.lower() == "отмена") 
async def test(message: Message, state: FSMContext):
    await message.answer('Отмена', reply_markup=ReplyKeyboardRemove())
    await state.clear()
    return
    

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
            await message.answer('Ошибка загрузки данных. Попробуйте снова')
            await state.clear()
            return
    except Exception as e:
        await message.answer('Неверный формат данных')
        return
    
    res = await save_dataframe(state, df)
    await message.answer(texts.choice, reply_markup=keyboard_vizual_vars()) 

    await state.set_state(Stage.choice)


@router.message(Stage.choice)
async def stage_2(message: Message, state: FSMContext):
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
    await message.answer(text, parse_mode="MarkdownV2", reply_markup=back)  
    await message.answer(texts.choice_types[message.text] + '\nВведи названия столбцов для визуализации')

    await state.set_state(Stage.columns)


@router.message(Stage.columns)
async def stage_3(message: Message, state: FSMContext):
    df = await load_dataframe(state)
    if type(df) == str: 
        return await message.answer(df)
    
    cols = get_cols(message.text)
    if cols == -1: 
        return await message.answer('Неверный формат данных. Попробуйте снова')

    vis_df = df[cols]
    rows = min(7, len(df))
    text = f"*Общая информация:* \n```{escape_md_v2(vis_df.sample(rows))}```"
    await message.answer(text, parse_mode="MarkdownV2", reply_markup=back)  

    data = await state.get_data()
    print(data)
    task = generate_plot.delay(vis_df.to_json(), data['choice'])
    await message.answer(f"Задача запущена! ID: {task.id}")
    await state.clear()

    loop = asyncio.get_running_loop()
    image_bytes = await loop.run_in_executor(None, task.get, 10)

    await message.answer_photo(BufferedInputFile(image_bytes, filename="chart.png"))


@router.message(Command("add"))
async def test(message: Message):
    task = add.delay(2, 2)  # Запускаем задачу
    await message.answer(f"Задача запущена! ID: {task.id}")
    
    # Ожидание результата (НЕ блокирует asyncio)
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, task.get, 20)  # Ждём максимум 20 сек
    await message.answer(f"Результат: {result}")

@router.message(F.text.lower() == "52") 
async def test(message: Message, state: FSMContext):
    await message.answer('писят два')

    