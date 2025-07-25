# Configuración de Cron para Sistema de Facturación Automatizado
# Instrucciones para configurar tareas programadas en Linux y Windows

# =============================================
# CONFIGURACIÓN PARA LINUX (CRON)
# =============================================

# Para editar el crontab del usuario actual:
# crontab -e

# Agregar las siguientes líneas al crontab:

# Generar facturas todos los días a las 01:00
0 1 * * * /ruta/completa/al/proyecto/generador_facturas.sh >> /ruta/completa/al/proyecto/cron_execution.log 2>&1

# Enviar correos todos los días a las 02:00
0 2 * * * /usr/bin/python3 /ruta/completa/al/proyecto/enviador.py >> /ruta/completa/al/proyecto/cron_execution.log 2>&1

# Procesar usuarios temporales todos los días a las 03:00 (solo si hay archivo)
0 3 * * * [ -f /ruta/completa/al/proyecto/datos/empleados.csv ] && /usr/bin/powershell /ruta/completa/al/proyecto/usuarios.ps1 >> /ruta/completa/al/proyecto/cron_execution.log 2>&1

# Alternativa: Usar el script orquestador completo
# Ejecutar proceso completo todos los días a las 01:00
0 1 * * * /ruta/completa/al/proyecto/cron_job.sh

# Limpiar logs antiguos semanalmente (domingos a las 00:30)
30 0 * * 0 find /ruta/completa/al/proyecto/logs -name "*.log" -mtime +7 -delete

# Variables de entorno para cron (agregar al inicio del crontab)
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
MAILTO=admin@mercadoirsi.com

# =============================================
# SCRIPT DE INSTALACIÓN AUTOMÁTICA PARA LINUX
# =============================================

#!/bin/bash
# instalar_cron.sh - Script para configurar automáticamente las tareas cron

# Obtener directorio actual del proyecto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Crear backup del crontab actual
crontab -l > crontab_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null || true

# Crear nueva configuración de cron
cat << EOF > temp_crontab
# Configuración automática - Sistema de Facturación Mercado IRSI
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
MAILTO=admin@mercadoirsi.com

# Proceso completo de facturación (01:00 diario)
0 1 * * * $PROJECT_DIR/cron_job.sh

# Limpiar logs antiguos (domingos 00:30)
30 0 * * 0 find $PROJECT_DIR/logs -name "*.log" -mtime +7 -delete 2>/dev/null

# Limpiar PDFs antiguos (primer día del mes, 23:59)
59 23 1 * * find $PROJECT_DIR/facturas_pdf -name "*.pdf" -mtime +30 -delete 2>/dev/null
EOF

# Instalar nueva configuración
crontab temp_crontab
rm temp_crontab

echo "✅ Configuración de cron instalada exitosamente"
echo "📄 Backup del crontab anterior guardado como: crontab_backup_*.txt"
echo "🔍 Para verificar: crontab -l"

# =============================================
# CONFIGURACIÓN PARA WINDOWS (TASK SCHEDULER)
# =============================================

# Script PowerShell para configurar Task Scheduler
# configurar_tareas_windows.ps1

# Ejecutar como Administrador
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "Este script debe ejecutarse como Administrador" -ForegroundColor Red
    exit 1
}

$ProjectPath = $PSScriptRoot

# Crear tarea para generación de facturas (01:00 diario)
$action1 = New-ScheduledTaskAction -Execute "bash" -Argument "$ProjectPath\generador_facturas.sh"
$trigger1 = New-ScheduledTaskTrigger -Daily -At "01:00"
$settings1 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$principal1 = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount

Register-ScheduledTask -TaskName "MercadoIRSI_GenerarFacturas" -Action $action1 -Trigger $trigger1 -Settings $settings1 -Principal $principal1 -Description "Generación automática de facturas"

# Crear tarea para envío de correos (02:00 diario)
$action2 = New-ScheduledTaskAction -Execute "python" -Argument "$ProjectPath\enviador.py"
$trigger2 = New-ScheduledTaskTrigger -Daily -At "02:00"

Register-ScheduledTask -TaskName "MercadoIRSI_EnviarCorreos" -Action $action2 -Trigger $trigger2 -Settings $settings1 -Principal $principal1 -Description "Envío automático de facturas por correo"

# Crear tarea para gestión de usuarios (03:00 diario)
$action3 = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File $ProjectPath\usuarios.ps1"
$trigger3 = New-ScheduledTaskTrigger -Daily -At "03:00"

Register-ScheduledTask -TaskName "MercadoIRSI_GestionUsuarios" -Action $action3 -Trigger $trigger3 -Settings $settings1 -Principal $principal1 -Description "Gestión de usuarios temporales"

Write-Host "✅ Tareas programadas configuradas exitosamente" -ForegroundColor Green

# =============================================
# CONFIGURACIÓN MANUAL WINDOWS TASK SCHEDULER
# =============================================

# 1. Abrir Task Scheduler (taskschd.msc)
# 2. Crear Tarea Básica o Tarea...
# 3. Configurar los siguientes parámetros:

# TAREA 1: Generación de Facturas
# Nombre: MercadoIRSI_GenerarFacturas
# Disparador: Diario a las 01:00
# Acción: Iniciar programa
#   Programa: bash (o ruta completa a bash.exe)
#   Argumentos: generador_facturas.sh
#   Iniciar en: C:\ruta\del\proyecto

# TAREA 2: Envío de Correos
# Nombre: MercadoIRSI_EnviarCorreos
# Disparador: Diario a las 02:00
# Acción: Iniciar programa
#   Programa: python (o ruta completa a python.exe)
#   Argumentos: enviador.py
#   Iniciar en: C:\ruta\del\proyecto

