from telegram.ext import ConversationHandler
from telegram.ext import Application, MessageHandler, filters
from telegram.ext import CommandHandler
import logging
import aiohttp

from random import choice
import requests

from data.user_data import UserData
from data.request_history import RequestHistory
from data import db_session
from system_functions import getting_an_image
from main import main as bd_main
from logical_framework import Multiple_analysis
from branching_bot_responses import response_to_the_request, ask_me


#logging.basicConfig(
#    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
#)

#logger = logging.getLogger(__name__)


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
        greeting = [rf"Привет, {new_user.name}!", rf"Здравствуй, {new_user.name}!",
                    rf"Питон Макс к вашим услугам"]
        await update.message.reply_html(
            choice(greeting),
        )
        await update.message.reply_html(
            choice(ask_me),
        )
        return 2


async def stop(update, context):
    user = update.effective_user
    db_sess = db_session.create_session()
    new_user = db_sess.query(UserData).filter(UserData.login.like(user.username)).first()
    farewell = [rf"Пока, {new_user.name}.", rf"До свидания, {new_user.name}.",
                rf"Всего хорошего!"]
    await update.message.reply_html(
        choice(farewell),
    )
    return ConversationHandler.END


async def rename(update, context):
    # изменение имени
    await update.message.reply_html(
        rf"Введи желаемое имя",)
    return 1


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
    await update.message.reply_html(
        choice(ask_me),
    )
    return 2


async def my_request(update, context):
    await update.message.reply_html(
        choice(response_to_the_request),
    )
    db_sess = db_session.create_session()
    request = update.message.text
    user_id = db_sess.query(UserData).filter(UserData.login.like(update.effective_user.username)).first()
    # сюда твой класс вместо заглушки
    request = Multiple_analysis(request, user_id.id)
    answer = (request.analysis_result_output(), request.type_requests)
    # пока без гс
    answer = getting_an_image(answer)
    await context.bot.send_photo(
        update.message.chat_id,
        answer[0],
        caption=''
    )
    await update.message.reply_html(
        answer[1],
    )
    return 2


async def get_response(url, params):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()


async def help_command(update, context):
    """Отправляет сообщение когда получена команда /help"""
    # фраза вывода еще будет редактироваться, пока оставлю это как заглушку
    await update.message.reply_text("Здравствуй, я питон Макс.")
    await update.message.reply_text("Вот, что я уже умею:\n"
                                    "/start -- начать работу.\n"
                                    "/name -- изменить имя пользователя.\n"
                                    "/help -- получить справку о работе программы\n"
                                    "/stop -- завершить работу программы")


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
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, my_name)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, my_request)]
        },

        fallbacks=[CommandHandler("help", help_command), CommandHandler("name", rename),
                   CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler)
    # обработчик гс
    #application.add_handler(voice_handler)

    application.run_polling()


if __name__ == '__main__':
    main()