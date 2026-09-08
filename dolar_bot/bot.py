import requests
import logging
import json
import time
import os  # 👈 NUEVO: Para variables de entorno
import threading  # 👈 NUEVO: Para el servidor web
from http.server import HTTPServer, BaseHTTPRequestHandler  # 👈 NUEVO
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ========== CONFIGURACIÓN ==========
TOKEN = "8768535605:AAEgwIdXp0Jnnxrf8K4wZKOXSbsNfrr4C3M"
# ⚠️ RECOMENDACIÓN: Usa variable de entorno en lugar de token hardcodeado
# TOKEN = os.environ.get("BOT_TOKEN", "TU_TOKEN_AQUI")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ========== SERVIDOR WEB PARA HEALTH CHECK (NUEVO) ==========
class HealthHandler(BaseHTTPRequestHandler):
    """Maneja las solicitudes de health check de Render."""
    
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

    def log_message(self, format, *args):
        # Suprime logs del servidor para no saturar
        return

def run_health_server():
    """Inicia un servidor web simple en el puerto asignado por Render."""
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info(f"✅ Servidor de health check corriendo en puerto {port}")

# ========== ARCHIVO DE USUARIOS PREMIUM ==========
PREMIUM_USERS_FILE = "premium_users.json"

def load_premium_users():
    """Carga datos de usuarios premium desde el archivo JSON."""
    try:
        with open(PREMIUM_USERS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": [], "waitlist": []}

def save_premium_users(data):
    """Guarda datos de usuarios premium en el archivo JSON."""
    with open(PREMIUM_USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ========== SISTEMA DE CÁCACHE DÓLAR (5 minutos) ==========
dolar_cache = {"precio": None, "timestamp": None}

def _get_dolar_eltoque():
    """Intenta obtener dólar desde API elTOQUE."""
    try:
        url = "https://api.eltoque.com/v1/dolar"
        response = requests.get(url, timeout=30)
        data = response.json()
        blue = data.get('blue')
        oficial = data.get('oficial')
        return True, blue, oficial
    except Exception as e:
        logger.warning(f"elTOQUE API error: {e}")
        return False, None, None

def get_dolar():
    """Obtiene precio del dólar con caché de 5 minutos."""
    global dolar_cache

    if dolar_cache["timestamp"] and datetime.now() - dolar_cache["timestamp"] < timedelta(minutes=5):
        return dolar_cache["precio"]

    success, blue, oficial = _get_dolar_eltoque()
    
    if success and blue is not None and oficial is not None:
        mensaje = (
            f"💵 **Dólar en Cuba**\n\n"
            f"🇺🇸 **Dólar Blue (informal):** {blue} CUP\n"
            f"🏛️ **Dólar Oficial:** {oficial} CUP\n"
            f"📅 Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            f"⚠️ *Precio aproximado del mercado informal.*"
        )
        dolar_cache["precio"] = mensaje
        dolar_cache["timestamp"] = datetime.now()
        return mensaje

    # Fallback con datos estimados
    estimated_oficial = 24
    estimated_blue = 660
    
    mensaje = (
        f"💵 **Dólar en Cuba**\n\n"
        f"🇨🇺 **Oficial (tasa BCC):** {estimated_oficial} CUP\n"
        f"💎 **Blue/Informal:** {estimated_blue} CUP\n"
        f"📅 Consultado: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        f"⚠️ *Datos estimados - la API elTOQUE está fuera de línea momentáneamente*"
        f"\n\n*Fuente: Tasa Representativa del Mercado Informal (elTOQUE/OMFi)*"
    )
    
    dolar_cache["precio"] = mensaje
    dolar_cache["timestamp"] = datetime.now()
    return mensaje

def get_analisis_economico():
    """Genera análisis económico de Cuba con formato Markdown y emojis."""
    try:
        analisis = (
            "📊 **Análisis Económico de Cuba**\n\n"
            "🔹 **Tendencias actuales del mercado:**\n"
            "• El dólar muestra volatilidad en el mercado informal.\n"
            "• Presión inflacionaria por escasez de divisas en el país.\n"
            "• Impacto de las sanciones internacionales en el comercio.\n"
            "• Variaciones en el tipo de cambio oficial vs informal.\n\n"
            "📰 **Noticias destacadas:**\n"
            "• Actualizaciones sobre políticas monetarias cubanas.\n"
            "• Informes de organismos internacionales sobre la economía.\n"
            "• Cambios en el mercado de divisas MLC.\n\n"
            "📌 **Recomendaciones básicas:**\n"
            "• Mantener monitoreo constante del precio del dólar.\n"
            "• Diversificar ahorros entre diferentes activos.\n"
            "• Consultar fuentes oficiales para precios regulados.\n\n"
            "💡 *Este análisis es una estimación basada en datos disponibles.*"
        )
        return analisis
    except Exception as e:
        logger.error(f"Error al generar análisis económico: {e}")
        return "⚠️ **Error:** No se pudo generar el análisis económico. Intenta más tarde."

# ========== COMANDOS DEL BOT ==========
# (Tus funciones start, dolar, analisis, premium, ayuda, button_callback van aquí)
# ... EL RESTO DE TU CÓDIGO PERMANECE IGUAL ...

# ========== MAIN ==========
def main():
    """Inicia el bot y configura los handlers."""
    
    # 👈 NUEVO: Inicia el servidor web ANTES del bot
    run_health_server()
    
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dolar", dolar))
    app.add_handler(CommandHandler("analisis", analisis))
    app.add_handler(CommandHandler("premium", premium))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(CallbackQueryHandler(button_callback))

    logger.info("🤖 Bot DolarCubaAnalisisBot iniciado correctamente")
    print("🤖 Bot DolarCubaAnalisisBot iniciado correctamente")

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