# TAREA 3: Gestión de Usuarios
# Nombre: MercadoIRSI_GestionUsuarios
# Disparador: Diario a las 03:00
# Acción: Iniciar programa
#   Programa: powershell.exe
#   Argumentos: -File usuarios.ps1
#   Iniciar en: C:\ruta\del\proyecto

# =============================================
# MONITOREO Y LOGS
# =============================================

# Script para verificar estado de las tareas
# verificar_sistema.sh

#!/bin/bash
echo "=== VERIFICACIÓN DEL SISTEMA DE FACTURACIÓN ==="

# Verificar archivos necesarios
echo "📁 Verificando archivos del sistema..."
files_required=("generador_compras.py" "generador_facturas.sh" "enviador.py" "plantilla_factura_IRSI.tex")

for file in "${files_required[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file"
    else
        echo "❌ $file - FALTANTE"
    fi
done

# Verificar permisos de ejecución
echo -e "\n🔐 Verificando permisos..."
if [[ -x "generador_facturas.sh" ]]; then
    echo "✅ generador_facturas.sh ejecutable"
else
    echo "❌ generador_facturas.sh sin permisos de ejecución"
    echo "   Ejecutar: chmod +x generador_facturas.sh"
fi

# Verificar dependencias
echo -e "\n📦 Verificando dependencias..."

if command -v python3 &> /dev/null; then
    echo "✅ Python3 instalado: $(python3 --version)"
else
    echo "❌ Python3 no encontrado"
fi

if command -v pdflatex &> /dev/null; then
    echo "✅ pdflatex instalado: $(pdflatex --version | head -1)"
else
    echo "❌ pdflatex no encontrado"
fi

# Verificar módulos Python
echo -e "\n🐍 Verificando módulos Python..."
python3 -c "import faker, smtplib; print('✅ Módulos Python OK')" 2>/dev/null || echo "❌ Módulos Python faltantes"

# Verificar logs recientes
echo -e "\n📊 Estado de logs..."
if [[ -f "log_diario.log" ]]; then
    last_entry=$(tail -1 log_diario.log)
    echo "📝 Última entrada: $last_entry"
else
    echo "⚠️  No hay log diario"
fi

# Verificar cron jobs (Linux)
if command -v crontab &> /dev/null; then
    echo -e "\n⏰ Verificando cron jobs..."
    if crontab -l | grep -q "generador_facturas"; then
        echo "✅ Cron configurado"
    else
        echo "⚠️  Cron no configurado"
    fi
fi

echo -e "\n=== FIN DE VERIFICACIÓN ==="

# =============================================
# INSTALACIÓN COMPLETA DEL SISTEMA
# =============================================

# setup.sh - Script de instalación completa

#!/bin/bash
set -e

echo "🚀 INSTALACIÓN DEL SISTEMA DE FACTURACIÓN MERCADO IRSI"

# Crear directorios necesarios
echo "📁 Creando estructura de directorios..."
mkdir -p datos logs facturas_pdf

# Dar permisos de ejecución
echo "🔐 Configurando permisos..."
chmod +x generador_facturas.sh
chmod +x cron_job.sh

# Verificar dependencias
echo "📦 Verificando dependencias..."

# Python y módulos
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    echo "   Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "   CentOS/RHEL: sudo yum install python3 python3-pip"
    exit 1
fi

# Instalar módulos Python si no están
python3 -c "import faker" 2>/dev/null || pip3 install faker
python3 -c "import smtplib" 2>/dev/null || echo "✅ smtplib ya incluido en Python"

# LaTeX
if ! command -v pdflatex &> /dev/null; then
    echo "❌ pdflatex no está instalado"
    echo "   Ubuntu/Debian: sudo apt install texlive-latex-base texlive-latex-extra"
    echo "   CentOS/RHEL: sudo yum install texlive texlive-latex"
    exit 1
fi

# Generar datos de prueba
echo "🧪 Generando datos de prueba..."
python3 generador_compras.py 5

# Configurar cron (opcional)
read -p "¿Desea configurar las tareas automáticas? (y/n): " configure_cron
if [[ $configure_cron == "y" || $configure_cron == "Y" ]]; then
    ./instalar_cron.sh
fi

echo "✅ Instalación completada"
echo "📚 Consulte README.md para instrucciones de uso"

# =============================================
# DOCUMENTACIÓN DE USO
# =============================================

# README - Guía de uso del sistema

SISTEMA DE FACTURACIÓN AUTOMATIZADO - MERCADO IRSI
==================================================

ESTRUCTURA DEL PROYECTO:
- generador_compras.py   : Simula transacciones de clientes
- plantilla_factura_IRSI.tex : Plantilla LaTeX para facturas
- generador_facturas.sh  : Genera PDFs desde CSV
- enviador.py           : Envía facturas por correo
- usuarios.ps1          : Gestiona usuarios temporales (Windows)
- cron_job.sh           : Orquesta todo el proceso

USO MANUAL:
1. Generar compras: python3 generador_compras.py 10
2. Generar facturas: ./generador_facturas.sh
3. Enviar correos: python3 enviador.py

USO AUTOMATIZADO:
- Linux: Configurar cron con instalar_cron.sh
- Windows: Ejecutar configurar_tareas_windows.ps1

PERSONALIZACIÓN:
- Editar SMTP_CONFIG en enviador.py
- Modificar plantilla_factura_IRSI.tex
- Ajustar horarios en configuración de cron

LOGS:
- log_diario.log: Registro general
- log_envios.csv: Resultados de envío
- cron_execution.log: Ejecución automatizada
