# Configuración SMTP para envío de correos
# Personalizar según tu proveedor de correo

SMTP_CONFIG = {
    'server': 'smtp.gmail.com',     # Gmail
    'port': 587,
    'user': 'tu_correo@gmail.com',  # CAMBIAR - Tu correo real
    'password': 'tu_app_password',   # CAMBIAR - Tu contraseña de aplicación
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

# INSTRUCCIONES DE CONFIGURACIÓN:
# 1. Cambia 'user' por tu dirección de correo real
# 2. Cambia 'password' por tu contraseña de aplicación (no la contraseña normal)
# 3. Para Gmail: Activa la verificación en 2 pasos y genera una contraseña de aplicación
# 4. Para otros proveedores: Usa la configuración correspondiente descomentada arriba
