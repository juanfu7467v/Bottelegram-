import os
import asyncio
from flask import Flask, request, jsonify
from pyrogram import Client, filters
from dotenv import load_dotenv

# Cargar variables desde .env
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

# Iniciar cliente de Pyrogram
app_tg = Client(
    "mi_sesion",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    workdir="./"
)

# Iniciar app Flask
app = Flask(__name__)

# Almacenamiento de respuestas
respuestas = {}

@app.route("/")
def home():
    return "✅ API Pyrogram + Flask funcionando"

@app.route("/consulta")
def consulta():
    comando = request.args.get("comando")
    valor = request.args.get("valor")

    if not comando or not valor:
        return jsonify({"error": "Faltan parámetros: comando y valor"}), 400

    mensaje = f"/{comando} {valor}"

    async def enviar():
        await app_tg.send_message("lederdata_publico_bot", mensaje)

    try:
        # Ejecutar la corrutina en el loop del cliente de Pyrogram
        asyncio.run_coroutine_threadsafe(enviar(), app_tg.loop)
        respuestas[valor.lower()] = "⌛ Esperando respuesta de @lederdata_publico_bot..."

        return jsonify({
            "status": "✅ Consulta enviada correctamente",
            "comando_enviado": mensaje
        })

    except Exception as e:
        return jsonify({"error": f"❌ Error al enviar mensaje: {str(e)}"}), 500

@app.route("/respuesta")
def respuesta():
    valor = request.args.get("valor")
    if not valor:
        return jsonify({"error": "Falta el parámetro 'valor'"}), 400

    return jsonify({
        "respuesta": respuestas.get(valor.lower(), "❌ Sin respuesta aún.")
    })

# Captura de mensajes del bot
@app_tg.on_message(filters.chat("lederdata_publico_bot"))
async def recibir_respuesta(client, message):
    if message.text:
        texto = message.text
        print("📩 Texto recibido:", texto)

        for clave in respuestas:
            if clave in texto.lower():
                respuestas[clave] = texto
                return

        respuestas["ultima"] = texto

    elif message.photo:
        file_path = await message.download()
        print("📸 Foto descargada:", file_path)
        respuestas["ultima"] = f"[📷 Imagen descargada: {file_path}]"

    elif message.document:
        file_path = await message.download()
        print("📄 Documento descargado:", file_path)
        respuestas["ultima"] = f"[📄 Documento descargado: {file_path}]"

    else:
        respuestas["ultima"] = "[❓ Respuesta en formato no reconocido]"

# Lanzar Flask y Pyrogram juntos
if __name__ == "__main__":
    print("🚀 Iniciando Telegram + Flask...")
    app_tg.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
