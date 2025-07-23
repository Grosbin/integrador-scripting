# Configuración de rutas y archivos del sistema
# Este archivo centraliza todas las rutas para facilitar mantenimiento

import os
from pathlib import Path

# Obtener directorio base del proyecto
BASE_DIR = Path(__file__).parent.absolute()

# Configuración de directorios
DIRECTORIES = {
    'data': BASE_DIR / 'datos',
    'logs': BASE_DIR / 'logs',
    'logs_envios': BASE_DIR / 'logs' / 'envios',
    'reports': BASE_DIR / 'logs' / 'reportes',
    'pdf': BASE_DIR / 'facturas_pdf',
    'temp': BASE_DIR / 'temp',
    'backup': BASE_DIR / 'backup'
}

# Configuración de archivos
FILES = {
    'template': BASE_DIR / 'plantilla_factura_IRSI.tex',
    'pending': BASE_DIR / 'temp' / 'pendientes_envio.csv',
    'daily_log': BASE_DIR / 'logs' / 'log_diario.log',
    'shipment_log': BASE_DIR / 'logs' / 'envios' / 'log_envios.csv',
    'enviador_log': BASE_DIR / 'logs' / 'envios' / 'enviador.log',
    'cron_log': BASE_DIR / 'cron_execution.log'
}

# Configuración de email del administrador
ADMIN_EMAIL = "admin@mercadoirsi.com"

# Configuración de limpieza automática (en días)
CLEANUP_CONFIG = {
    'logs_days': 7,           # Días para mantener logs
    'pdf_days': 30,           # Días para mantener PDFs
    'temp_users_days': 30,    # Días para mantener usuarios temporales
    'backup_days': 90         # Días para mantener backups
}

# Configuración de límites del sistema
LIMITS = {
    'max_emails_per_batch': 100,    # Máximo correos por lote
    'max_retries': 3,               # Máximo reintentos de envío
    'timeout_seconds': 30,          # Timeout para conexiones SMTP
    'max_file_size_mb': 10          # Tamaño máximo de archivos adjuntos
}

# Configuración de formato de fechas
DATE_FORMATS = {
    'display': '%Y-%m-%d %H:%M:%S',
    'file': '%Y%m%d',
    'log': '%Y-%m-%d %H:%M:%S'
}

# Configuración de logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s [%(levelname)s] %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S'
}

def ensure_directories():
    """Crea todos los directorios necesarios si no existen"""
    for dir_path in DIRECTORIES.values():
        dir_path.mkdir(parents=True, exist_ok=True)

def get_path(key: str) -> Path:
    """Obtiene una ruta específica del sistema"""
    if key in DIRECTORIES:
        return DIRECTORIES[key]
    elif key in FILES:
        return FILES[key]
    else:
        raise KeyError(f"Ruta no encontrada: {key}")

def get_file_path(key: str) -> str:
    """Obtiene la ruta de un archivo como string"""
    return str(get_path(key))

def get_dir_path(key: str) -> str:
    """Obtiene la ruta de un directorio como string"""
    return str(get_path(key)) 