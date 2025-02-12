from aiogram.utils.keyboard import (
    ReplyKeyboardBuilder,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardBuilder
)


def keyboard_vizual_vars():
    builder = ReplyKeyboardBuilder()

    builder.button(text='1 вариант') # ,callback_data='1'
    builder.button(text='52 вариант')
    builder.button(text='333')
    builder.button(text='4 вариант')
    builder.button(text='Отмена')
    builder.adjust(2, 2, 1)

    return builder.as_markup()
