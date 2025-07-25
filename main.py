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

# Almacenamiento temporal de respuestas
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

    asyncio.ensure_future(enviar())

    # Usamos la clave original como referencia
    respuestas[valor.lower()] = "⌛ Esperando respuesta de @lederdata_publico_bot..."

    return jsonify({
        "status": "✅ Consulta enviada correctamente",
        "comando_enviado": mensaje
    })

@app.route("/respuesta")
def respuesta():
    valor = request.args.get("valor")
    if not valor:
        return jsonify({"error": "Falta el parámetro 'valor'"}), 400

    respuesta = respuestas.get(valor.lower(), "❌ Sin respuesta aún.")
    return jsonify({"respuesta": respuesta})


# Captura de respuestas del bot
@app_tg.on_message(filters.chat("lederdata_publico_bot"))
async def recibir_respuesta(client, message):
    # Si es texto
    if message.text:
        texto = message.text
        print("📩 Texto recibido:", texto)

        for clave in respuestas:
            if clave in texto.lower():
                respuestas[clave] = texto
                return

        respuestas["ultima"] = texto

    # Si es foto
    elif message.photo:
        file_path = await message.download()
        print("📸 Foto descargada:", file_path)
        respuestas["ultima"] = f"[📷 Imagen recibida y descargada: {file_path}]"

    # Si es documento (PDF u otros)
    elif message.document:
        file_path = await message.download()
        print("📄 Documento recibido:", file_path)
        respuestas["ultima"] = f"[📄 Documento recibido y descargado: {file_path}]"

    else:
        respuestas["ultima"] = "[❓ Respuesta en formato no reconocido]"

# Iniciar la app
if __name__ == "__main__":
    print("🚀 Iniciando Telegram + Flask...")
    app_tg.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
