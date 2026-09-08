import requests
import logging
import json
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ========== CONFIGURACIÓN ==========
TOKEN = "8768535605:AAEgwIdXp0Jnnxrf8K4wZKOXSbsNfrr4C3M"
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ========== SERVIDOR WEB PARA HEALTH CHECK ==========
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
        f"⚠️ *Datos estimados - la API elTOQUE está fuera de línea momentáneamente*\n\n"
        f"*Fuente: Tasa Representativa del Mercado Informal (elTOQUE/OMFi)*"
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Mensaje de bienvenida con botones interactivos."""
    user_id = str(update.effective_user.id)
    premium_data = load_premium_users()
    is_premium = user_id in premium_data["users"]

    keyboard = [
        [InlineKeyboardButton("📊 Ver Dólar", callback_data="dolar")],
        [InlineKeyboardButton("📰 Análisis Económico", callback_data="analisis")],
        [InlineKeyboardButton("⭐ Hacerse Premium", callback_data="premium")],
    ]

    estado = "⭐ Premium" if is_premium else "🟢 Gratuito"

    mensaje = (
        f"🇨🇺 **Bienvenido a DolarCubaAnalisisBot**\n\n"
        f"📊 Tu asistente económico para Cuba.\n"
        f"🔹 **Estado:** {estado}\n\n"
        f"Usa los botones o comandos:\n"
        f"/dolar - Ver precio del dólar\n"
        f"/analisis - Análisis económico\n"
        f"/premium - Info de suscripción\n"
        f"/ayuda - Ver comandos"
    )

    await update.message.reply_text(
        mensaje,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )

async def dolar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /dolar - Precio del dólar con caché."""
    await update.message.reply_text(get_dolar(), parse_mode="Markdown")

