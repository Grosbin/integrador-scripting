#!/bin/bash

# Sistema de Generación de Facturas Automatizado
# Procesa archivos CSV y genera facturas PDF usando LaTeX

set -e  # Terminar si hay errores

# Configuración
TEMPLATE_FILE="plantilla_factura_IRSI.tex"
LOG_DIR="logs"
PDF_DIR="facturas_pdf"
PENDING_FILE="temp/pendientes_envio.csv"
DAILY_LOG="logs/log_diario.log"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para logging
log_message() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$DAILY_LOG"
}

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 [archivo_csv] [plantilla_tex]"
    echo "Genera facturas PDF a partir de datos CSV usando plantilla LaTeX"
    echo ""
    echo "Opciones:"
    echo "  -h, --help     Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 compras.csv plantilla_factura_IRSI.tex"
    echo "  $0  # Usa valores por defecto"
}

# Función para crear directorios necesarios
setup_directories() {
    mkdir -p "$LOG_DIR" "$PDF_DIR"
    log_message "INFO" "Directorios creados: $LOG_DIR, $PDF_DIR"
}

# Función para validar archivos necesarios
validate_files() {
    local csv_file=$1
    local template_file=$2
    
    if [[ ! -f "$csv_file" ]]; then
        log_message "ERROR" "Archivo CSV no encontrado: $csv_file"
        exit 1
    fi
    
    if [[ ! -f "$template_file" ]]; then
        log_message "ERROR" "Plantilla LaTeX no encontrada: $template_file"
        exit 1
    fi
    
    # Verificar que pdflatex esté disponible
    if ! command -v pdflatex &> /dev/null; then
        log_message "ERROR" "pdflatex no está instalado o no está en PATH"
        exit 1
    fi
    
    log_message "INFO" "Validación de archivos completada"
}

# Función para limpiar archivos auxiliares de LaTeX
cleanup_latex() {
    local base_name=$1
    rm -f "${base_name}.aux" "${base_name}.log" "${base_name}.fls" "${base_name}.fdb_latexmk"
}

# Función para sustituir placeholders en plantilla LaTeX
substitute_placeholders() {
    local template_file=$1
    local output_file=$2
    local id_transaccion=$3
    local fecha_emision=$4
    local nombre=$5
    local correo=$6
    local telefono=$7
    local direccion=$8
    local ciudad=$9
    local cantidad=${10}
    local monto=${11}
    local pago=${12}
    local estado_pago=${13}
    local ip=${14}
    local timestamp=${15}
    local observaciones=${16}
    
    # Copiar plantilla a archivo temporal
    cp "$template_file" "$output_file"

    # sed -i "s/{id_transaccion}/$id_transaccion/g" "$output_file"
    # sed -i "s/{fecha_emision}/$fecha_emision/g" "$output_file"
    # sed -i "s/{nombre}/$nombre/g" "$output_file"
    # sed -i "s/{correo}/$correo/g" "$output_file"
    # sed -i "s/{telefono}/$telefono/g" "$output_file"
    # sed -i "s/{direccion}/$direccion/g" "$output_file"
    # sed -i "s/{ciudad}/$ciudad/g" "$output_file"
    # sed -i "s/{cantidad}/$cantidad/g" "$output_file"
    # sed -i "s/{monto}/$monto/g" "$output_file"
    # sed -i "s/{pago}/$pago/g" "$output_file"
    # sed -i "s/{estado_pago}/$estado_pago/g" "$output_file"
    # sed -i "s/{ip}/$ip/g" "$output_file"
    # sed -i "s/{timestamp}/$timestamp/g" "$output_file"
    # sed -i "s/{observaciones}/$observaciones/g" "$output_file"
    
    # Sustituir cada placeholder individualmente usando sed (compatible con macOS)
    sed -i '' "s/{id_transaccion}/$id_transaccion/g" "$output_file"
    sed -i '' "s/{fecha_emision}/$fecha_emision/g" "$output_file"
    sed -i '' "s/{nombre}/$nombre/g" "$output_file"
    sed -i '' "s/{correo}/$correo/g" "$output_file"
    sed -i '' "s/{telefono}/$telefono/g" "$output_file"
    sed -i '' "s/{direccion}/$direccion/g" "$output_file"
    sed -i '' "s/{ciudad}/$ciudad/g" "$output_file"
    sed -i '' "s/{cantidad}/$cantidad/g" "$output_file"
    sed -i '' "s/{monto}/$monto/g" "$output_file"
    sed -i '' "s/{pago}/$pago/g" "$output_file"
    sed -i '' "s/{estado_pago}/$estado_pago/g" "$output_file"
    sed -i '' "s/{ip}/$ip/g" "$output_file"
    sed -i '' "s/{timestamp}/$timestamp/g" "$output_file"
    sed -i '' "s/{observaciones}/$observaciones/g" "$output_file"
}

# Función para compilar LaTeX a PDF
compile_latex() {
    local tex_file=$1
    local base_name=$(basename "$tex_file" .tex)
    local log_file="${LOG_DIR}/${base_name}.log"
    
    log_message "INFO" "Compilando $tex_file"
    
    # Compilar con pdflatex
    if pdflatex -output-directory="$PDF_DIR" -interaction=nonstopmode "$tex_file" > "$log_file" 2>&1; then
        cleanup_latex "${PDF_DIR}/${base_name}"
        log_message "INFO" "PDF generado: ${PDF_DIR}/${base_name}.pdf"
        return 0
    else
        # Buscar errores en el log
        if grep -q "!" "$log_file"; then
            log_message "ERROR" "Error de compilación en $tex_file:"
            grep "!" "$log_file" | head -5 | while read error; do
                log_message "ERROR" "  $error"
            done
        fi
        return 1
    fi
}

