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
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN no configurado")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ========== EMOJIS TEMÁTICOS ==========
E = {
    "dolar": "💵",
    "blue": "🇺🇸",
    "oficial": "🏛️",
    "analisis": "📊",
    "premium": "⭐",
    "alerta": "⚠️",
    "check": "✅",
    "info": "ℹ️",
    "calendario": "📅",
    "tendencia": "📈",
    "ayuda": "🆘",
    "volver": "🔙",
    "usuario": "👤",
    "dinero": "💰",
    "grafico": "📈",
    "noticia": "📰",
    "recomendacion": "📌",
}

# ========== SERVIDOR WEB ==========
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
    logger.info(f"✅ Health check en puerto {port}")

# ========== USUARIOS PREMIUM ==========
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

# ========== DÓLAR ==========
dolar_cache = {"precio": None, "timestamp": None}

def _get_dolar_eltoque():
    try:
        url = "https://api.eltoque.com/v1/dolar"
        response = requests.get(url, timeout=30)
        data = response.json()
        return True, data.get('blue'), data.get('oficial')
    except Exception as e:
        logger.warning(f"elTOQUE error: {e}")
        return False, None, None

def get_dolar():
    global dolar_cache
    if dolar_cache["timestamp"] and datetime.now() - dolar_cache["timestamp"] < timedelta(minutes=5):
        return dolar_cache["precio"]

    success, blue, oficial = _get_dolar_eltoque()
    fecha = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    if success and blue is not None and oficial is not None:
        mensaje = (
            f"{E['dolar']} *DÓLAR EN CUBA*\n"
            f"═══════════════════\n\n"
            f"{E['blue']} *Blue:* `{blue}` CUP\n"
            f"{E['oficial']} *Oficial:* `{oficial}` CUP\n"
            f"{E['calendario']} *Fecha:* {fecha}\n\n"
            f"───────────────────\n"
            f"{E['alerta']} *Precio aproximado*\n"
            f"───────────────────\n"
            f"_{'Datos de elTOQUE'}_"
        )
    else:
        mensaje = (
            f"{E['dolar']} *DÓLAR EN CUBA*\n"
            f"═══════════════════\n\n"
            f"{E['blue']} *Blue:* `660` CUP\n"
            f"{E['oficial']} *Oficial:* `24` CUP\n"
            f"{E['calendario']} *Fecha:* {fecha}\n\n"
            f"───────────────────\n"
            f"{E['alerta']} *Datos estimados*\n"
            f"───────────────────\n"
            f"_API elTOQUE fuera de línea_"
        )
    
    dolar_cache["precio"] = mensaje
    dolar_cache["timestamp"] = datetime.now()
    return mensaje

def get_analisis_economico():
    return (
        f"{E['analisis']} *ANÁLISIS ECONÓMICO*\n"
        f"═══════════════════\n\n"
        f"{E['tendencia']} *Tendencias:*\n"
        f"• Dólar volátil en mercado informal\n"
        f"• Presión inflacionaria\n"
        f"• Impacto de sanciones\n\n"
        f"{E['noticia']} *Noticias:*\n"
        f"• Políticas monetarias en revisión\n"
        f"• Informes internacionales\n\n"
        f"───────────────────\n"
        f"{E['recomendacion']} *Recomendación:*\n"
        f"_Monitorea el precio regularmente_\n"
        f"───────────────────\n"
        f"_Estimación basada en datos disponibles_"
    )

