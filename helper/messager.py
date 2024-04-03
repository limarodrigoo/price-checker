from telegram import Bot
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

class Messager:
    async def send_message(self, product, url, price):
        bot = Bot(TELEGRAM_TOKEN)
        updates = await bot.get_updates()

        if updates:
            last_update = updates[-1]

            if last_update.message:
                print(last_update.message.chat_id)
                chat_id = last_update.message.chat_id
        else:
            print("Nenhuma atualização recebida")

        message = f"Preço do produto {product} caiu! R${price} Acesse: {url}"
        print("PRICE FOUND!")
        if chat_id == None:
            chat_id = 1251102646
        await bot.send_message(chat_id=chat_id, text=message)
