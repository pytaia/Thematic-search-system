# Рабочая программа с пересылкой картинки, но вроде все так же сделано

import logging
from telegram.ext import Application, MessageHandler, filters
from telegram.ext import CommandHandler
import aiohttp


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


async def start(update, context):
    """Отправляет сообщение когда получена команда /start"""
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я Бот-геокодер. Напишите мне адрес, и я покажу вам это место!",
    )


async def help_command(update, context):
    """Отправляет сообщение когда получена команда /help"""
    await update.message.reply_text("Введите адрес места, которое хотите увидеть. "
                                    "Внимательно проверьте введенные данные, "
                                    "иначе бот может не сработать! "
                                    "Вводите только адрес или название места. "
                                    "Никакой лишней информации!")


async def geocoder(update, context):
    geocoder_uri = "http://geocode-maps.yandex.ru/1.x/"
    response = await get_response(geocoder_uri, params={
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "format": "json",
        "geocode": update.message.text
    })

    if not response:
        await update.message.reply_text("Ошибка выполнения запроса:")
        await update.message.reply_text(f"Http статус: {response.status_code} ({response.reason})")

    else:
        toponym = response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        ll, spn = ','.join(toponym["Point"]["pos"].split(' ')), 0.005
        mess = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]

        static_api_request = f"http://static-maps.yandex.ru/1.x/?ll={ll}&spn={spn},{spn}&l=map&pt={ll},vkbkm"
        await context.bot.send_photo(
            update.message.chat_id,
            static_api_request,
            caption=f"Нашёл: {mess}"
        )


async def get_response(url, params):
    logger.info(f"getting {url}")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()


def main():
    #Токен не указан
    application = Application.builder().token('').build()

    text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, geocoder)

    application.add_handler(text_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.run_polling()


if __name__ == '__main__':
    main()