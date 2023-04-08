import logging
from telegram.ext import ConversationHandler
from telegram.ext import Application, MessageHandler, filters
from telegram.ext import CommandHandler

from data.user_data import UserData
from data.request_history import RequestHistory
from data import db_session2
from main import main as bd_main
from work_with_api import address_is_true, work_with_request



#logging.basicConfig(
#    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
#)

#logger = logging.getLogger(__name__)


async def start(update, context):
    """Отправляет сообщение когда получена команда /start"""
    # здесь вывод тоже будет редактироваться под стилистику общения бота, но в целом готово
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
        await update.message.reply_html(
            rf"Как к тебе обращаться? (Напиши имя или skip, если тебя устраивает это обращение)",
        )
        return 1
    else:
        user = user.username
        new_user = db_sess.query(UserData).filter(UserData.login.like(user)).first()
        await update.message.reply_html(
            rf"Привет {new_user.name}!",
        )
        if not new_user.address:
            await update.message.reply_html(
                rf"{new_user.name}, для упрощения работы программы укажите свой адрес или напишите skip, для пропуска этого этапа.",
            )
            return 2


async def stop(update, context):
    user = update.effective_user
    db_sess = db_session2.create_session()
    new_user = db_sess.query(UserData).filter(UserData.login.like(user.username)).first()
    await update.message.reply_html(
        rf"До свидания, {new_user.name}!",
    )
    return ConversationHandler.END


async def rename(update, context):
    await update.message.reply_html(
        rf"Введите желаемое имя",)
    return 1


async def readdress(update, context):
    await update.message.reply_html(
        rf"Введите свой адрес",)
    return 2


async def my_name(update, context):
    # функция для знакомства. надо добавить еще функцию изменения имени, которая будет приводить сюда же
    user = update.effective_user
    name = update.message.text
    db_sess = db_session2.create_session()
    new_user = db_sess.query(UserData).filter(UserData.login.like(user.username)).first()
    if name == 'skip':
        new_user.name = user.mention_html()
    else:
        new_user.name = name
    db_sess.commit()
    await update.message.reply_html(
        rf"{new_user.name}, имя вы всегда сможете изменить вызвав функцию /name",
    )
    if not new_user.address:
        await update.message.reply_html(
            rf"{new_user.name}, для упрощения работы программы укажите свой адрес или напишите skip, для пропуска этого этапа.",
        )
        return 2


async def my_address(update, context):
    # функция, узнающая адрес, или соглашающаяся узнать его позже. еще надо направляющую сюда функцию написать.
    user = update.effective_user
    address = update.message.text
    db_sess = db_session2.create_session()
    new_user = db_sess.query(UserData).filter(UserData.login.like(user.username)).first()
    if address == 'skip':
        await update.message.reply_html(
            rf"Хорошо, вернемся к этому позже.",
        )
    else:
        if address_is_true(address):
            new_user.address = address
            db_sess.commit()
            await update.message.reply_html(
                rf"Ваш адрес изменен",
            )
        else:
            await update.message.reply_html(
                rf"Ваш адрес не найден. Проверьте коректность записи и попробуйте еще раз, вызвав функцию /address",
            )
    await update.message.reply_html(
        rf"Спроси у меня что-нибудь.",
    )
    return 3


async def my_request(update, context):
    request = update.message.text
    work_with_request(request)
    await update.message.reply_html(
        rf"Пока бот не умеет обрабатывать запросы.",
    )


async def help_command(update, context):
    """Отправляет сообщение когда получена команда /help"""
    # фраза вывода еще будет редактироваться, пока оставлю это как заглушку
    await update.message.reply_text("Здравствуйте, я ... .")
    await update.message.reply_text("Вот, что я уже умею:\n"
                                    "/start -- начать работу.\n"
                                    "/name -- изменить имя пользователя.\n"
                                    "/address -- изменить адрес по умолчанию.\n"
                                    "/help -- получить справку о работе программы\n"
                                    "/stop -- завершить работу программы")


async def echo(update, context):
    # обработчик сообщений, думаю отсюда начнется твоя часть.
    await update.message.reply_text(f"Я получил сообщение {update.message.text}")


def main():
    # временный юз бота @my_helpik_bot
    # ПОМЕНЯТЬ ТОКЕН ПЕРЕД СДАЧЕЙ
    bd_main()
    application = Application.builder().token('6042512660:AAGMdc8FAhR1XovphTfkB1Rin7lQG6Lg6gU').build()

    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, my_name)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, my_address)],
            3: [MessageHandler(filters.TEXT & ~filters.COMMAND, my_request)]
        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler("help", help_command), CommandHandler("name", rename),
                   CommandHandler("address", readdress), CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler)

    application.add_handler(text_handler)

    application.run_polling()


if __name__ == '__main__':
    main()