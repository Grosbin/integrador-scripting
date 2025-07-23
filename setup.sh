#!/bin/bash

# Script de Instalación Completa del Sistema de Facturación Mercado IRSI
# Configura el entorno, dependencias y estructura del proyecto

set -e  # Terminar si hay errores

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner de inicio
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║        SISTEMA DE FACTURACIÓN AUTOMATIZADO               ║
║                  MERCADO IRSI                            ║
║                                                           ║
║  Instalación y configuración automática del sistema      ║
╚═══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Función para mostrar progreso
show_progress() {
    local current=$1
    local total=$2
    local task=$3
    
    printf "\r${BLUE}[%d/%d]${NC} %s..." "$current" "$total" "$task"
}

# Función para mostrar éxito
show_success() {
    echo -e "\r${GREEN}$1${NC}"
}

# Función para mostrar error
show_error() {
    echo -e "\r${RED}ERROR: $1${NC}"
}

# Función para mostrar advertencia
show_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

# Verificar sistema operativo
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if command -v apt &> /dev/null; then
            PACKAGE_MANAGER="apt"
        elif command -v yum &> /dev/null; then
            PACKAGE_MANAGER="yum"
        elif command -v dnf &> /dev/null; then
            PACKAGE_MANAGER="dnf"
        else
            show_error "Gestor de paquetes no soportado"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        PACKAGE_MANAGER="brew"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        PACKAGE_MANAGER="choco"
    else
        show_error "Sistema operativo no soportado: $OSTYPE"
        exit 1
    fi
    
    show_success "Sistema detectado: $OS con $PACKAGE_MANAGER"
}

# Crear estructura de directorios
create_directories() {
    show_progress 1 8 "Creando estructura de directorios"
    
    directories=("datos" "logs" "facturas_pdf" "reportes" "backup")
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
    done
    
    show_success "Estructura de directorios creada"
}

# Configurar permisos
set_permissions() {
    show_progress 2 8 "Configurando permisos de archivos"
    
    # Scripts de bash
    chmod +x generador_facturas.sh 2>/dev/null || true
    chmod +x cron_job.sh 2>/dev/null || true
    chmod +x setup.sh 2>/dev/null || true
    
    # Script de instalación de cron
    if [[ -f "instalar_cron.sh" ]]; then
        chmod +x instalar_cron.sh
    fi
    
    show_success "Permisos configurados"
}

# Verificar e instalar Python
install_python() {
    show_progress 3 8 "Verificando Python 3"
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        show_success "Python 3 ya instalado: $PYTHON_VERSION"
    else
        show_warning "Python 3 no encontrado, instalando..."
        
        case $PACKAGE_MANAGER in
            "apt")
                sudo apt update && sudo apt install -y python3 python3-pip
                ;;
            "yum")
                sudo yum install -y python3 python3-pip
                ;;
            "dnf")
                sudo dnf install -y python3 python3-pip
                ;;
            "brew")
                brew install python3
                ;;
            *)
                show_error "No se puede instalar Python automáticamente"
                echo "Por favor instale Python 3 manualmente"
                exit 1
                ;;
        esac
        
        show_success "Python 3 instalado"
    fi
}

# Instalar módulos Python
install_python_modules() {
    show_progress 4 8 "Instalando módulos Python"
    
    modules=("faker")
    
    for module in "${modules[@]}"; do
        if python3 -c "import $module" 2>/dev/null; then
            echo "  $module ya instalado"
        else
            echo "  Instalando $module..."
            pip3 install "$module" --user
        fi
    done
    
    show_success "Módulos Python instalados"
}

# Verificar e instalar LaTeX
install_latex() {
    show_progress 5 8 "Verificando LaTeX"
    
    if command -v pdflatex &> /dev/null; then
        show_success "LaTeX ya instalado"
    else
        show_warning "LaTeX no encontrado"
        
        echo -e "${YELLOW}Para instalar LaTeX:${NC}"
        case $OS in
            "linux")
                case $PACKAGE_MANAGER in
                    "apt")
                        echo "  sudo apt install texlive-latex-base texlive-latex-extra"
                        ;;
                    "yum"|"dnf")
                        echo "  sudo $PACKAGE_MANAGER install texlive texlive-latex"
                        ;;
                esac
                ;;
            "macos")
                echo "  brew install --cask mactex"
                ;;
            "windows")
                echo "  choco install miktex"
                ;;
        esac
        
        read -p "¿Desea instalar LaTeX automáticamente? (y/n): " install_tex
        
        if [[ $install_tex == "y" || $install_tex == "Y" ]]; then
            case $PACKAGE_MANAGER in
                "apt")
                    sudo apt install -y texlive-latex-base texlive-latex-extra
                    ;;
                "yum")
                    sudo yum install -y texlive texlive-latex
                    ;;
                "dnf")
                    sudo dnf install -y texlive texlive-latex
                    ;;
                "brew")
                    brew install --cask mactex
                    ;;
                *)
                    show_warning "Instalación manual requerida"
                    ;;
            esac
            
            if command -v pdflatex &> /dev/null; then
                show_success "LaTeX instalado exitosamente"
            else
                show_error "Error instalando LaTeX"
            fi
        else
            show_warning "LaTeX no instalado - funcionalidad limitada"
        fi
    fi
}

