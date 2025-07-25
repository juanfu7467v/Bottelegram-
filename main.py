import os
import asyncio
from flask import Flask, request, jsonify
from pyrogram import Client, filters
from dotenv import load_dotenv

# Cargar variables del entorno
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

# Variables compartidas
respuestas = {}
loop = asyncio.get_event_loop()

# Cliente de Pyrogram
app_tg = Client(
    name="mi_sesion",
    session_string=SESSION_STRING,
    api_id=API_ID,
    api_hash=API_HASH
)

# Flask App
app = Flask(__name__)

@app.route("/")
def index():
    return "✅ Flask + Telegram funcionando"

@app.route("/consulta")
def consulta():
    comando = request.args.get("comando")
    valor = request.args.get("valor")

    if not comando or not valor:
        return jsonify({"error": "Faltan parámetros"}), 400

    mensaje = f"/{comando} {valor}"

    async def enviar_mensaje():
        try:
            await app_tg.send_message("lederdata_publico_bot", mensaje)
            respuestas[valor.lower()] = "⌛ Esperando respuesta del bot..."
        except Exception as e:
            respuestas[valor.lower()] = f"❌ Error: {str(e)}"

    loop.create_task(enviar_mensaje())

    return jsonify({
        "status": "✅ Consulta enviada correctamente",
        "comando_enviado": mensaje
    })

@app.route("/respuesta")
def respuesta():
    valor = request.args.get("valor")
    if not valor:
        return jsonify({"error": "Falta el parámetro 'valor'"}), 400

    return jsonify({
        "respuesta": respuestas.get(valor.lower(), "❌ Sin respuesta aún.")
    })

# Escuchar respuestas del bot
@app_tg.on_message(filters.chat("lederdata_publico_bot"))
async def recibir(client, message):
    if message.text:
        texto = message.text.lower()
        print("📩 Mensaje recibido:", texto)
        for clave in respuestas:
            if clave in texto:
                respuestas[clave] = message.text
                return
        respuestas["ultima"] = message.text

# Ejecutar Flask y Pyrogram
if __name__ == "__main__":
    async def iniciar():
        await app_tg.start()
        print("✅ Bot Telegram iniciado")
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

    loop.run_until_complete(iniciar())
