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

# Iniciar cliente de Pyrogram (sin loop)
app_tg = Client(
    "mi_sesion",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    workdir="./"
)

# Iniciar app Flask
app = Flask(__name__)

# Almacenamiento de respuestas (memoria temporal)
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
        await app_tg.send_message("LederDataBot", mensaje)

    # Ejecutar la tarea sin bloquear Flask
    asyncio.ensure_future(enviar())

    # Guardar estado inicial
    respuestas[valor] = "⌛ Esperando respuesta del bot..."

    return jsonify({
        "status": "✅ Consulta enviada",
        "mensaje_enviado": mensaje
    })


@app.route("/respuesta")
def respuesta():
    valor = request.args.get("valor")
    if not valor:
        return jsonify({"error": "Falta el parámetro 'valor'"}), 400

    respuesta = respuestas.get(valor, "❌ Sin resultados aún.")
    return jsonify({"respuesta": respuesta})


# Escuchar respuestas de @LederDataBot
@app_tg.on_message(filters.chat("LederDataBot"))
async def recibir_respuesta(client, message):
    texto = message.text or "[Respuesta no textual]"
    print("📩 Respuesta del bot:", texto)

    # Buscar coincidencia con claves guardadas
    for clave in respuestas:
        if clave in texto:
            respuestas[clave] = texto
            return

    # Si no se encuentra coincidencia, guardar como última genérica
    respuestas["ultima"] = texto


# Iniciar la app
if __name__ == "__main__":
    print("🚀 Iniciando Telegram y Flask...")
    app_tg.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