# Función para procesar una línea del CSV
process_invoice() {
    local line=$1
    local line_number=$2
    
    # Separar campos del CSV usando awk
    IFS=',' read -r id_transaccion fecha_emision nombre correo telefono direccion ciudad cantidad monto pago estado_pago ip timestamp observaciones <<< "$line"
    
    # Limpiar campos (remover comillas y espacios)
    id_transaccion=$(echo "$id_transaccion" | tr -d '"' | xargs)
    fecha_emision=$(echo "$fecha_emision" | tr -d '"' | xargs)
    nombre=$(echo "$nombre" | tr -d '"' | xargs)
    correo=$(echo "$correo" | tr -d '"' | xargs)
    telefono=$(echo "$telefono" | tr -d '"' | xargs)
    direccion=$(echo "$direccion" | tr -d '"' | xargs)
    ciudad=$(echo "$ciudad" | tr -d '"' | xargs)
    cantidad=$(echo "$cantidad" | tr -d '"' | xargs)
    monto=$(echo "$monto" | tr -d '"' | xargs)
    pago=$(echo "$pago" | tr -d '"' | xargs)
    estado_pago=$(echo "$estado_pago" | tr -d '"' | xargs)
    ip=$(echo "$ip" | tr -d '"' | xargs)
    timestamp=$(echo "$timestamp" | tr -d '"' | xargs)
    observaciones=$(echo "$observaciones" | tr -d '"' | xargs)
    
    # Validar campos obligatorios
    if [[ -z "$id_transaccion" || -z "$nombre" || -z "$correo" ]]; then
        log_message "ERROR" "Línea $line_number: Campos obligatorios faltantes"
        return 1
    fi
    
    # Nombres de archivos
    local tex_file="factura_${id_transaccion}.tex"
    local pdf_file="factura_${id_transaccion}.pdf"
    
    # Sustituir placeholders
    substitute_placeholders "$TEMPLATE_FILE" "$tex_file" \
        "$id_transaccion" "$fecha_emision" "$nombre" "$correo" \
        "$telefono" "$direccion" "$ciudad" "$cantidad" "$monto" \
        "$pago" "$estado_pago" "$ip" "$timestamp" "$observaciones"
    
    # Compilar a PDF
    if compile_latex "$tex_file"; then
        # Agregar a lista de pendientes de envío
        echo "${PDF_DIR}/${pdf_file},${correo}" >> "$PENDING_FILE"
        log_message "INFO" "Factura agregada a pendientes: $pdf_file -> $correo"
        
        # Limpiar archivo temporal
        rm -f "$tex_file"
        
        return 0
    else
        log_message "ERROR" "Error compilando factura $id_transaccion"
        return 1
    fi
}

# Función principal
main() {
    local csv_file=${1:-$(ls -t datos/compras_lote_*.csv 2>/dev/null | head -1)}
    local template_file=${2:-$TEMPLATE_FILE}
    
    # Mostrar ayuda si se solicita
    if [[ "$1" == "-h" || "$1" == "--help" ]]; then
        show_help
        exit 0
    fi
    
    # Inicializar log diario
    log_message "INFO" "=== INICIO DE GENERACIÓN DE FACTURAS ==="
    log_message "INFO" "Archivo CSV: $csv_file"
    log_message "INFO" "Plantilla: $template_file"
    
    # Configurar directorios
    setup_directories
    
    # Validar archivos
    validate_files "$csv_file" "$template_file"
    
    # Limpiar archivo de pendientes
    > "$PENDING_FILE"
    
    # Contadores
    local total_lines=0
    local successful=0
    local failed=0
    
    # Procesar CSV línea por línea (saltando header)
    log_message "INFO" "Procesando facturas..."
    
    while IFS= read -r line; do
        ((total_lines++))
        
        # Saltar header
        if [[ $total_lines -eq 1 ]]; then
            continue
        fi
        
        echo -e "${YELLOW}Procesando línea $total_lines...${NC}"
        
        if process_invoice "$line" "$total_lines"; then
            ((successful++))
            echo -e "${GREEN}Factura generada exitosamente${NC}"
        else
            ((failed++))
            echo -e "${RED}Error generando factura${NC}"
        fi
        
    done < "$csv_file"
    
    # Resumen final
    log_message "INFO" "=== RESUMEN DE GENERACIÓN ==="
    log_message "INFO" "Total procesadas: $((total_lines - 1))"
    log_message "INFO" "Exitosas: $successful"
    log_message "INFO" "Fallidas: $failed"
    log_message "INFO" "Archivo de pendientes: $PENDING_FILE"
    
    # Mostrar estadísticas
    echo -e "\n${GREEN}=== ESTADÍSTICAS ===${NC}"
    echo -e "Total procesadas: $((total_lines - 1))"
    echo -e "Exitosas: ${GREEN}$successful${NC}"
    echo -e "Fallidas: ${RED}$failed${NC}"
    echo -e "PDFs generados en: ${YELLOW}$PDF_DIR${NC}"
    echo -e "Pendientes de envío: ${YELLOW}$PENDING_FILE${NC}"
    
    # Generar reporte con awk
    if [[ -f "$PENDING_FILE" ]]; then
        local total_monto=$(awk -F',' 'NR>1 {sum += $9} END {print sum}' "$csv_file")
        local total_pagos_completos=$(awk -F',' 'NR>1 && $10=="Pago completo" {count++} END {print count+0}' "$csv_file")
        
        log_message "INFO" "Monto total procesado: L$total_monto"
        log_message "INFO" "Pagos completos: $total_pagos_completos"
    fi
    
    log_message "INFO" "=== FIN DE GENERACIÓN DE FACTURAS ==="
    
    return 0
}

# Ejecutar función principal con todos los argumentos
main "$@"