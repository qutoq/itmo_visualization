from aiogram.utils.keyboard import (
    ReplyKeyboardBuilder,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardBuilder
)

from src.texts import choice_types

back = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отмена')]], resize_keyboard=True)


def keyboard_vizual_vars():
    builder = ReplyKeyboardBuilder()
    for el in choice_types.keys():
        builder.button(text=el) 
    builder.button(text='Отмена')
    builder.adjust(2, 2, 2, 1)

    return builder.as_markup()