async def analisis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /analisis - Análisis económico."""
    await update.message.reply_text(get_analisis_economico(), parse_mode="Markdown")

async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /premium - Información del plan premium y estado del usuario."""
    user_id = str(update.effective_user.id)
    premium_data = load_premium_users()
    is_premium = user_id in premium_data["users"]
    is_waitlist = user_id in premium_data["waitlist"]

    if is_premium:
        mensaje = (
            "⭐ **Ya eres usuario Premium**\n\n"
            "Beneficios que disfrutas:\n"
            "✅ Alertas personalizadas del dólar en tiempo real\n"
            "✅ Análisis detallado diario con IA\n"
            "✅ Reportes exclusivos semanales\n"
            "✅ Soporte prioritario directo\n\n"
            "Gracias por confiar en DolarCubaAnalisisBot."
        )
        await update.message.reply_text(mensaje, parse_mode="Markdown")

    elif is_waitlist:
        pos = premium_data["waitlist"].index(user_id) + 1
        mensaje = (
            f"📝 **Estás en la lista de espera**\n\n"
            f"Posición: {pos} de {len(premium_data['waitlist'])}\n\n"
            "Te avisaremos cuando haya una vacante disponible para premium."
        )
        await update.message.reply_text(mensaje, parse_mode="Markdown")

    else:
        disponible = 500 - len(premium_data["users"])
        keyboard = [
            [InlineKeyboardButton("📝 Unirse a lista de espera", callback_data="join_waitlist")],
        ]
        mensaje = (
            "⭐ **Plan Premium**\n\n"
            "Precio: **500 CUP/mes**\n\n"
            "Beneficios premium:\n"
            "✅ Alertas personalizadas del dólar\n"
            "✅ Análisis detallado con IA\n"
            "✅ Reportes exclusivos\n"
            "✅ Soporte prioritario\n\n"
            f"Cupos disponibles: **{disponible} / 500**\n\n"
            "¿Te unes a la lista de espera?"
        )
        await update.message.reply_text(
            mensaje,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /ayuda - Lista de comandos disponibles."""
    mensaje = (
        "🇨🇺 **Ayuda de DolarCubaAnalisisBot**\n\n"
        "Comandos disponibles:\n"
        "/start - Menú principal y bienvenida\n"
        "/dolar - Ver precio actual del dólar\n"
        "/analisis - Análisis económico de Cuba\n"
        "/premium - Información del plan suscripción\n"
        "/ayuda - Mostrar este mensaje\n\n"
        "📌 Funcionalidades:\n"
        "• Precio del dólar blue y oficial desde elTOQUE\n"
        "• Análisis económico con tendencias actuales\n"
        "• Sistema de lista de espera para premium\n"
        "• Caché de 5 minutos para evitar peticiones excesivas\n\n"
        "Creado con 🇨🇺 para la comunidad economica."
    )
    await update.message.reply_text(mensaje, parse_mode="Markdown")

# ========== CALLBACKS DE TECLADO INTERACTIVO ==========

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejo de callbacks de botones inline."""
    query = update.callback_query
    await query.answer()
    user_id = str(update.effective_user.id)
    premium_data = load_premium_users()

    if query.data == "dolar":
        await query.edit_message_text(get_dolar(), parse_mode="Markdown")

    elif query.data == "analisis":
        await query.edit_message_text(get_analisis_economico(), parse_mode="Markdown")

    elif query.data == "premium":
        is_premium = user_id in premium_data["users"]
        is_waitlist = user_id in premium_data["waitlist"]

        if is_premium:
            mensaje = "⭐ **Ya eres usuario Premium**\n\nGracias por tu apoyo."
            await query.edit_message_text(mensaje, parse_mode="Markdown")

        elif is_waitlist:
            pos = premium_data["waitlist"].index(user_id) + 1
            mensaje = (
                f"📝 **Estás en la lista de espera**\n\n"
                f"Posición: {pos}"
            )
            await query.edit_message_text(mensaje, parse_mode="Markdown")

        else:
            keyboard = [
                [InlineKeyboardButton("📝 Unirse a lista de espera", callback_data="join_waitlist")],
                [InlineKeyboardButton("🔙 Volver", callback_data="back_start")],
            ]
            mensaje = (
                "⭐ **Plan Premium**\n\n"
                "Precio: **500 CUP/mes**\n\n"
                "Beneficios:\n"
                "✅ Alertas personalizadas del dólar\n"
                "✅ Análisis con IA\n"
                "✅ Reportes exclusivos\n\n"
                f"Cupos disponibles: **{500 - len(premium_data['users'])} / 500**\n\n"
                "¿Te unes a la lista de espera?"
            )
            await query.edit_message_text(
                mensaje,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown",
            )

    elif query.data == "join_waitlist":
        if user_id not in premium_data["waitlist"] and user_id not in premium_data["users"]:
            premium_data["waitlist"].append(user_id)
            save_premium_users(premium_data)
            pos = len(premium_data["waitlist"])
            mensaje = (
                f"📝 **Te has unido a la lista de espera**\n\n"
                f"Posición: {pos}\n\n"
                "Te avisaremos cuando haya una vacante premium."
            )
            await query.edit_message_text(mensaje, parse_mode="Markdown")

        else:
            mensaje = "✅ Ya estás en la lista de espera o eres premium."
            await query.edit_message_text(mensaje, parse_mode="Markdown")

    elif query.data == "back_start":
        keyboard = [
            [InlineKeyboardButton("📊 Ver Dólar", callback_data="dolar")],
            [InlineKeyboardButton("📰 Análisis Económico", callback_data="analisis")],
            [InlineKeyboardButton("⭐ Hacerse Premium", callback_data="premium")],
        ]
        mensaje = "🇨🇺 **DolarCubaAnalisisBot**\n\nElige una opción:"
        await query.edit_message_text(
            mensaje,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

# ========== MAIN ==========

def main():
    """Inicia el bot y configura los handlers."""
    # Inicia el servidor web para health check de Render
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
