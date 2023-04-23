from telegram.ext import ConversationHandler
from telegram.ext import Application, MessageHandler, filters
from telegram.ext import CommandHandler

from random import choice

from data.user_data import UserData
from data.request_history import RequestHistory
from data import db_session
from main import main as bd_main
from system_functions import address_is_true
from logical_framework import Multiple_analysis
from branching_bot_responses import response_to_the_request


async def start(update, context):
    """Отправляет сообщение когда получена команда /start"""
    # здесь вывод тоже будет редактироваться под стилистику общения бота, но в целом готово
    user = update.effective_user
    db_sess = db_session.create_session()
    if user.username not in [item.login for item in db_sess.query(UserData).all()]:
        new_user = UserData()
        new_user.login = user.username
        db_sess.add(new_user)
        db_sess.commit()
        await update.message.reply_html(
            rf"Привет {user.mention_html()}! Я питон Макс.",
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
                rf"{new_user.name}, для упрощения работы программы укажи свой адрес или напиши skip, для пропуска этого этапа.",
            )
            return 2


async def stop(update, context):
    user = update.effective_user
    db_sess = db_session.create_session()
    new_user = db_sess.query(UserData).filter(UserData.login.like(user.username)).first()
    await update.message.reply_html(
        rf"До свидания, {new_user.name}!",
    )
    return ConversationHandler.END


async def rename(update, context):
    # изменение имени
    await update.message.reply_html(
        rf"Введи желаемое имя",)
    return 1


async def readdress(update, context):
    # изменение адреса
    await update.message.reply_html(
        rf"Введи свой адрес",)
    return 2


async def my_name(update, context):
    # изменение имени
    user = update.effective_user
    name = update.message.text
    db_sess = db_session.create_session()
    new_user = db_sess.query(UserData).filter(UserData.login.like(user.username)).first()
    if name == 'skip':
        new_user.name = user.mention_html()
    else:
        new_user.name = name
    db_sess.commit()
    await update.message.reply_html(
        rf"{new_user.name}, имя ты всегда сможешь изменить вызвав функцию /name",
    )
    if not new_user.address:
        await update.message.reply_html(
            rf"{new_user.name}, для упрощения работы программы укажи свой адрес или напиши skip, для пропуска этого этапа.",
        )
        return 2


async def my_address(update, context):
    # изменение адреса
    user = update.effective_user
    address = update.message.text
    db_sess = db_session.create_session()
    new_user = db_sess.query(UserData).filter(UserData.login.like(user.username)).first()
    if address == 'skip':
        await update.message.reply_html(
            rf"Хорошо, вернемся к этому позже.",
        )
    else:
        coord = address_is_true(address)
        if coord:
            new_user.address = coord
            db_sess.commit()
            await update.message.reply_html(
                rf"Твой адрес изменен",
            )
        else:
            await update.message.reply_html(
                rf"Твой адрес не найден. Проверь коректность записи и попробуй еще раз, вызвав функцию /address",
            )
    await update.message.reply_html(
        rf"Спроси у меня что-нибудь.",
    )
    return 3


async def my_request(update, context):
    await update.message.reply_html(
        choice(response_to_the_request),
    )
    db_sess = db_session.create_session()
    request = update.message.text
    user_id = db_sess.query(UserData).filter(UserData.login.like(update.effective_user.username)).first()
    # сюда твой класс вместо заглушки
    request = Multiple_analysis(request, user_id.id)
    answer = request.analysis_result_output()
    #тут допишем еще переход к уточнению адреса и вывода. еще над диалогами поработаем. + насчет адреса еще не решили


async def help_command(update, context):
    """Отправляет сообщение когда получена команда /help"""
    # фраза вывода еще будет редактироваться, пока оставлю это как заглушку
    await update.message.reply_text("Здравствуй, я питон Макс.")
    await update.message.reply_text("Вот, что я уже умею:\n"
                                    "/start -- начать работу.\n"
                                    "/name -- изменить имя пользователя.\n"
                                    "/address -- изменить адрес по умолчанию.\n"
                                    "/help -- получить справку о работе программы\n"
                                    "/stop -- завершить работу программы")


async def echo(update, context):
    # обработчик незапланированных сообщений, если пошло не по плану диалога
    await update.message.reply_text(f"Прости, я не расслышал вопрос. Повтори, пожалуйста")
    # вот тут возможно переход не сработает,тогда просто продублировать функцию my_request
    return 3


async def voice(update, context):
    mess = update.message.voice.file_id
    # считывать аудио
    await update.message.reply_html(
        choice(response_to_the_request),
    )


def main():
    # юз бота @thematic_search_engine_bot
    bd_main()
    application = Application.builder().token('5998954719:AAFEErzH8fLAWiYh_MF2eCDvjtYGiEowwbY').build()

    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
    voice_handler = MessageHandler(filters.VOICE, voice)

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
    application.add_handler(voice_handler)

    application.run_polling()


if __name__ == '__main__':
    main()