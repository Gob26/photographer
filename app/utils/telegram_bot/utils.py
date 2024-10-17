from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from app.models.photosession import Category

# Основное меню
menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Войти", callback_data="login")],
    [InlineKeyboardButton(text="Добавить статью", callback_data="add_article")],
    [InlineKeyboardButton(text="Добавить фотосессию", callback_data="add_photosession")],
    [InlineKeyboardButton(text="Добавить услугу", callback_data="add_service")]
])

# Создание клавиатуры категорий
def create_category_menu():
    keyboard = []
    row = []
    for category in Category:
        if len(row) == 2:
            keyboard.append(row)
            row = []
        row.append(InlineKeyboardButton(text=category.value[:20], callback_data=f"category_{category.name}"))
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

category_menu = create_category_menu()
