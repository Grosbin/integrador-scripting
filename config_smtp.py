# Configuración SMTP para envío de correos
# Personalizar según tu proveedor de correo

SMTP_CONFIG = {
    'server': 'smtp.gmail.com',     # Gmail
    'port': 587,
    'user': 'robertobetancourth96@gmail.com',  # CAMBIAR 
    'password': 'app_password',   # CAMBIAR
    'use_tls': True
}

# Configuración alternativa para otros proveedores:

# Outlook/Hotmail
# SMTP_CONFIG = {
#     'server': 'smtp-mail.outlook.com',
#     'port': 587,
#     'user': 'tu_correo@outlook.com',
#     'password': 'tu_password',
#     'use_tls': True
# }

# Yahoo
# SMTP_CONFIG = {
#     'server': 'smtp.mail.yahoo.com',
#     'port': 587,
#     'user': 'tu_correo@yahoo.com',
#     'password': 'tu_app_password',
#     'use_tls': True
# }

# Office 365
# SMTP_CONFIG = {
#     'server': 'smtp.office365.com',
#     'port': 587,
#     'user': 'tu_correo@tudominio.com',
#     'password': 'tu_password',
#     'use_tls': True
# }

# INSTRUCCIONES DE CONFIGURACIÓN PARA GMAIL:
# 
# PASO 1: Activar verificación en 2 pasos
# 1. Ve a https://myaccount.google.com/security
# 2. Activa "Verificación en 2 pasos" si no está activada
# 
# PASO 2: Generar contraseña de aplicación
# 1. Ve a https://myaccount.google.com/apppasswords
# 2. Selecciona "Correo" como aplicación
# 3. Selecciona tu dispositivo (o "Otro" si no aparece)
# 4. Haz clic en "Generar"
# 5. Copia la contraseña de 16 caracteres (sin espacios)
# 
# PASO 3: Actualizar configuración
# 1. Cambia 'user' por tu dirección de correo real
# 2. Cambia 'password' por la contraseña de aplicación generada
# 
# NOTA: Si sigues teniendo problemas:
# - Verifica que la verificación en 2 pasos esté activada
# - Asegúrate de usar la contraseña de aplicación, NO tu contraseña normal
# - La contraseña de aplicación debe tener exactamente 16 caracteres
# - Si el problema persiste, genera una nueva contraseña de aplicación
