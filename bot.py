from pyrogram import Client
from pyrogram.enums import ParseMode
import os
import time

api_id = int(os.environ["API_ID"])
api_hash = os.environ["API_HASH"]
bot_token = os.environ["BOT_TOKEN"]
mi_id = int(os.environ["MI_ID"])  # Tu ID personal

app = Client("mi_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message()
def escuchar_mensajes(client, message):
    if message.text == "/test":
        message.reply("✅ Estoy funcionando correctamente.")

app.start()

print("🤖 Bot Pyrogram corriendo...")

while True:
    time.sleep(60)
