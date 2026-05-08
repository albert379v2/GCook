import asyncio
import logging
import os
import time
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configurar logging para DisCloud
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Configuración
BOT_TOKEN = os.getenv("BOT_TOKEN", "8323089139:AAGMHTiXoiL5yAOaC1AMhz0qSD_W67jG_wk")
CREDENTIALS_FILE = "user_credentials.json"

def load_user_credentials():
    """Carga las credenciales de usuarios desde archivo"""
    try:
        if os.path.exists(CREDENTIALS_FILE):
            with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error cargando credenciales: {e}")
        return {}

def save_user_credentials(user_id, email, password):
    """Guarda las credenciales de un usuario"""
    try:
        credentials = load_user_credentials()
        credentials[str(user_id)] = {
            'email': email,
            'password': password,
            'timestamp': time.time()
        }
        with open(CREDENTIALS_FILE, 'w', encoding='utf-8') as f:
            json.dump(credentials, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error guardando credenciales: {e}")
        return False

def get_user_credentials(user_id):
    """Obtiene las credenciales de un usuario"""
    credentials = load_user_credentials()
    return credentials.get(str(user_id))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /start"""
    welcome_text = (
        "🤖 **Bot de Cookies Amazon - VikingCookies** 🍪\n\n"
        "🔐 *Autenticación personalizada por usuario*\n\n"
        "**Comandos disponibles:**\n"
        "/acc email@ejemplo.com contraseña - Configurar tu cuenta Amazon\n"
        "/gencookie - Generar cookies con flujo completo\n"
        "/micuenta - Ver tu cuenta configurada\n"
        "/help - Mostrar ayuda\n"
        "/status - Estado del bot\n\n"
        "**Ejemplo:**\n"
        "`/acc usuario@gmail.com micontraseña123`"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def acc_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /acc para configurar credenciales"""
    try:
        user_id = update.message.from_user.id
        user_name = update.message.from_user.first_name
        message_text = update.message.text
        
        logger.info(f"Usuario {user_id} ({user_name}) ejecutó /acc")
        
        # Verificar si el mensaje tiene suficiente longitud
        if len(message_text.strip()) < 10:
            await update.message.reply_text(
                "❌ **Formato incorrecto**\n\n"
                "**Uso correcto:**\n"
                "`/acc email@ejemplo.com contraseña`\n\n"
                "**Ejemplos:**\n"
                "`/acc usuario@gmail.com contraseña123`\n"
                "`/acc usuario@hotmail.com mi.contraseña`",
                parse_mode='Markdown'
            )
            return
        
        # Dividir el mensaje en partes
        parts = message_text.split()
        
        # El formato debe ser: /acc email contraseña
        if len(parts) < 3:
            await update.message.reply_text(
                "❌ **Faltan argumentos**\n\n"
                "Debes incluir email y contraseña.\n\n"
                "**Ejemplo:**\n"
                "`/acc tuemail@gmail.com tucontraseña`",
                parse_mode='Markdown'
            )
            return
        
        # Obtener email (segunda palabra)
        email = parts[1].strip()
        
        # Obtener contraseña (todo lo demás)
        password = ' '.join(parts[2:]).strip()
        
        # Validaciones básicas
        if not email or not password:
            await update.message.reply_text(
                "❌ **Email o contraseña vacíos**",
                parse_mode='Markdown'
            )
            return
        
        if '@' not in email or '.' not in email:
            await update.message.reply_text(
                "❌ **Email inválido**\n\nPor favor ingresa un email válido",
                parse_mode='Markdown'
            )
            return
        
        if len(password) < 4:
            await update.message.reply_text(
                "❌ **Contraseña muy corta**\n\nLa contraseña debe tener al menos 4 caracteres",
                parse_mode='Markdown'
            )
            return
        
        # Guardar credenciales
        success = save_user_credentials(user_id, email, password)
        
        if success:
            # Mostrar contraseña oculta
            if len(password) > 3:
                password_display = password[0] + '•' * (len(password) - 2) + password[-1]
            else:
                password_display = '•' * len(password)
            
            confirmation_text = (
                f"✅ **¡Cuenta configurada exitosamente, {user_name}!** ✅\n\n"
                f"📧 **Email:** `{email}`\n"
                f"🔑 **Contraseña:** `{password_display}`\n"
                f"🆔 **Tu ID:** `{user_id}`\n\n"
                f"**Próximo paso:** Usa `/gencookie` para generar tus cookies de Amazon"
            )
            
            await update.message.reply_text(confirmation_text, parse_mode='Markdown')
            logger.info(f"Credenciales guardadas para usuario {user_id}")
            
        else:
            await update.message.reply_text(
                "❌ **Error al guardar credenciales**\n\nPor favor, intenta nuevamente",
                parse_mode='Markdown'
            )
            logger.error(f"Error guardando credenciales para usuario {user_id}")
            
    except Exception as e:
        logger.error(f"Error en acc_command: {e}")
        error_text = (
            "❌ **Error al procesar el comando**\n\n"
            "**Por favor, usa este formato:**\n"
            "`/acc email@ejemplo.com contraseña`\n\n"
            "**Ejemplo concreto:**\n"
            "`/acc miemail@gmail.com MiContraseña.123`\n\n"
            "Si el problema persiste, contacta al administrador."
        )
        await update.message.reply_text(error_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /help"""
    help_text = (
        "🆘 **AYUDA - VikingCookies Bot** 🍪\n\n"
        "**📋 COMANDOS DISPONIBLES:**\n\n"
        "`/start` - Mensaje de bienvenida\n"
        "`/acc email contraseña` - Configurar cuenta Amazon\n"
        "`/gencookie` - Generar cookies (flujo completo)\n"
        "`/micuenta` - Ver tu cuenta configurada\n"
        "`/status` - Estado del bot\n"
        "`/help` - Esta ayuda\n\n"
        "**🔐 CONFIGURACIÓN INICIAL:**\n\n"
        "1. **Configura tu cuenta:**\n"
        "   ```\n"
        "   /acc tuemail@gmail.com tucontraseña\n"
        "   ```\n\n"
        "2. **Genera cookies:**\n"
        "   ```\n"
        "   /gencookie\n"
        "   ```\n\n"
        "**⚡ FLUJO COMPLETO:**\n"
        "El bot realizará automáticamente:\n"
        "- ✅ Login en tu cuenta Amazon\n"
        "- ✅ Agregar dirección EE.UU.\n"
        "- ✅ Configurar One-Click\n"
        "- ✅ Generar cookies válidas\n\n"
        "**🛠️ SOPORTE:**\n"
        "Si tienes problemas, verifica:\n"
        "- Tu cuenta Amazon está activa\n"
        "- Las credenciales son correctas\n"
        "- No hay espacios extras en el comando"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /status"""
    try:
        # Contar usuarios registrados
        credentials = load_user_credentials()
        user_count = len(credentials)
        
        status_text = (
            f"✅ **BOT FUNCIONANDO CORRECTAMENTE** ✅\n\n"
            f"**📊 ESTADÍSTICAS:**\n"
            f"👥 Usuarios registrados: `{user_count}`\n"
            f"🆔 Tu ID: `{update.message.from_user.id}`\n"
            f"📛 Tu nombre: `{update.message.from_user.first_name}`\n\n"
            f"**🌎 SERVICIO:**\n"
            f"🔧 Estado: `🟢 ACTIVO`\n"
            f"⚡ Versión: `VikingCookies 2.0`\n"
            f"🕒 Última actualización: `{time.ctime()}`\n\n"
            f"**💡 INFORMACIÓN:**\n"
            f"Este bot genera cookies de Amazon mediante\n"
            f"un flujo completo de autenticación."
        )
        await update.message.reply_text(status_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error en status_command: {e}")
        await update.message.reply_text("✅ **Bot activo y funcionando**", parse_mode='Markdown')

async def micuenta_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /micuenta"""
    try:
        user_id = update.message.from_user.id
        user_name = update.message.from_user.first_name
        credentials = get_user_credentials(user_id)
        
        if credentials:
            email = credentials['email']
            timestamp = credentials['timestamp']
            
            # Formatear contraseña oculta
            password = credentials['password']
            if len(password) > 3:
                password_display = password[0] + '•' * (len(password) - 2) + password[-1]
            else:
                password_display = '•' * len(password)
            
            account_info = (
                f"📋 **INFORMACIÓN DE TU CUENTA** 📋\n\n"
                f"👤 **Usuario:** `{user_name}`\n"
                f"🆔 **ID:** `{user_id}`\n"
                f"📧 **Email Amazon:** `{email}`\n"
                f"🔑 **Contraseña:** `{password_display}`\n"
                f"📅 **Configurada el:** `{time.ctime(timestamp)}`\n\n"
                f"**Acciones disponibles:**\n"
                f"• Usa `/gencookie` para generar cookies\n"
                f"• Usa `/acc nuevoemail nuevacontraseña` para cambiar\n"
                f"• Usa `/status` para ver el estado del bot"
            )
            
            await update.message.reply_text(account_info, parse_mode='Markdown')
            
        else:
            await update.message.reply_text(
                "❌ **No tienes cuenta configurada**\n\n"
                "Usa el comando:\n"
                "`/acc email@ejemplo.com contraseña`\n\n"
                "**Ejemplo:**\n"
                "`/acc usuario@gmail.com micontraseña123`",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Error en micuenta_command: {e}")
        await update.message.reply_text(
            "❌ **Error al obtener información de la cuenta**",
            parse_mode='Markdown'
        )

async def generar_cookie_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja el comando /gencookie"""
    try:
        from comandos.gencookie import generar_cookie_completa, format_cookies_amz
        
        user_id = update.message.from_user.id
        user_name = update.message.from_user.first_name
        
        # Verificar si el usuario tiene credenciales configuradas
        credentials = get_user_credentials(user_id)
        if not credentials:
            await update.message.reply_text(
                "❌ **Primero configura tu cuenta Amazon**\n\n"
                "Usa el comando:\n"
                "`/acc email@ejemplo.com contraseña`\n\n"
                "**Ejemplo:**\n"
                "`/acc usuario@gmail.com micontraseña123`",
                parse_mode='Markdown'
            )
            return
        
        # Enviar mensaje de "generando..."
        mensaje = await update.message.reply_text(
            f"🔐 **INICIANDO FLUJO COMPLETO** 🔐\n\n"
            f"👤 **Usuario:** {user_name}\n"
            f"📧 **Cuenta:** {credentials['email']}\n\n"
            "🔄 **Procesando... Esto puede tomar 20-30 segundos**\n\n"
            "⏳ Por favor, espera...",
            parse_mode='Markdown'
        )

        # Generar las cookies con flujo completo
        cookies_dict, success = generar_cookie_completa(user_id, "com", "US")

        if success and cookies_dict:
            # Formatear cookies
            cookies_text = format_cookies_amz(cookies_dict)
            
            # Mensaje de éxito
            success_message = (
                f"✅ **¡COOKIES GENERADAS EXITOSAMENTE!** ✅\n\n"
                f"👤 **Usuario:** {user_name}\n"
                f"📧 **Cuenta:** {credentials['email']}\n"
                f"🍪 **Total cookies:** {len(cookies_dict)}\n"
                f"🇺🇸 **Dirección EE.UU.:** ✅ Agregada\n"
                f"⚡ **One-Click:** ✅ Configurado\n\n"
                "🔹 **TUS COOKIES LISTAS:**\n\n"
                f"`{cookies_text}`\n\n"
                "📋 **Copia el texto de arriba**\n"
                "💳 **Listas para usar en verificaciones**"
            )
            
            await mensaje.edit_text(success_message, parse_mode='Markdown')
            
        else:
            await mensaje.edit_text(
                "❌ **Error al generar las cookies**\n\n"
                "⚠️ **Posibles causas:**\n"
                "• Credenciales incorrectas\n"
                "• Problemas de conexión con Amazon\n"
                "• CAPTCHA requerido\n"
                "• Cuenta temporalmente bloqueada\n\n"
                "🔧 **Solución:**\n"
                "1. Verifica tus credenciales con `/micuenta`\n"
                "2. Intenta nuevamente en unos minutos\n"
                "3. Si persiste, contacta al administrador",
                parse_mode='Markdown'
            )

    except Exception as e:
        logger.error(f"Error en generar_cookie_handler: {e}")
        error_msg = (
            "❌ **Error inesperado durante la generación**\n\n"
            "El bot encontró un problema inesperado.\n"
            "Por favor, intenta nuevamente en unos minutos."
        )
        await update.message.reply_text(error_msg, parse_mode='Markdown')

def main():
    """Función principal para iniciar el bot en DisCloud"""
    try:
        # Verificar que el token esté configurado
        if BOT_TOKEN == "TU_TOKEN_AQUI":
            logger.error("❌ ERROR: Configura BOT_TOKEN en las variables de entorno de DisCloud")
            print("❌ ERROR: Configura BOT_TOKEN en las variables de entorno de DisCloud")
            return
        
        # Crear la aplicación
        application = Application.builder().token(BOT_TOKEN).build()

        # Añadir handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("acc", acc_command))
        application.add_handler(CommandHandler("gencookie", generar_cookie_handler))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(CommandHandler("micuenta", micuenta_command))

        # Iniciar el bot
        logger.info("🤖 Bot VikingCookies iniciado en DisCloud...")
        print("🚀 VikingCookies Bot está funcionando!")
        print("📊 Listo para recibir comandos...")
        application.run_polling()

    except Exception as e:
        logger.error(f"❌ Error al iniciar el bot: {e}")
        print(f"❌ Error al iniciar el bot: {e}")

if __name__ == "__main__":
    main()
