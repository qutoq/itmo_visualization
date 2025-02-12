import asyncio
import io
import pandas as pd
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.tasks import add
from src.states import Stage
from src.keyboards import keyboard_vizual_vars
from src.utils import get_dataframe, load_dataframe

router: Router = Router()


@router.message(Command("start"))
async def process_any_message(message: Message, state: FSMContext):
    await state.clear()
    await message.reply('Вводный текст')


@router.message(Command("add"))
async def test(message: Message):
    task = add.delay(2, 2)  # Запускаем задачу
    await message.answer(f"Задача запущена! ID: {task.id}")
    
    # Ожидание результата (НЕ блокирует asyncio)
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, task.get, 20)  # Ждём максимум 20 сек
    await message.answer(f"Результат: {result}")


@router.message(Command("visual"))
async def test(message: Message, state: FSMContext):
    await state.set_state(Stage.input)
    await message.reply('Введите текст')


@router.message(Stage.input)
async def stage_1(message: Message, state: FSMContext):
    await get_dataframe(state, message.text)
    await message.answer('Выбери тип диаграммы', reply_markup=keyboard_vizual_vars()) 
    await state.set_state(Stage.choice)


@router.message(Stage.choice)
async def stage_2(message: Message, state: FSMContext):
    if message.text == 'Отмена':
        await message.answer('Отмена', reply_markup=ReplyKeyboardRemove())
        await state.clear()
        return
    df = await load_dataframe(state)
    #if df:
    await message.answer(df.to_string() + '\n' + message.text, reply_markup=ReplyKeyboardRemove())
    #else:
    #    await message.answer('Ошибка загрузки данных. Попробуйте снова')
    #    await state.clear()
    #    return

    #task = add.delay(2, 2)
    #await message.answer(f"Задача запущена! ID: {task.id}")
    #loop = asyncio.get_running_loop()
    #result = await loop.run_in_executor(None, task.get, 20)
    await state.clear()
