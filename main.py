import os
import asyncio
from flask import Flask, request, jsonify
from pyrogram import Client, filters
from dotenv import load_dotenv
from threading import Thread

# Cargar .env
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

# Cliente de Pyrogram
app_tg = Client(
    name="mi_sesion",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING
)

# Flask
app = Flask(__name__)
respuestas = {}

@app.route("/")
def home():
    return "✅ API Flask + Pyrogram funcionando correctamente"

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
            respuestas[valor.lower()] = "⌛ Esperando respuesta..."
        except Exception as e:
            print("❌ Error enviando mensaje:", e)

    # Ejecutar en el loop de Pyrogram
    asyncio.run_coroutine_threadsafe(enviar_mensaje(), app_tg.loop)

    return jsonify({
        "comando_enviado": mensaje,
        "status": "✅ Consulta enviada correctamente"
    })

@app.route("/respuesta")
def obtener_respuesta():
    valor = request.args.get("valor")
    if not valor:
        return jsonify({"error": "Falta el parámetro 'valor'"}), 400

    return jsonify({
        "respuesta": respuestas.get(valor.lower(), "❌ Sin respuesta aún.")
    })

# Escucha de respuestas del bot
@app_tg.on_message(filters.chat("lederdata_publico_bot"))
async def recibir_respuesta(client, message):
    texto = message.text or ""
    print("📨 Mensaje recibido:", texto)

    # Verifica coincidencias
    for clave in respuestas:
        if clave in texto.lower():
            respuestas[clave] = texto
            return
    respuestas["ultima"] = texto

# Ejecutar Pyrogram y Flask en paralelo
def iniciar_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    print("🚀 Iniciando bot y servidor web...")
    app_tg.start()
    Thread(target=iniciar_flask).start()
