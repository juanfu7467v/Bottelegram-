import os
import asyncio
from flask import Flask, request, jsonify
from pyrogram import Client, filters
from dotenv import load_dotenv

# Cargar .env
load_dotenv()

# Credenciales
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

# Iniciar Pyrogram
loop = asyncio.get_event_loop()
app_tg = Client(
    "mi_sesion",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    workdir="./",
    loop=loop
)

# Iniciar Flask
app = Flask(__name__)

# Almacenamiento simple
respuestas = {}

@app.route("/")
def home():
    return "✅ API funcionando correctamente"

@app.route("/consulta")
def consulta():
    comando = request.args.get("comando")
    valor = request.args.get("valor")

    if not comando or not valor:
        return jsonify({"error": "Faltan parámetros: comando y valor"}), 400

    mensaje = f"/{comando} {valor}"

    async def enviar():
        await app_tg.send_message("LederDataBot", mensaje)

    loop.create_task(enviar())

    # Asociar respuesta con valor
    respuestas[valor] = "Esperando respuesta..."

    return jsonify({"status": "Consulta enviada", "comando": comando, "valor": valor})


@app.route("/respuesta")
def respuesta():
    valor = request.args.get("valor")
    if not valor:
        return jsonify({"error": "Falta parámetro valor"}), 400

    resultado = respuestas.get(valor, "Sin resultados aún.")
    return jsonify({"respuesta": resultado})


# Captura de mensajes entrantes del bot
@app_tg.on_message(filters.chat("LederDataBot"))
async def capturar_respuesta(client, message):
    texto = message.text or "[Respuesta sin texto]"
    print("📩 Mensaje recibido:", texto)

    # Intentamos encontrar el DNI u otro valor dentro del texto
    for clave in list(respuestas.keys()):
        if clave in texto:
            respuestas[clave] = texto
            break
    else:
        respuestas["ultima"] = texto


# Iniciar aplicación
if __name__ == "__main__":
    print("Iniciando Telegram y Flask...")
    app_tg.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
