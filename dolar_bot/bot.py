import requests
import logging
import json
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta
import pytz  # 👈 NUEVO: Para zona horaria de Cuba
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
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

# ========== ZONA HORARIA CUBA ==========
HAVANA_TZ = pytz.timezone('America/Havana')

def get_cuba_time():
    """Devuelve la fecha y hora actual en Cuba."""
    return datetime.now(HAVANA_TZ)

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
    "atras": "⬅️",
    "menu": "🏠",
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

# ========== TECLADO PRINCIPAL (en el teclado, no en el chat) ==========
def get_main_keyboard():
    """Teclado que aparece en la parte inferior del chat."""
    keyboard = [
        [KeyboardButton(f"{E['dinero']} Dólar"), KeyboardButton(f"{E['analisis']} Análisis")],
        [KeyboardButton(f"{E['premium']} Premium"), KeyboardButton(f"{E['ayuda']} Ayuda")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

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
    # 👈 FECHA EN HORARIO DE CUBA
    fecha = get_cuba_time().strftime('%d/%m/%Y %I:%M %p')
    
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
    fecha = get_cuba_time().strftime('%d/%m/%Y %I:%M %p')
    return (
        f"{E['analisis']} *ANÁLISIS ECONÓMICO*\n"
        f"═══════════════════\n\n"
        f"{E['calendario']} *Fecha:* {fecha}\n\n"
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
    """Comando /start - Muestra el menú principal."""
    user = update.effective_user
    # 👈 NOMBRE DE USUARIO
    nombre = user.first_name or user.username or "Usuario"
    user_id = str(user.id)
    
    premium_data = load_premium_users()
    is_premium = user_id in premium_data["users"]

    mensaje = (
        f"{E['usuario']} *BIENVENIDO, {nombre.upper()}!*\n"
        f"═══════════════════\n\n"
        f"{E['analisis']} *DolarCubaAnalisisBot*\n"
        f"Tu asistente económico 🇨🇺\n\n"
        f"{E['usuario']} *Estado:* {'⭐ Premium' if is_premium else '🟢 Gratuito'}\n\n"
        f"Usa los botones del teclado 👇"
    )

    await update.message.reply_text(
        mensaje,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown",
    )

async def handle_dolar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el botón Dólar."""
    await update.message.reply_text(
        get_dolar(),
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown",
    )

async def handle_analisis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el botón Análisis."""
    await update.message.reply_text(
        get_analisis_economico(),
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown",
    )

async def handle_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el botón Premium."""
    user = update.effective_user
    nombre = user.first_name or user.username or "Usuario"
    user_id = str(user.id)
    premium_data = load_premium_users()
    is_premium = user_id in premium_data["users"]
    is_waitlist = user_id in premium_data["waitlist"]

    if is_premium:
        mensaje = (
            f"{E['premium']} *USUARIO PREMIUM*\n"
            f"═══════════════════\n\n"
            f"¡Gracias por tu apoyo, {nombre}! 🎉\n\n"
            f"{E['check']} Beneficios activos:\n"
            f"• Alertas en tiempo real\n"
            f"• Análisis detallado\n"
            f"• Soporte prioritario"
        )
        await update.message.reply_text(
            mensaje,
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown",
        )
    elif is_waitlist:
        pos = premium_data["waitlist"].index(user_id) + 1
        mensaje = (
            f"{E['info']} *LISTA DE ESPERA*\n"
            f"═══════════════════\n\n"
            f"{nombre}, estás en la posición: *{pos}*\n\n"
            f"{E['alerta']} *Te avisaremos cuando haya cupo*"
        )
        await update.message.reply_text(
            mensaje,
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown",
        )
    else:
        mensaje = (
            f"{E['premium']} *PLAN PREMIUM*\n"
            f"═══════════════════\n\n"
            f"{E['dinero']} *Precio:* 500 CUP/mes\n\n"
            f"{E['check']} *Beneficios:*\n"
            f"• Alertas personalizadas\n"
            f"• Análisis con IA\n"
            f"• Reportes exclusivos\n\n"
            f"Cupos: *{500 - len(premium_data['users'])} / 500*\n\n"
            f"¿Te unes a la lista de espera?\n"
            f"Usa el comando /unirse"
        )
        await update.message.reply_text(
            mensaje,
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown",
        )

async def handle_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el botón Ayuda."""
    user = update.effective_user
    nombre = user.first_name or user.username or "Usuario"
    
    mensaje = (
        f"{E['ayuda']} *AYUDA PARA {nombre.upper()}*\n"
        f"═══════════════════\n\n"
        f"*Comandos disponibles:*\n"
        f"/start - Menú principal\n"
        f"/dolar - Precio del dólar\n"
        f"/analisis - Análisis económico\n"
        f"/premium - Info de suscripción\n"
        f"/unirse - Unirse a lista premium\n"
        f"/ayuda - Este mensaje\n\n"
        f"───────────────────\n"
        f"_{'Creado para la comunidad cubana 🇨🇺'}_"
    )
    await update.message.reply_text(
        mensaje,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown",
    )

async def dolar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /dolar"""
    await update.message.reply_text(
        get_dolar(),
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown",
    )

async def analisis_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /analisis"""
    await update.message.reply_text(
        get_analisis_economico(),
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown",
    )

async def premium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /premium"""
    await handle_premium(update, context)

async def ayuda_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /ayuda"""
    await handle_ayuda(update, context)

async def unirse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /unirse - Unirse a la lista de espera premium."""
    user = update.effective_user
    nombre = user.first_name or user.username or "Usuario"
    user_id = str(user.id)
    premium_data = load_premium_users()

    if user_id in premium_data["users"]:
        mensaje = f"{E['premium']} ¡Ya eres usuario Premium, {nombre}! ⭐"
        await update.message.reply_text(
            mensaje,
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown",
        )
        return

    if user_id in premium_data["waitlist"]:
        pos = premium_data["waitlist"].index(user_id) + 1
        mensaje = (
            f"{E['info']} *YA ESTÁS EN LA LISTA*\n"
            f"═══════════════════\n\n"
            f"{nombre}, posición: *{pos}*"
        )
        await update.message.reply_text(
            mensaje,
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown",
        )
        return

    premium_data["waitlist"].append(user_id)
    save_premium_users(premium_data)
    
    mensaje = (
        f"{E['check']} *¡UNIDO CON ÉXITO, {nombre.upper()}!*\n"
        f"═══════════════════\n\n"
        f"Posición: *{len(premium_data['waitlist'])}*\n\n"
        f"{E['alerta']} *Te avisaremos cuando haya cupo*"
    )
    await update.message.reply_text(
        mensaje,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown",
    )

# ========== MAIN ==========
def main():
    run_health_server()
    
    app = Application.builder().token(TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dolar", dolar_command))
    app.add_handler(CommandHandler("analisis", analisis_command))
    app.add_handler(CommandHandler("premium", premium_command))
    app.add_handler(CommandHandler("ayuda", ayuda_command))
    app.add_handler(CommandHandler("unirse", unirse_command))

    # Manejadores de texto para botones del teclado
    # (Los botones del teclado envían texto, no callback_data)
    from telegram.ext import MessageHandler, filters
    app.add_handler(MessageHandler(filters.Regex(f"^{E['dinero']} Dólar$"), handle_dolar))
    app.add_handler(MessageHandler(filters.Regex(f"^{E['analisis']} Análisis$"), handle_analisis))
    app.add_handler(MessageHandler(filters.Regex(f"^{E['premium']} Premium$"), handle_premium))
    app.add_handler(MessageHandler(filters.Regex(f"^{E['ayuda']} Ayuda$"), handle_ayuda))

    logger.info("🤖 Bot DolarCubaAnalisisBot iniciado correctamente")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
