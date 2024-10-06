import os
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from flask import current_app
from app.models.user import User
from app.models.post import Post
from app.models.photosession import Category, Photosession, Photo
from app.extensions import db, bcrypt
from app.__init__ import create_app

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
    [InlineKeyboardButton(text="Добавить фотосессию", callback_data="add_photosession")]
])

# Настройка директории для сохранения изображений
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'img', 'blog')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Функции-обработчики команд

# Создаем постоянную клавиатуру с кнопкой "Меню"
menu_keyboard = ReplyKeyboardMarkup([[KeyboardButton("Меню")]], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик команды /start. Отправляет приветственное сообщение и показывает постоянную кнопку "Меню".
    """
    await update.message.reply_text("Привет! Нажмите кнопку 'Меню' для доступа к функциям.", reply_markup=menu_keyboard)

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик нажатия кнопки "Меню". Показывает inline-клавиатуру с основными действиями.
    """
    await update.message.reply_text("Выберите действие:", reply_markup=menu)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик нажатий на кнопки inline-клавиатуры.
    """
    query = update.callback_query
    await query.answer()

    if query.data == "login":
        await query.message.reply_text("Вы выбрали вход в систему.")
    elif query.data == "add_article":
        await query.message.reply_text("Вы выбрали добавление статьи.")
    elif query.data == "add_photosession":
        await query.message.reply_text("Вы выбрали добавление фотосессии.")

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
    await update.callback_query.answer()

    user_id = update.callback_query.from_user.id
    if user_auth.get(user_id):
        await update.callback_query.message.reply_text("Введите заголовок фотосессии:")
        user_states[user_id] = {"state": "waiting_for_photosession_title"}
    else:
        await update.callback_query.message.reply_text("Пожалуйста, сначала войдите в систему.")

# Функция для создания клавиатуры категорий
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


async def process_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Обработчик выбора категории фотосессии.
    """
    await update.callback_query.answer()

    # Получаем название категории из нажатой кнопки
    category_name = update.callback_query.data.split('_')[1]

    # Проверяем, существует ли такая категория
    if category_name not in Category.__members__:
        await update.callback_query.message.reply_text("Ошибка: выбранная категория не существует.")
        return

    category = Category[category_name]

    # Сохраняем категорию в состояние пользователя
    user_states[update.callback_query.from_user.id] = user_states.get(update.callback_query.from_user.id, {})
    user_states[update.callback_query.from_user.id]['category'] = category

    # Сохраняем значение category.name в context.user_data
    context.user_data['category_name'] = category.name  # Измените здесь на category.name

    # Проверка правильного сохранения категории
    print(f"Выбранная категория: {category.name}")

    # Далее работа с файлами для сохранения изображений в правильной папке
    with app.app_context():
        upload_folder = current_app.config['SERVER_PATH']
        UPLOAD_FOLDER_PHOTOSESSION = os.path.join(upload_folder, category.name)

        if not os.path.exists(UPLOAD_FOLDER_PHOTOSESSION):
            os.makedirs(UPLOAD_FOLDER_PHOTOSESSION)

    # Сохраняем путь загрузки в context.user_data
    context.user_data['upload_folder_photosession'] = UPLOAD_FOLDER_PHOTOSESSION

    await update.callback_query.message.reply_text(
        f"Выбранная категория: {category.name}. Теперь загрузите изображения фотосессии:")

    # Меняем состояние пользователя для ожидания изображений
    user_states[update.callback_query.from_user.id]['state'] = "waiting_for_photosession_images"



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
        elif isinstance(user_states.get(user_id), dict) and user_states[user_id]['state'] in [
            "waiting_for_photosession_title", "waiting_for_photosession_description",
            "waiting_for_photosession_content", "waiting_for_photosession_category",
            "waiting_for_photosession_images"
        ]:
            await handle_photosession_message(update, context)

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
        elif user_states[user_id]['state'] == "waiting_for_photosession_title":
            await handle_photosession_title(update, context)
        elif user_states[user_id]['state'] == "waiting_for_photosession_description":
            await handle_photosession_description(update, context)
        elif user_states[user_id]['state'] == "waiting_for_photosession_content":
            await handle_photosession_content(update, context)
        elif user_states[user_id]['state'] == "waiting_for_photosession_category":
            await handle_photosession_category(update, context)
        elif user_states[user_id]['state'] == "waiting_for_photosession_images":
            await handle_photosession_images(update, context)

async def handle_photosession_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    context.user_data['title'] = update.message.text
    user_states[user_id]['state'] = "waiting_for_photosession_description"
    # Логирование заголовка
    print(f"Заголовок фотосессии: {context.user_data['title']}")
    await update.message.reply_text("Теперь введите мета описание:")

async def handle_photosession_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    context.user_data['meta_description'] = update.message.text
    user_states[user_id]['state'] = "waiting_for_photosession_content"

    await update.message.reply_text("Теперь введите содержание фотосессии:")

async def handle_photosession_content(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    context.user_data['content'] = update.message.text
    user_states[user_id]['state'] = "waiting_for_photosession_category"

    await update.message.reply_text("Теперь выберите категорию фотосессии из списка:", reply_markup=category_menu)

async def handle_photosession_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    category_name = update.message.text.lower()  # Преобразуем в верхний регистр для соответствия с Enum

    if category_name not in Category.__members__:
        await update.message.reply_text("Ошибка: выбранная категория не существует. Попробуйте снова.")
        return

    category = Category[category_name]
    context.user_data['category'] = category
    user_states[user_id]['state'] = "waiting_for_photosession_images"

    await update.message.reply_text(f"Выбранная категория: {category.value}. Теперь загрузите изображения фотосессии:")


async def handle_photosession_images(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    UPLOAD_FOLDER_PHOTOSESSION = context.user_data.get('upload_folder_photosession')

    if update.message.photo:
        photo = update.message.photo[-1].file_id
        file = await context.bot.get_file(photo)
        file_path = os.path.join(UPLOAD_FOLDER_PHOTOSESSION, f"{photo}.jpg")  #################### КУда сохранять
        await file.download_to_drive(file_path)
        if 'photos' not in context.user_data:
            context.user_data['photos'] = []
        context.user_data['photos'].append(os.path.basename(file_path))

        # Логирование пути к файлу изображения
        print(f"Изображение сохранено: {file_path}")

        await update.message.reply_text(
            "Изображение добавлено. Отправьте еще изображения или напишите 'готово', чтобы завершить.")
    elif update.message.text.lower() == 'готово':
        await finalize_photosession(update, context)
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

# В функции finalize_photosession добавьте проверку на наличие категории
async def finalize_photosession(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    title = context.user_data.get('title')
    meta_description = context.user_data.get('meta_description')
    content = context.user_data.get('content')
    category_name = context.user_data.get('category_name')  # Получаем category.name
    photo_filenames = context.user_data.get('photos', [])

    # Логирование всех данных перед отправкой в базу
    print(f"Финальные данные фотосессии: Заголовок: {title}, Описание: {meta_description}, "
          f"Контент: {content}, Категория: {category_name}, Фото: {photo_filenames}")

    # Проверка наличия всех необходимых данных
    if not all([title, meta_description, content, category_name]):
        await update.message.reply_text("Ошибка: не все необходимые данные для фотосессии заполнены.")
        return

    # Убедимся, что категория - это строка
    if not isinstance(category_name, str):
        await update.message.reply_text("Ошибка: неверная категория фотосессии.")
        return

    try:
        new_photoshoot = Photosession(
            title=title,
            meta_description=meta_description,
            content=content,
            category=category_name,  # Используем category_name
            created_at=datetime.utcnow(),
            show_on_main=False
        )
        db.session.add(new_photoshoot)
        db.session.flush()  # Чтобы получить id новой фотосессии!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        for filename in photo_filenames:
            photo = Photo(filename=filename, photosession_id=new_photoshoot.id)
            db.session.add(photo)

        db.session.commit()
        await update.message.reply_text("Фотосессия успешно добавлена!")
    except IntegrityError as e:
        db.session.rollback()
        await update.message.reply_text(f"Ошибка при сохранении фотосессии: {str(e)}")
    except Exception as e:
        db.session.rollback()
        await update.message.reply_text(f"Произошла неожиданная ошибка: {str(e)}")
    finally:
        user_states[user_id] = None
        context.user_data.clear()


def main() -> None:
    """
    Основная функция для запуска бота.
    """
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("^Меню$"), show_menu))
    application.add_handler(CallbackQueryHandler(process_login, pattern='login'))
    application.add_handler(CallbackQueryHandler(process_add_article, pattern='add_article'))
    application.add_handler(CallbackQueryHandler(process_add_photosession, pattern='add_photosession'))
    application.add_handler(CallbackQueryHandler(process_category_selection, pattern='^category_'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