# ========== COMANDOS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    premium_data = load_premium_users()
    is_premium = user_id in premium_data["users"]

    keyboard = [
        [InlineKeyboardButton(f"{E['dinero']} Dólar", callback_data="dolar"),
         InlineKeyboardButton(f"{E['analisis']} Análisis", callback_data="analisis")],
        [InlineKeyboardButton(f"{E['premium']} Premium", callback_data="premium"),
         InlineKeyboardButton(f"{E['ayuda']} Ayuda", callback_data="ayuda")],
    ]

    mensaje = (
        f"{E['usuario']} *BIENVENIDO*\n"
        f"═══════════════════\n\n"
        f"{E['analisis']} *DolarCubaAnalisisBot*\n"
        f"Tu asistente económico 🇨🇺\n\n"
        f"{E['usuario']} *Estado:* {'⭐ Premium' if is_premium else '🟢 Gratuito'}\n\n"
        f"Elige una opción 👇"
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
        mensaje = (
            f"{E['premium']} *USUARIO PREMIUM*\n"
            f"═══════════════════\n\n"
            f"¡Gracias por tu apoyo! 🎉\n\n"
            f"{E['check']} Beneficios activos:\n"
            f"• Alertas en tiempo real\n"
            f"• Análisis detallado\n"
            f"• Soporte prioritario"
        )
        await update.message.reply_text(mensaje, parse_mode="Markdown")
    elif is_waitlist:
        pos = premium_data["waitlist"].index(user_id) + 1
        mensaje = (
            f"{E['info']} *LISTA DE ESPERA*\n"
            f"═══════════════════\n\n"
            f"Posición: *{pos}*\n\n"
            f"{E['alerta']} *Te avisaremos cuando haya cupo*"
        )
        await update.message.reply_text(mensaje, parse_mode="Markdown")
    else:
        keyboard = [
            [InlineKeyboardButton(f"{E['premium']} Unirse a lista", callback_data="join_waitlist")],
        ]
        mensaje = (
            f"{E['premium']} *PLAN PREMIUM*\n"
            f"═══════════════════\n\n"
            f"{E['dinero']} *Precio:* 500 CUP/mes\n\n"
            f"{E['check']} *Beneficios:*\n"
            f"• Alertas personalizadas\n"
            f"• Análisis con IA\n"
            f"• Reportes exclusivos\n\n"
            f"Cupos: *{500 - len(premium_data['users'])} / 500*\n\n"
            f"¿Te unes a la lista de espera?"
        )
        await update.message.reply_text(
            mensaje,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = (
        f"{E['ayuda']} *AYUDA*\n"
        f"═══════════════════\n\n"
        f"*Comandos disponibles:*\n"
        f"/start - Menú principal\n"
        f"/dolar - Precio del dólar\n"
        f"/analisis - Análisis económico\n"
        f"/premium - Info de suscripción\n"
        f"/ayuda - Este mensaje\n\n"
        f"───────────────────\n"
        f"_{'Creado para la comunidad cubana 🇨🇺'}_"
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
            mensaje = (
                f"{E['premium']} *PREMIUM*\n"
                f"═══════════════════\n\n"
                f"¡Ya eres usuario Premium! 🎉"
            )
            await query.edit_message_text(mensaje, parse_mode="Markdown")
        elif is_waitlist:
            pos = premium_data["waitlist"].index(user_id) + 1
            mensaje = (
                f"{E['info']} *LISTA DE ESPERA*\n"
                f"═══════════════════\n\n"
                f"Posición: *{pos}*"
            )
            await query.edit_message_text(mensaje, parse_mode="Markdown")
        else:
            keyboard = [
                [InlineKeyboardButton(f"{E['premium']} Unirse", callback_data="join_waitlist")],
                [InlineKeyboardButton(f"{E['volver']} Volver", callback_data="back_start")],
            ]
            mensaje = (
                f"{E['premium']} *PLAN PREMIUM*\n"
                f"═══════════════════\n\n"
                f"Cupos: *{500 - len(premium_data['users'])} / 500*\n\n"
                f"¿Te unes a la lista de espera?"
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
            mensaje = (
                f"{E['check']} *¡UNIDO CON ÉXITO!*\n"
                f"═══════════════════\n\n"
                f"Posición: *{len(premium_data['waitlist'])}*\n\n"
                f"{E['alerta']} *Te avisaremos cuando haya cupo*"
            )
            await query.edit_message_text(mensaje, parse_mode="Markdown")
        else:
            mensaje = f"{E['info']} *Ya estás en la lista*"
            await query.edit_message_text(mensaje, parse_mode="Markdown")
    
    elif query.data == "ayuda":
        mensaje = (
            f"{E['ayuda']} *AYUDA*\n"
            f"═══════════════════\n\n"
            f"*Comandos:*\n"
            f"/start - Menú\n"
            f"/dolar - Precio\n"
            f"/analisis - Análisis\n"
            f"/premium - Suscripción\n\n"
            f"_{'Creado para la comunidad cubana 🇨🇺'}_"
        )
        await query.edit_message_text(mensaje, parse_mode="Markdown")
    
    elif query.data == "back_start":
        keyboard = [
            [InlineKeyboardButton(f"{E['dinero']} Dólar", callback_data="dolar"),
             InlineKeyboardButton(f"{E['analisis']} Análisis", callback_data="analisis")],
            [InlineKeyboardButton(f"{E['premium']} Premium", callback_data="premium"),
             InlineKeyboardButton(f"{E['ayuda']} Ayuda", callback_data="ayuda")],
        ]
        mensaje = (
            f"{E['usuario']} *BIENVENIDO*\n"
            f"═══════════════════\n\n"
            f"Elige una opción 👇"
        )
        await query.edit_message_text(
            mensaje,
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
