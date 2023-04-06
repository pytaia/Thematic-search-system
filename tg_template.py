import logging
from telegram.ext import Application, MessageHandler, filters
from telegram.ext import CommandHandler

from data.user_data import UserData
from data.request_history import RequestHistory
from data import db_session2
from main import main


main()
#logging.basicConfig(
#    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
#)

#logger = logging.getLogger(__name__)


async def start(update, context):
    """Отправляет сообщение когда получена команда /start"""
    # здесь вывод тоже будет редактироваться под стилистику общения бота
    print(update.effective_user.username)
    user = update.effective_user
    db_sess = db_session2.create_session()
    if user.username not in [item.login for item in db_sess.query(UserData).all()]:
        new_user = UserData()
        new_user.login = user.username
        db_sess.add(new_user)
        db_sess.commit()
        await update.message.reply_html(
            rf"Привет {user.mention_html()}! Я ... .",
        )
        # skip ущу не прописано
        await update.message.reply_html(
            rf"Как к тебе обращаться? (Напиши имя или команду /skip, если тебя устраивает это обращение)",
        )
    else:
        user = user.username
        name = db_sess.query(UserData).filter(UserData.login.like(user)).first()['name']
        await update.message.reply_html(
            rf"Привет {name}!",
        )


async def help_command(update, context):
    """Отправляет сообщение когда получена команда /help"""
    # фраза вывода еще будет редактироваться, пока оставлю это как заглушку
    await update.message.reply_text("Я пока не умею помогать... Я только ваше эхо.")


async def echo(update, context):
    await update.message.reply_text(f"Я получил сообщение {update.message.text}")


def main():
    # ПОМЕНЯТЬ ТОКЕН ПЕРЕД СДАЧЕЙ
    application = Application.builder().token('6042512660:AAGMdc8FAhR1XovphTfkB1Rin7lQG6Lg6gU').build()

    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)

    application.add_handler(text_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.run_polling()


if __name__ == '__main__':
    main()