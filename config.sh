#!/bin/bash
# Configuración general del sistema

# Directorios
DATA_DIR="datos"
LOGS_DIR="logs"
PDF_DIR="facturas_pdf"
REPORTS_DIR="reportes"

# Archivos
TEMPLATE_FILE="plantilla_factura_IRSI.tex"
PENDING_FILE="temp/pendientes_envio.csv"
DAILY_LOG="logs/log_diario.log"
SHIPMENT_LOG="logs/envios/log_envios.csv"

# Email del administrador
ADMIN_EMAIL="admin@mercadoirsi.com"

# Configuración de limpieza automática
CLEANUP_LOGS_DAYS=7      # Días para mantener logs
CLEANUP_PDF_DAYS=30      # Días para mantener PDFs
CLEANUP_TEMP_USERS_DAYS=30  # Días para mantener usuarios temporales
