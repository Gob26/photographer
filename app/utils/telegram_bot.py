from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from flask_login import login_user
from werkzeug.security import check_password_hash
from app.models.user import User
from app.models.post import Post
from app.extensions import db, bcrypt
from app.__init__ import create_app
import os

TOKEN = '7484238687:AAFywOTF8ZkhVIcXFwAtGG6IhlrqQBxGhrU'
app = create_app()

user_auth = {}
user_states = {}

menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Войти", callback_data="login")],
    [InlineKeyboardButton(text="Добавить статью", callback_data="add_article")]
])

# Настройка директории для сохранения изображений
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'img', 'blog')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Выберите действие:", reply_markup=menu)

async def process_login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("Пожалуйста, введите ваш логин:")
    user_states[update.callback_query.from_user.id] = "waiting_for_login"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    with app.app_context():
        if user_states.get(user_id) == "waiting_for_login":
            user_states[user_id] = "waiting_for_password"
            context.user_data['login'] = update.message.text
            await update.message.reply_text("Теперь введите ваш пароль:")
        elif user_states.get(user_id) == "waiting_for_password":
            login = context.user_data['login']
            password = update.message.text
            user = User.query.filter_by(login=login).first()

            if user and bcrypt.check_password_hash(user.password, password):
                user_auth[user_id] = True
                await update.message.reply_text("Вы успешно вошли в систему!")
            else:
                await update.message.reply_text("Неверный логин или пароль. Попробуйте еще раз.")

            user_states.pop(user_id, None)

        elif user_states.get(user_id) == "waiting_for_title":
            context.user_data['title'] = update.message.text
            user_states[user_id] = "waiting_for_content"
            await update.message.reply_text("Теперь введите содержание статьи:")
        elif user_states.get(user_id) == "waiting_for_content":
            context.user_data['content'] = update.message.text
            user_states[user_id] = "waiting_for_snippet"
            await update.message.reply_text("Введите краткое описание (сниппет) статьи:")
        elif user_states.get(user_id) == "waiting_for_snippet":
            context.user_data['snippet'] = update.message.text
            user_states[user_id] = "waiting_for_images"
            await update.message.reply_text("Теперь отправьте изображения (если есть):")
        elif user_states.get(user_id) == "waiting_for_images":
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
                title = context.user_data['title']
                content = context.user_data['content']
                snippet = context.user_data['snippet']
                images = context.user_data.get('images', [])

                post = Post(title=title, content=content, snippet=snippet, images=images)
                db.session.add(post)
                db.session.commit()

                await update.message.reply_text("Статья успешно добавлена!")
                user_states.pop(user_id, None)
            else:
                await update.message.reply_text("Пожалуйста, отправьте изображение или напишите 'готово', чтобы завершить.")

async def process_add_article(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()

    if user_auth.get(update.callback_query.from_user.id):
        await update.callback_query.message.reply_text("Введите заголовок статьи:")
        user_states[update.callback_query.from_user.id] = "waiting_for_title"
    else:
        await update.callback_query.message.reply_text("Пожалуйста, сначала войдите в систему.")

def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(process_login, pattern='login'))
    application.add_handler(CallbackQueryHandler(process_add_article, pattern='add_article'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
