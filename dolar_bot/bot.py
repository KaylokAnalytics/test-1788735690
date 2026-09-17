import requests
import logging
import json
import os
import re
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta
import pytz
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# ========== CONFIGURACIÓN ==========
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("❌ BOT_TOKEN no configurado")

# Canal de Telegram de elTOQUE (nuevo canal)
TELEGRAM_CHANNEL_URL = "https://t.me/s/eltoquecom2"

# Tasa oficial (fija, del BCC)
TASA_OFICIAL = 24

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ========== ZONA HORARIA CUBA ==========
HAVANA_TZ = pytz.timezone('America/Havana')

def get_cuba_time():
    return datetime.now(HAVANA_TZ)

# ========== EMOJIS ==========
E = {
    "dolar": "💵", "blue": "🇺🇸", "oficial": "🏛️", "euro": "🇪🇺", "mlc": "💳",
    "analisis": "📊", "premium": "⭐", "alerta": "⚠️", "check": "✅", "info": "ℹ️",
    "calendario": "📅", "tendencia": "📈", "ayuda": "🆘", "usuario": "👤",
    "dinero": "💰", "noticia": "📰", "recomendacion": "📌", "menu": "🏠",
    "fuente": "📡", "divisas": "💱", "hora": "🕐", "compartir": "📤",
    "rango": "📊", "telegram": "📱",
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

# ========== TECLADO ==========
def get_main_keyboard():
    keyboard = [
        [KeyboardButton(f"{E['dinero']} Dólar"), KeyboardButton(f"{E['divisas']} Todas las divisas")],
        [KeyboardButton(f"{E['analisis']} Análisis"), KeyboardButton(f"{E['premium']} Premium")],
        [KeyboardButton(f"{E['ayuda']} Ayuda"), KeyboardButton(f"{E['compartir']} Compartir")],
        [KeyboardButton(f"{E['menu']} Menú")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

# ========== CACHÉ ==========
CACHE_DURATION = 15  # minutos

dolar_cache = {"datos": None, "timestamp": None, "peticiones_hoy": 0, "ultima_peticion": None}

# ========== SCRAPING DEL CANAL DE TELEGRAM ==========
def _get_tasas_desde_telegram():
    """Extrae las tasas MÁS RECIENTES del canal de Telegram de elTOQUE."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
        }

        logger.info("🌐 Obteniendo tasas del canal de Telegram de elTOQUE...")
        response = requests.get(TELEGRAM_CHANNEL_URL, headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error(f"❌ Error al acceder al canal: {response.status_code}")
            return False, None

        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')

        if not messages:
            logger.warning("⚠️ No se encontraron mensajes en el canal")
            return False, None

        mensajes_con_tasas = []

        for msg in messages:
            texto = msg.get_text()
            fecha_match = re.search(r'Fecha[:\s]+(\d{2}/\d{2}/\d{4})', texto, re.IGNORECASE)
            usd_match = re.search(r'USD[:\s]+([\d,.]+)', texto, re.IGNORECASE)
            eur_match = re.search(r'EUR[:\s]+([\d,.]+)', texto, re.IGNORECASE)
            mlc_match = re.search(r'MLC[:\s]+([\d,.]+)', texto, re.IGNORECASE)

            if usd_match and fecha_match:
                fecha_str = fecha_match.group(1)
                try:
                    fecha_dt = datetime.strptime(fecha_str, '%d/%m/%Y')
                except:
                    continue

                usd_valor = float(usd_match.group(1).replace(',', ''))
                eur_valor = float(eur_match.group(1).replace(',', '')) if eur_match else None
                mlc_valor = float(mlc_match.group(1).replace(',', '')) if mlc_match else None

                if usd_valor > 100:
                    mensajes_con_tasas.append({
                        "fecha": fecha_dt,
                        "fecha_str": fecha_str,
                        "blue": usd_valor,
                        "eur": eur_valor,
                        "mlc": mlc_valor,
                    })

        if not mensajes_con_tasas:
            logger.warning("⚠️ No se encontraron mensajes con tasas y fecha válida")
            return False, None

        mensajes_con_tasas.sort(key=lambda x: x["fecha"], reverse=True)
        mas_reciente = mensajes_con_tasas[0]

        logger.info(f"✅ Tasas extraídas: {mas_reciente['fecha_str']} - USD={mas_reciente['blue']}, EUR={mas_reciente['eur']}, MLC={mas_reciente['mlc']}")

        data = {
            "blue": mas_reciente["blue"],
            "oficial": TASA_OFICIAL,
            "eur": mas_reciente["eur"],
            "mlc": mas_reciente["mlc"],
            "fecha_eltoque": mas_reciente["fecha_str"],
            "fuente": "Telegram @eltoquecom2"
        }
        return True, data

    except Exception as e:
        logger.warning(f"Error scraping Telegram: {e}")
        return False, None

def get_divisas():
    """Obtiene las divisas con caché."""
    global dolar_cache

    if dolar_cache["timestamp"] and (get_cuba_time() - dolar_cache["timestamp"]) < timedelta(minutes=CACHE_DURATION):
        logger.info("📦 Usando caché de divisas")
        return dolar_cache["datos"]

    success, data = _get_tasas_desde_telegram()

    if success and data:
        dolar_cache["datos"] = data
        dolar_cache["timestamp"] = get_cuba_time()
        dolar_cache["peticiones_hoy"] += 1
        dolar_cache["ultima_peticion"] = get_cuba_time()
        return data

    return None

def formatear_divisas(data):
    """Formatea los datos de divisas para mostrarlos."""
    fecha = get_cuba_time().strftime('%d/%m/%Y %I:%M %p')
    hora_actual = get_cuba_time().strftime('%I:%M %p')

    if data:
        mensaje = f"{E['divisas']} *DIVISAS EN CUBA*\n"
        mensaje += f"═══════════════════\n\n"
        mensaje += f"{E['calendario']} *Fecha:* {fecha}\n"
        mensaje += f"{E['hora']} *Hora:* {hora_actual}\n\n"

        if data.get('blue'):
            mensaje += f"{E['blue']} *USD Blue:* `{data['blue']:,.2f}` CUP\n"
        if data.get('oficial'):
            mensaje += f"{E['oficial']} *USD Oficial:* `{data['oficial']:,.2f}` CUP\n"
        if data.get('eur'):
            mensaje += f"{E['euro']} *EUR:* `{data['eur']:,.2f}` CUP\n"
        if data.get('mlc'):
            mensaje += f"{E['mlc']} *MLC:* `{data['mlc']:,.2f}` CUP\n"

        mensaje += f"\n───────────────────\n"
        mensaje += f"{E['fuente']} *Fuente:* elTOQUE.com\n"
        if data.get('fecha_eltoque'):
            mensaje += f"{E['telegram']} *Publicado:* {data['fecha_eltoque']}\n"
        mensaje += f"───────────────────\n"
        mensaje += f"_{'Datos del mercado cambiario cubano'}_"

        return mensaje
    else:
        mensaje = f"{E['divisas']} *DIVISAS EN CUBA*\n"
        mensaje += f"═══════════════════\n\n"
        mensaje += f"{E['calendario']} *Fecha:* {fecha}\n"
        mensaje += f"{E['hora']} *Hora:* {hora_actual}\n\n"
        mensaje += f"{E['blue']} *USD Blue:* `700.00` CUP\n"
        mensaje += f"{E['oficial']} *USD Oficial:* `24.00` CUP\n"
        mensaje += f"{E['euro']} *EUR:* `797.50` CUP\n"
        mensaje += f"{E['mlc']} *MLC:* `455.39` CUP\n\n"
        mensaje += f"───────────────────\n"
        mensaje += f"{E['fuente']} *Fuente:* elTOQUE.com (estimado)\n"
        mensaje += f"{E['alerta']} *Nota:* Datos estimados - Canal fuera de línea\n"
        mensaje += f"───────────────────\n"
        mensaje += f"_{'Datos de respaldo basados en tendencias del mercado'}_"

        return mensaje

# ========== MANEJADOR DE ERRORES ==========
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"❌ Error: {context.error}")

    mensaje = (
        f"{E['alerta']} *UPS! ALGO SALIÓ MAL*\n"
        f"═══════════════════\n\n"
        f"Lo sentimos, ha ocurrido un error inesperado. 😓\n\n"
        f"───────────────────\n"
        f"_¡Gracias por tu comprensión!_ 🙏"
    )

    if update and update.effective_chat:
        await update.effective_chat.send_message(
            mensaje,
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )

# ========== COMANDOS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action(action="typing")

    user = update.effective_user
    nombre = user.first_name or user.username or "Usuario"
    user_id = str(user.id)

    hora = get_cuba_time().hour
    if 6 <= hora < 12:
        saludo = "🌅 Buenos días"
    elif 12 <= hora < 18:
        saludo = "🌤️ Buenas tardes"
    else:
        saludo = "🌙 Buenas noches"

    premium_data = load_premium_users()
    is_premium = user_id in premium_data["users"]

    mensaje = (
        f"{saludo}, {nombre}! 👋\n"
        f"═══════════════════\n\n"
        f"{E['analisis']} *DolarCubaAnalisisBot*\n"
        f"Tu asistente económico 🇨🇺\n\n"
        f"{E['usuario']} *Estado:* {'⭐ Premium' if is_premium else '🟢 Gratuito'}\n"
        f"{E['divisas']} *Divisas:* USD (Blue/Oficial), EUR, MLC\n\n"
        f"Usa los botones del teclado 👇"
    )

    await update.message.reply_text(
        mensaje,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown",
    )

async def handle_dolar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action(action="typing")

    try:
        divisas_data = get_divisas()

        if divisas_data:
            blue = divisas_data.get('blue')
            oficial = divisas_data.get('oficial')
            fecha = get_cuba_time().strftime('%d/%m/%Y %I:%M %p')

            mensaje = f"{E['dolar']} *DÓLAR EN CUBA*\n"
            mensaje += f"═══════════════════\n\n"
            if blue:
                mensaje += f"{E['blue']} *Blue:* `{blue:,.2f}` CUP\n"
            if oficial:
                mensaje += f"{E['oficial']} *Oficial:* `{oficial:,.2f}` CUP\n"
            mensaje += f"\n{E['calendario']} *Fecha:* {fecha}\n"
            if divisas_data.get('fecha_eltoque'):
                mensaje += f"{E['telegram']} *Publicado:* {divisas_data['fecha_eltoque']}\n"
            mensaje += f"───────────────────\n"
            mensaje += f"{E['fuente']} *Fuente:* elTOQUE.com\n"
            mensaje += f"───────────────────\n"
            mensaje += f"_{'Datos del mercado cambiario cubano'}_"
        else:
            mensaje = (
                f"{E['dolar']} *DÓLAR EN CUBA*\n"
                f"═══════════════════\n\n"
                f"{E['blue']} *Blue:* `700.00` CUP\n"
                f"{E['oficial']} *Oficial:* `24.00` CUP\n\n"
                f"{E['fuente']} *Fuente:* elTOQUE.com (estimado)\n"
                f"{E['alerta']} *Nota:* Datos estimados por fallo de fuente"
            )

        await update.message.reply_text(
            mensaje,
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Error en handle_dolar: {e}")
        await update.message.reply_text(
            f"{E['alerta']} *ERROR AL OBTENER DATOS*\n\nNo pudimos obtener el precio del dólar. 😓\n\n_Intenta de nuevo en unos minutos._",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )

async def handle_divisas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action(action="typing")

    try:
        divisas_data = get_divisas()
        mensaje = formatear_divisas(divisas_data)

        await update.message.reply_text(
            mensaje,
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Error en handle_divisas: {e}")
        await update.message.reply_text(
            f"{E['alerta']} *Error al obtener divisas*\n\nIntenta de nuevo en unos minutos.",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )

async def handle_analisis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action(action="typing")

    fecha = get_cuba_time().strftime('%d/%m/%Y %I:%M %p')
    mensaje = (
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
        f"{E['fuente']} *Fuente:* elTOQUE.com\n"
        f"───────────────────\n"
        f"_{'Estimación basada en datos disponibles'}_"
    )
    await update.message.reply_text(
        mensaje,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown",
    )

async def handle_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action(action="typing")

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
    elif is_waitlist:
        pos = premium_data["waitlist"].index(user_id) + 1
        mensaje = (
            f"{E['info']} *LISTA DE ESPERA*\n"
            f"═══════════════════\n\n"
            f"{nombre}, estás en la posición: *{pos}*\n\n"
            f"{E['alerta']} *Te avisaremos cuando haya cupo*"
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
            f"¿Te unes a la lista de espera?\n"
            f"Usa el comando /unirse"
        )

    await update.message.reply_text(
        mensaje,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown",
    )

async def handle_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action(action="typing")

    user = update.effective_user
    nombre = user.first_name or user.username or "Usuario"

    mensaje = (
        f"{E['ayuda']} *AYUDA PARA {nombre.upper()}*\n"
        f"═══════════════════\n\n"
        f"*Comandos disponibles:*\n"
        f"/start - Menú principal\n"
        f"/dolar - Precio del dólar\n"
        f"/divisas - Todas las divisas\n"
        f"/analisis - Análisis económico\n"
        f"/premium - Info de suscripción\n"
        f"/unirse - Unirse a lista premium\n"
        f"/compartir - Compartir el bot\n"
        f"/ayuda - Este mensaje\n\n"
        f"───────────────────\n"
        f"{E['fuente']} *Fuente de datos:* elTOQUE.com\n"
        f"───────────────────\n"
        f"_{'Creado para la comunidad cubana 🇨🇺'}_"
    )
    await update.message.reply_text(
        mensaje,
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown",
    )

async def handle_compartir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action(action="typing")

    keyboard = [
        [InlineKeyboardButton("📤 Compartir en Telegram", url="https://t.me/share/url?url=https://t.me/DolarCubaAnalisisBot")],
        [InlineKeyboardButton("📋 Copiar enlace", callback_data="copiar_enlace")],
    ]

    mensaje = (
        f"{E['compartir']} *COMPARTE EL BOT*\n"
        f"═══════════════════\n\n"
        f"¡Ayuda a más personas a conocer el bot!\n\n"
        f"{E['info']} *Link del bot:*\n"
        f"`https://t.me/DolarCubaAnalisisBot`\n\n"
        f"───────────────────\n"
        f"_{'¡Gracias por ayudar a crecer la comunidad!'}_ 🙏"
    )

    await update.message.reply_text(
        mensaje,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

# ========== CALLBACKS ==========
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "copiar_enlace":
        mensaje = (
            f"📋 *COPIA EL ENLACE*\n"
            f"═══════════════════\n\n"
            f"`https://t.me/DolarCubaAnalisisBot`\n\n"
            f"Selecciona el texto y cópialo 📋"
        )
        await query.edit_message_text(mensaje, parse_mode="Markdown")

# ========== COMANDOS DE TEXTO ==========
async def dolar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_dolar(update, context)

async def divisas_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_divisas(update, context)

async def analisis_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_analisis(update, context)

async def premium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_premium(update, context)

async def ayuda_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_ayuda(update, context)

async def compartir_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_compartir(update, context)

async def unirse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action(action="typing")

    user = update.effective_user
    nombre = user.first_name or user.username or "Usuario"
    user_id = str(user.id)
    premium_data = load_premium_users()

    if user_id in premium_data["users"]:
        mensaje = (
            f"{E['premium']} *YA ERES PREMIUM*\n"
            f"═══════════════════\n\n"
            f"¡Ya eres usuario Premium, {nombre}! ⭐\n\n"
            f"Gracias por tu apoyo. 🙏"
        )
    elif user_id in premium_data["waitlist"]:
        pos = premium_data["waitlist"].index(user_id) + 1
        mensaje = (
            f"{E['info']} *YA ESTÁS EN LA LISTA*\n"
            f"═══════════════════\n\n"
            f"{nombre}, estás en la posición: *{pos}*\n\n"
            f"{E['alerta']} *Te avisaremos cuando haya cupo*"
        )
    else:
        premium_data["waitlist"].append(user_id)
        save_premium_users(premium_data)
        mensaje = (
            f"{E['check']} *¡UNIDO CON ÉXITO!*\n"
            f"═══════════════════\n\n"
            f"¡Bienvenido a la lista de espera, {nombre}! 🎉\n\n"
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

    logger.info("✅ Bot configurado para usar scraping de Telegram (@eltoquecom2)")
    logger.info(f"⏱️ Caché configurado a {CACHE_DURATION} minutos")

    app = Application.builder().token(TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dolar", dolar_command))
    app.add_handler(CommandHandler("divisas", divisas_command))
    app.add_handler(CommandHandler("analisis", analisis_command))
    app.add_handler(CommandHandler("premium", premium_command))
    app.add_handler(CommandHandler("ayuda", ayuda_command))
    app.add_handler(CommandHandler("compartir", compartir_command))
    app.add_handler(CommandHandler("unirse", unirse_command))

    # Botones del teclado
    app.add_handler(MessageHandler(filters.Regex(f"^{E['dinero']} Dólar$"), handle_dolar))
    app.add_handler(MessageHandler(filters.Regex(f"^{E['divisas']} Todas las divisas$"), handle_divisas))
    app.add_handler(MessageHandler(filters.Regex(f"^{E['analisis']} Análisis$"), handle_analisis))
    app.add_handler(MessageHandler(filters.Regex(f"^{E['premium']} Premium$"), handle_premium))
    app.add_handler(MessageHandler(filters.Regex(f"^{E['ayuda']} Ayuda$"), handle_ayuda))
    app.add_handler(MessageHandler(filters.Regex(f"^{E['compartir']} Compartir$"), handle_compartir))
    app.add_handler(MessageHandler(filters.Regex(f"^{E['menu']} Menú$"), handle_menu))

    # Callbacks
    app.add_handler(CallbackQueryHandler(button_callback))

    # Errores
    app.add_error_handler(error_handler)

    logger.info("🤖 Bot DolarCubaAnalisisBot iniciado correctamente")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
