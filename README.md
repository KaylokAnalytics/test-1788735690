# DolarCubaAnalisisBot
Bot de Telegram para obtener el precio del dólar en Cuba y análisis económico.

## Token del Bot
`8768535605:AAEgwIdXp0Jnnxrf8K4wZKOXSbsNfrr4C3M`

## Requisitos Previos
- Python 3.12 o superior
- Acceso a internet para consultar la API elTOQUE

## Instalación de Dependencias

1. Clona este repositorio o copia los archivos:
```bash
git clone <tu-directorio>
cd test-1788735690
```

2. Crea un entorno virtual (recomendado):
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Ejecutar el Bot Localmente

1. Asegúrate de estar en el directorio correcto:
```bash
cd /workspaces/test-1788735690
```

2. Ejecuta el bot:
```bash
python bot.py
```

3. El bot comenzará a escuchar actualizaciones de Telegram. Verás en consola:
```
🤖 Bot DolarCubaAnalisisBot iniciado correctamente
```

4. ¡Listo! Interactúa con el bot en Telegram usando los comandos:
   - `/start` - Bienvenida y menú principal
   - `/dolar` - Precio del dólar
   - `/analisis` - Análisis económico
   - `/premium` - Info de suscripción premium
   - `/ayuda` - Ver comandos

## Despliegue en Render (Gratis)

1. Crea una cuenta en [Render](https://render.com) (gratis).

2. Conecta tu repositorio:
   - Ve a "New Web Service" 
   - Conecta tu repositorio de GitHub o GitLab
   - El repositorio es: `KaylokAnalytics/test-1788735690`

3. Configura el servicio:
   - **Name**: `dolar-cuba-analisis-bot`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Python Version**: `3.12` (si se pregunta)

4. Variables de entorno (opcional, si quieres cambiar el token):
   - `TOKEN`: `8768535605:AAEgwIdXp0Jnnxrf8K4wZKOXSbsNfrr4C3M`

5. Haz clic en "Create Web Service". Render iniciará el despliegue automáticamente.

6. Una vez finalizado, obtendrás una URL pública tipo `https://dolar-cuba-analisis-bot.onrender.com`

7. El bot se reiniciará automáticamente si hay cambios o después de cierto período (plan gratuito).

## Estructura de Archivos (raíz del repositorio)

```
test-1788735690/
├── bot.py              # Código principal del bot
├── requirements.txt    # Dependencias Python
├── premium_users.json  # Archivo generado automáticamente (usuarios premium)
├── venv/              # Entorno virtual (ignorar en git)
├── ajedrez/           # Directorio de ajedrez
├── Repertorio-Ajedrez.pdf
└── repertorio-ajedrez.zip
```

## Funcionalidades Principales

### Comandos
- `/start` - Menú principal con botones interactivos
- `/dolar` - Precio del dólar (usando caché de 5 min)
- `/analisis` - Análisis económico de Cuba
- `/premium` - Estado de suscripción premium
- `/ayuda` - Ayuda y comandos disponibles

### Sistema Premium
- Máximo 500 usuarios premium
- Precio: 500 CUP/mes
- Almacenamiento en `premium_users.json`
- Lista de espera ilimitada hasta llenar los 500 cupos

### Botones Inline
- Menú principal: Ver Dólar, Análisis Económico, Hacerse Premium
- Sección premium: Unirse a lista de espera, Volver al menú