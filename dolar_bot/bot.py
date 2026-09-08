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
# 🔒 TOKEN desde variable de entorno (SEGURO)
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ Error: BOT_TOKEN no está configurado en las variables de entorno de Render")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ========== SERVIDOR WEB PARA HEALTH CHECK ==========
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

    def log_message(self, format, *args):
        return

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info(f"✅ Servidor de health check corriendo en puerto {port}")

# ========== ARCHIVO DE USUARIOS PREMIUM ==========
PREMIUM_USERS_FILE = "premium_users.json"

def load_premium_users():
    try:
        with open(PREMIUM_USERS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": [], "waitlist": []}

def save_premium_users(data):
    with open(PREMIUM_USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ========== SISTEMA DE CÁCACHE DÓLAR ==========
dolar_cache = {"precio": None, "timestamp": None}

def _get_dolar_eltoque():
    try:
        url = "https://api.eltoque.com/v1/dolar"
        response = requests.get(url, timeout=30)
        data = response.json()
        return True, data.get('blue'), data.get('oficial')
    except Exception as e:
        logger.warning(f"elTOQUE API error: {e}")
        return False, None, None

def get_dolar():
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
    else:
        mensaje = (
            f"💵 **Dólar en Cuba**\n\n"
            f"🇨🇺 **Oficial (tasa BCC):** 24 CUP\n"
            f"💎 **Blue/Informal:** 660 CUP\n"
            f"📅 Consultado: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
            f"⚠️ *Datos estimados - API elTOQUE fuera de línea*"
        )
    
    dolar_cache["precio"] = mensaje
    dolar_cache["timestamp"] = datetime.now()
    return mensaje

def get_analisis_economico():
    return (
        "📊 **Análisis Económico de Cuba**\n\n"
        "🔹 **Tendencias actuales del mercado:**\n"
        "• El dólar muestra volatilidad en el mercado informal.\n"
        "• Presión inflacionaria por escasez de divisas.\n"
        "• Impacto de las sanciones internacionales.\n\n"
        "📰 **Noticias destacadas:**\n"
        "• Actualizaciones sobre políticas monetarias.\n"
        "• Informes de organismos internacionales.\n\n"
        "💡 *Estimación basada en datos disponibles.*"
    )

# ========== COMANDOS DEL BOT ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    premium_data = load_premium_users()
    is_premium = user_id in premium_data["users"]

    keyboard = [
        [InlineKeyboardButton("📊 Ver Dólar", callback_data="dolar")],
        [InlineKeyboardButton("📰 Análisis Económico", callback_data="analisis")],
        [InlineKeyboardButton("⭐ Hacerse Premium", callback_data="premium")],
    ]

    mensaje = (
        f"🇨🇺 **Bienvenido a DolarCubaAnalisisBot**\n\n"
        f"📊 Tu asistente económico para Cuba.\n"
        f"🔹 **Estado:** {'⭐ Premium' if is_premium else '🟢 Gratuito'}\n\n"
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
    await update.message.reply_text(get_dolar(), parse_mode="Markdown")

async def analisis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_analisis_economico(), parse_mode="Markdown")

async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    premium_data = load_premium_users()
    is_premium = user_id in premium_data["users"]
    is_waitlist = user_id in premium_data["waitlist"]

    if is_premium:
        mensaje = "⭐ **Ya eres usuario Premium**\n\nGracias por confiar en nosotros."
        await update.message.reply_text(mensaje, parse_mode="Markdown")
    elif is_waitlist:
        pos = premium_data["waitlist"].index(user_id) + 1
        mensaje = f"📝 **Estás en la lista de espera**\n\nPosición: {pos}"
        await update.message.reply_text(mensaje, parse_mode="Markdown")
    else:
        keyboard = [
            [InlineKeyboardButton("📝 Unirse a lista de espera", callback_data="join_waitlist")],
        ]
        mensaje = (
            "⭐ **Plan Premium**\n\n"
            "Precio: **500 CUP/mes**\n\n"
            "Beneficios premium:\n"
            "✅ Alertas personalizadas del dólar\n"
            "✅ Análisis detallado con IA\n"
            f"Cupos disponibles: **{500 - len(premium_data['users'])} / 500**\n\n"
            "¿Te unes a la lista de espera?"
        )
        await update.message.reply_text(
            mensaje,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = (
        "🇨🇺 **Ayuda de DolarCubaAnalisisBot**\n\n"
        "Comandos disponibles:\n"
        "/start - Menú principal\n"
        "/dolar - Precio del dólar\n"
        "/analisis - Análisis económico\n"
        "/premium - Info de suscripción\n"
        "/ayuda - Este mensaje\n\n"
        "Creado con 🇨🇺 para la comunidad cubana."
    )
    await update.message.reply_text(mensaje, parse_mode="Markdown")

# ========== CALLBACKS ==========
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            await query.edit_message_text("⭐ **Ya eres usuario Premium**", parse_mode="Markdown")
        elif is_waitlist:
            pos = premium_data["waitlist"].index(user_id) + 1
            await query.edit_message_text(f"📝 **Lista de espera**\n\nPosición: {pos}", parse_mode="Markdown")
        else:
            keyboard = [
                [InlineKeyboardButton("📝 Unirse a lista de espera", callback_data="join_waitlist")],
                [InlineKeyboardButton("🔙 Volver", callback_data="back_start")],
            ]
            mensaje = (
                "⭐ **Plan Premium**\n\n"
                f"Cupos: **{500 - len(premium_data['users'])} / 500**"
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
            await query.edit_message_text(
                f"📝 **Unido a lista de espera**\n\nPosición: {len(premium_data['waitlist'])}",
                parse_mode="Markdown"
            )
    elif query.data == "back_start":
        keyboard = [
            [InlineKeyboardButton("📊 Ver Dólar", callback_data="dolar")],
            [InlineKeyboardButton("📰 Análisis Económico", callback_data="analisis")],
            [InlineKeyboardButton("⭐ Hacerse Premium", callback_data="premium")],
        ]
        await query.edit_message_text(
            "🇨🇺 **DolarCubaAnalisisBot**\n\nElige una opción:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

# ========== MAIN ==========
def main():
    run_health_server()
    
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dolar", dolar))
    app.add_handler(CommandHandler("analisis", analisis))
    app.add_handler(CommandHandler("premium", premium))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(CallbackQueryHandler(button_callback))

    logger.info("🤖 Bot DolarCubaAnalisisBot iniciado correctamente")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