# Crear archivos de configuración
create_config_files() {
    show_progress 6 8 "Creando archivos de configuración"
    
    # Archivo de configuración para SMTP
    if [[ ! -f "config_smtp.py" ]]; then
        cat > config_smtp.py << 'EOF'
# Configuración SMTP para envío de correos
# Personalizar según tu proveedor de correo

SMTP_CONFIG = {
    'server': 'smtp.gmail.com',     # Gmail
    'port': 587,
    'user': 'tu_correo@gmail.com',  # CAMBIAR
    'password': 'tu_app_password',   # CAMBIAR - usar contraseña de aplicación
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
EOF
    fi
    
    # Archivo de configuración general
    if [[ ! -f "config.sh" ]]; then
        cat > config.sh << 'EOF'
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
EOF
    fi
    
    show_success "Archivos de configuración creados"
}

# Generar datos de prueba
generate_test_data() {
    show_progress 7 8 "Generando datos de prueba"
    
    if [[ -f "generador_compras.py" ]]; then
        # Asegurar que el directorio datos existe
        mkdir -p datos
        
        # Generar datos desde el directorio raíz
        python3 generador_compras.py 5 > /dev/null 2>&1
        
        show_success "Datos de prueba generados"
    else
        show_warning "generador_compras.py no encontrado"
    fi
}

# Verificar instalación
verify_installation() {
    show_progress 8 8 "Verificando instalación"
    
    errors=0
    
    # Verificar archivos principales
    required_files=("generador_compras.py" "generador_facturas.sh" "enviador.py" "plantilla_factura_IRSI.tex")
    
    for file in "${required_files[@]}"; do
        if [[ -f "$file" ]]; then
            echo "  $file"
        else
            echo "  FALTANTE: $file"
            ((errors++))
        fi
    done
    
    # Verificar comandos
    if command -v python3 &> /dev/null; then
        echo "  Python 3"
    else
        echo "  FALTANTE: Python 3"
        ((errors++))
    fi
    
    if command -v pdflatex &> /dev/null; then
        echo "  pdflatex"
    else
        echo "  WARNING: pdflatex (opcional)"
    fi
    
    # Verificar módulos Python
    if python3 -c "import faker" 2>/dev/null; then
        echo "  Modulo faker"
    else
        echo "  FALTANTE: Modulo faker"
        ((errors++))
    fi
    
    if [[ $errors -eq 0 ]]; then
        show_success "Verificación completada sin errores"
    else
        show_error "Verificación completada con $errors errores"
    fi
    
    return $errors
}

# Mostrar siguiente pasos
show_next_steps() {
    echo -e "\n${GREEN}INSTALACION COMPLETADA${NC}\n"
    
    echo -e "${BLUE}PRÓXIMOS PASOS:${NC}"
    echo "1. Configurar credenciales SMTP en config_smtp.py"
    echo "2. Ejecutar prueba manual:"
    echo "   ${YELLOW}python3 generador_compras.py 3${NC}"
    echo "   ${YELLOW}./generador_facturas.sh${NC}"
    echo ""
    echo "3. Para automatización:"
    echo "   ${YELLOW}./instalar_cron.sh${NC} (Linux/macOS)"
    echo "   ${YELLOW}powershell configurar_tareas_windows.ps1${NC} (Windows)"
    echo ""
    echo -e "${BLUE}ARCHIVOS IMPORTANTES:${NC}"
    echo "config_smtp.py - Configuracion de correo"
    echo "config.sh - Configuracion general"
    echo "datos/ - Archivos CSV generados"
    echo "facturas_pdf/ - PDFs generados"
    echo "logs/ - Archivos de log"
    echo ""
    echo -e "${BLUE}DOCUMENTACIÓN:${NC}"
    echo "Para más información, consulte los comentarios en cada archivo."
}

# Función principal
main() {
    echo -e "${BLUE}Iniciando instalación...${NC}\n"
    
    # Detectar sistema operativo
    detect_os
    
    # Ejecutar pasos de instalación
    create_directories
    set_permissions
    install_python
    install_python_modules
    install_latex
    create_config_files
    generate_test_data
    
    # Verificar instalación
    if verify_installation; then
        show_next_steps
        exit 0
    else
        echo -e "\n${RED}ERROR: Instalacion completada con errores${NC}"
        echo "Revise los mensajes anteriores y corrija los problemas."
        exit 1
    fi
}

# Manejo de señales
trap 'echo -e "\n${RED}ERROR: Instalacion interrumpida${NC}"; exit 130' SIGINT SIGTERM

# Ejecutar instalación
main "$@"