import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from flask import current_app
from app.models.user import User
from app.models.post import Post
from app.extensions import db, bcrypt
from app.__init__ import create_app
from app.models.photosession import Category, Photosession

# Конфигурация
TOKEN = '7484238687:AAFywOTF8ZkhVIcXFwAtGG6IhlrqQBxGhrU'
app = create_app()

# Глобальные переменные для хранения состояний пользователей
user_auth = {}
user_states = {}

# Клавиатура главного меню
menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Войти", callback_data="login")],
    [InlineKeyboardButton(text="Добавить статью", callback_data="add_article")],
    [InlineKeyboardButton(text="Добавить фотосессию",  callback_data="add_photosession")]
])

category_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton(text=category.value, callback_data=category.name) for category in Category]
])

# Настройка директории для сохранения изображений
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'img', 'blog')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Функции-обработчики команд

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /start. Отправляет приветственное сообщение и показывает главное меню.
    """
    await update.message.reply_text("Привет! Выберите действие:", reply_markup=menu)

async def process_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик нажатия кнопки "Войти". Запускает процесс авторизации.
    """
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("Пожалуйста, введите ваш логин:")
    user_states[update.callback_query.from_user.id] = "waiting_for_login"

async def process_add_article(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик нажатия кнопки "Добавить статью". Проверяет авторизацию и запускает процесс добавления статьи.
    """
    await update.callback_query.answer()

    if user_auth.get(update.callback_query.from_user.id):
        await update.callback_query.message.reply_text("Введите заголовок статьи:")
        user_states[update.callback_query.from_user.id] = "waiting_for_title"
    else:
        await update.callback_query.message.reply_text("Пожалуйста, сначала войдите в систему.")


async def process_add_photosession(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик нажатия кнопки "Добавить фотосессию". Проверяет авторизацию и запускает процесс добавления фотосессии.
    """
    # Ответить на событие (нажатие кнопки)
    await update.callback_query.answer()

    # Проверяем, авторизован ли пользователь
    user_id = update.callback_query.from_user.id
    if user_auth.get(user_id):
        await update.callback_query.message.reply_text("Введите заголовок фотосессии:")
        user_states[user_id] = {"state": "waiting_for_photosession_title"}  # Убедитесь, что это словарь
    else:
        await update.callback_query.message.reply_text("Пожалуйста, сначала войдите в систему.")


async def process_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик выбора категории фотосессии.
    """
    await update.callback_query.answer()

    # Получаем категорию, которую выбрал пользователь
    category_name = update.callback_query.data  # Это имя категории, например, 'wedding'

    # Проверяем, есть ли такая категория в перечислении
    if category_name not in Category.__members__:
        await update.callback_query.message.reply_text("Ошибка: выбранная категория не существует.")
        return

    category = Category[category_name]  # Получаем объект категории из перечисления

    # Сохраняем выбранную категорию в состоянии пользователя
    user_states[update.callback_query.from_user.id] = user_states.get(update.callback_query.from_user.id, {})
    user_states[update.callback_query.from_user.id]['category'] = category

    # Создаем путь для загрузки фотографий
    upload_folder = current_app.config['SERVER_PATH']
    UPLOAD_FOLDER_PHOTOSESSION = os.path.join(upload_folder, category.name)  # Используем имя категории для папки

    # Проверяем, существует ли папка, и создаем её при необходимости
    if not os.path.exists(UPLOAD_FOLDER_PHOTOSESSION):
        os.makedirs(UPLOAD_FOLDER_PHOTOSESSION)

    # Уведомляем пользователя о выбранной категории и запрашиваем заголовок
    await update.callback_query.message.reply_text(
        f"Выбранная категория: {category.value}. Теперь введите заголовок фотосессии:")

    # Устанавливаем состояние на ожидание заголовка фотосессии
    user_states[update.callback_query.from_user.id]['state'] = "waiting_for_photosession_title"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Основной обработчик текстовых сообщений и изображений.
    Обрабатывает различные состояния пользователя: авторизация, добавление статьи.
    """
    user_id = update.message.from_user.id

    with app.app_context():
        if user_states.get(user_id) == "waiting_for_login":
            await handle_login(update, context)
        elif user_states.get(user_id) == "waiting_for_password":
            await handle_password(update, context)
        elif user_states.get(user_id) in ["waiting_for_title", "waiting_for_content", "waiting_for_snippet"]:
            await handle_article_text(update, context)
        elif user_states.get(user_id) == "waiting_for_images":
            await handle_article_images(update, context)


async def handle_photosession_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Основной обработчик текстовых сообщений и изображений для фотосессий.
    Обрабатывает различные состояния пользователя: авторизация, добавление фотосессии.
    """
    user_id = update.message.from_user.id

    with app.app_context():
        if user_states.get(user_id) == "waiting_for_login":
            await handle_login(update, context)
        elif user_states.get(user_id) == "waiting_for_password":
            await handle_password(update, context)
        elif user_states.get(user_id) == "waiting_for_photosession_title":
            await handle_photosession_title(update, context)
        elif user_states.get(user_id) == "waiting_for_photosession_description":
            await handle_photosession_description(update, context)
        elif user_states.get(user_id) == "waiting_for_photosession_content":
            await handle_photosession_content(update, context)
        elif user_states.get(user_id) == "waiting_for_photosession_category":
            await handle_photosession_category(update, context)
        elif user_states.get(user_id) == "waiting_for_photosession_images":
            await handle_photosession_images(update, context)


async def handle_photosession_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    current_state = user_states.get(user_id)
    # Сохраняем заголовок фотосессии
    context.user_data['title'] = update.message.text
    # Устанавливаем состояние на ожидание мета описания
    user_states[user_id] = "waiting_for_photosession_description"

    await update.message.reply_text("Теперь введите мета описание:")


async def handle_photosession_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    # Сохраняем мета описание фотосессии
    context.user_data['meta_description'] = update.message.text
    # Устанавливаем состояние на ожидание содержания
    user_states[user_id] = "waiting_for_photosession_content"

    await update.message.reply_text("Теперь введите содержание фотосессии:")


async def handle_photosession_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    # Сохраняем содержание фотосессии
    context.user_data['content'] = update.message.text
    # Устанавливаем состояние на ожидание категории
    user_states[user_id] = "waiting_for_photosession_category"

    await update.message.reply_text("Теперь выберите категорию фотосессии из списка:")


async def handle_photosession_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    category_name = update.message.text  # Получаем выбранную категорию от пользователя
    # Проверка, что категория существует
    if category_name not in Category.__members__:
        await update.message.reply_text("Ошибка: выбранная категория не существует. Попробуйте снова.")
        return

    # Сохраняем выбранную категорию
    context.user_data['category'] = Category[category_name]
    user_states[user_id] = "waiting_for_photosession_images"

    await update.message.reply_text(f"Выбранная категория: {context.user_data['category'].value}. Теперь загрузите изображения фотосессии:")

#Добавление фото Нужно  потом ошибки обработать!!!!!!!!!!!!!!!!!
async def handle_photosession_images(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.photo:
        photo = update.message.photo[-1].file_id
        file = await context.bot.get_file(photo)
        file_path = os.path.join(UPLOAD_FOLDER, f"{photo}.jpg")
        await file.download_to_drive(file_path)
        if 'photos' not in context.user_data:
            context.user_data['photos'] = []
        context.user_data['photos'].append(os.path.basename(file_path))
        await update.message.reply_text(
            "Изображение добавлено. Отправьте еще изображения или напишите 'готово', чтобы завершить.")
    elif update.message.text.lower() == 'готово':
        await finalize_article(update, context)
    else:
        await update.message.reply_text("Пожалуйста, отправьте изображение или напишите 'готово', чтобы завершить.")


# Вспомогательные функции
async def handle_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает ввод логина пользователем.
    """
    user_states[update.message.from_user.id] = "waiting_for_password"
    context.user_data['login'] = update.message.text
    await update.message.reply_text("Теперь введите ваш пароль:")

async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает ввод пароля и выполняет проверку авторизации.
    """
    login = context.user_data['login']
    password = update.message.text
    user = User.query.filter_by(login=login).first()

    if user and bcrypt.check_password_hash(user.password, password):
        user_auth[update.message.from_user.id] = True
        await update.message.reply_text("Вы успешно вошли в систему!")
    else:
        await update.message.reply_text("Неверный логин или пароль. Попробуйте еще раз.")

    user_states.pop(update.message.from_user.id, None)

async def handle_article_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает ввод текстовой информации для новой статьи (заголовок, содержание, сниппет).
    """
    user_id = update.message.from_user.id
    current_state = user_states.get(user_id)

    if current_state == "waiting_for_title":
        context.user_data['title'] = update.message.text
        user_states[user_id] = "waiting_for_content"
        await update.message.reply_text("Теперь введите содержание статьи:")
    elif current_state == "waiting_for_content":
        context.user_data['content'] = update.message.text
        user_states[user_id] = "waiting_for_snippet"
        await update.message.reply_text("Введите краткое описание (сниппет) статьи:")
    elif current_state == "waiting_for_snippet":
        context.user_data['snippet'] = update.message.text
        user_states[user_id] = "waiting_for_images"
        await update.message.reply_text("Теперь отправьте изображения (если есть):")

#Нужно потом ошибки обработать!!!!!!!!!!!!!!!!!
async def handle_article_images(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обрабатывает загрузку изображений для статьи и завершает процесс добавления статьи.
    """
    if update.message.photo:
        photo = update.message.photo[-1].file_id
        file = await context.bot.get_file(photo)
        file_path = os.path.join(UPLOAD_FOLDER, f"{photo}.jpg")
        await file.download_to_drive(file_path)
        if 'images' not in context.user_data:
            context.user_data['images'] = []
        context.user_data['images'].append(os.path.basename(file_path))
        await update.message.reply_text("Изображение добавлено. Отправьте еще изображения или напишите 'готово', чтобы завершить.")
    elif update.message.text.lower() == 'готово':
        await finalize_article(update, context)
    else:
        await update.message.reply_text("Пожалуйста, отправьте изображение или напишите 'готово', чтобы завершить.")

async def finalize_article(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Завершает процесс добавления статьи, сохраняя её в базу данных.
    """
    title = context.user_data['title']
    content = context.user_data['content']
    snippet = context.user_data['snippet']
    images = context.user_data.get('images', [])

    post = Post(title=title, content=content, snippet=snippet, images=images)
    db.session.add(post)
    db.session.commit()

    await update.message.reply_text("Статья успешно добавлена!")
    user_states.pop(update.message.from_user.id, None)


async def finalize_photosession(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    # Получаем все данные из user_data
    title = context.user_data.get('title')
    meta_description = context.user_data.get('meta_description')
    content = context.user_data.get('content')
    category = context.user_data.get('category')
    photos = context.user_data.get('photos', [])

    new_photoshoot = Photosession(title=title, meta_description=meta_description, content=content, category=category, photos=photos)

    await update.message.reply_text("Фотосессия успешно добавлена!")

    # Сброс состояний пользователя
    user_states[user_id] = None
    context.user_data.clear()  # Очищаем пользовательские данные


def main() -> None:
    """
    Основная функция для запуска бота.
    """
    application = ApplicationBuilder().token(TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(process_login, pattern='login'))
    application.add_handler(CallbackQueryHandler(process_add_article, pattern='add_article'))
    application.add_handler(CallbackQueryHandler(process_add_article, pattern='add_photosession'))
    application.add_handler(CallbackQueryHandler(process_add_article, pattern='process_category_selection'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()