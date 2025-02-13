from aiogram.utils.keyboard import (
    ReplyKeyboardBuilder,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardBuilder
)

from src import texts

back = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отмена')]], resize_keyboard=True)


def keyboard_visual_vars():
    builder = ReplyKeyboardBuilder()
    for el in texts.choice_types.keys():
        builder.button(text=el) 
    builder.button(text='Отмена')
    builder.adjust(2, 2, 2, 1)

    return builder.as_markup()


def keyboard_again():
    builder = ReplyKeyboardBuilder()
    builder.button(text=texts.again_stage_2) 
    builder.button(text='В главное меню')
    builder.adjust(2)

    return builder.as_markup()


def keyboard_start():
    builder = ReplyKeyboardBuilder()
    builder.button(text=texts.btn_rules) 
    builder.button(text=texts.visual)
    builder.adjust(2)

    return builder.as_markup()

