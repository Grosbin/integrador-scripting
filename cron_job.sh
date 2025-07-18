#!/bin/bash

# Script de Automatización para Cron
# Orquesta la ejecución secuencial del sistema de facturación

# Configuración
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/cron_execution.log"
LOCK_FILE="/tmp/mercado_irsi_cron.lock"

# Función de logging con timestamp
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [CRON] $1" | tee -a "$LOG_FILE"
}

# Función para cleanup en caso de error
cleanup() {
    if [[ -f "$LOCK_FILE" ]]; then
        rm -f "$LOCK_FILE"
    fi
}

# Trap para cleanup
trap cleanup EXIT

# Verificar si ya se está ejecutando otra instancia
if [[ -f "$LOCK_FILE" ]]; then
    log_message "ERROR: Otra instancia del proceso ya está ejecutándose"
    exit 1
fi

# Crear lock file
echo $$ > "$LOCK_FILE"

# Cambiar al directorio del script
cd "$SCRIPT_DIR"

log_message "=== INICIO DE EJECUCIÓN AUTOMATIZADA ==="

# Función para ejecutar paso con manejo de errores
execute_step() {
    local step_name="$1"
    local command="$2"
    local timeout_seconds="${3:-300}"  # 5 minutos por defecto
    
    log_message "Iniciando: $step_name"
    
    # Ejecutar comando con timeout
    if timeout "$timeout_seconds" bash -c "$command"; then
        log_message "✅ $step_name completado exitosamente"
        return 0
    else
        local exit_code=$?
        if [[ $exit_code -eq 124 ]]; then
            log_message "❌ $step_name - TIMEOUT después de $timeout_seconds segundos"
        else
            log_message "❌ $step_name - Error con código: $exit_code"
        fi
        return $exit_code
    fi
}

# PASO 1: Generar datos de compras (opcional, solo si no hay archivos recientes)
newest_csv=$(ls -t datos/compras_lote_*.csv 2>/dev/null | head -1)
if [[ -z "$newest_csv" ]] || [[ $(find "$newest_csv" -mtime +1 2>/dev/null) ]]; then
    execute_step "Generación de Compras" "python3 generador_compras.py 15" 120
    if [[ $? -ne 0 ]]; then
        log_message "ERROR: Fallo en generación de compras, abortando"
        exit 1
    fi
else
    log_message "INFO: Usando archivo CSV existente: $newest_csv"
fi

# PASO 2: Generar facturas
execute_step "Generación de Facturas" "./generador_facturas.sh" 600
if [[ $? -ne 0 ]]; then
    log_message "ERROR: Fallo en generación de facturas, abortando"
    exit 1
fi

# Esperar 1 hora antes del envío (simular diferencia horaria)
# En producción, esto se manejaría con cron programado para diferentes horas
if [[ "${SKIP_WAIT:-false}" != "true" ]]; then
    log_message "INFO: Esperando 1 hora antes del envío de correos..."
    sleep 3600  # 1 hora
fi

# PASO 3: Enviar correos
execute_step "Envío de Correos" "python3 enviador.py" 1800
envio_exit_code=$?

# PASO 4: Procesar empleados temporales (si hay archivo)
if [[ -f "datos/empleados.csv" ]]; then
    execute_step "Gestión de Usuarios" "powershell -File usuarios.ps1" 300
fi

# Resumen final
log_message "=== RESUMEN DE EJECUCIÓN ==="
log_message "Facturas generadas: $(ls facturas_pdf/*.pdf 2>/dev/null | wc -l)"
log_message "Pendientes de envío: $(wc -l < pendientes_envio.csv 2>/dev/null || echo 0)"

if [[ -f "log_envios.csv" ]]; then
    exitosos=$(awk -F',' '$3=="exitoso" {count++} END {print count+0}' log_envios.csv)
    fallidos=$(awk -F',' '$3=="fallido" {count++} END {print count+0}' log_envios.csv)
    log_message "Envíos exitosos: $exitosos"
    log_message "Envíos fallidos: $fallidos"
fi

log_message "=== FIN DE EJECUCIÓN AUTOMATIZADA ==="

# Limpiar archivos temporales antiguos (más de 7 días)
find . -name "*.aux" -o -name "*.log" -o -name "factura_*.tex" | xargs rm -f 2>/dev/null
find logs/ -name "*.log" -mtime +7 -delete 2>/dev/null
find facturas_pdf/ -name "*.pdf" -mtime +30 -delete 2>/dev/null

# Código de salida basado en el resultado del envío
exit $envio_exit_code