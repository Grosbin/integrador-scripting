#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Envío Automatizado de Facturas por Correo
Procesa archivo pendientes_envio.csv y envía facturas por correo electrónico
"""

import csv
import smtplib
import os
import re
import sys
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import logging

# Configuración de correo (ajustar según proveedor)
SMTP_CONFIG = {
    'server': 'smtp.gmail.com',
    'port': 587,
    'user': 'tu_correo@gmail.com',  # Cambiar por tu correo
    'password': 'tu_password_app',   # Cambiar por tu contraseña de aplicación
    'use_tls': True
}

# Archivos de configuración
PENDING_FILE = 'pendientes_envio.csv'
LOG_ENVIOS = 'log_envios.csv'
LOG_DIARIO = 'log_diario.log'

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('enviador.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def validate_email(email):
    """Valida formato de correo electrónico usando regex"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def create_email_message(recipient, pdf_path, invoice_id):
    """Crea mensaje de correo con factura adjunta"""
    
    # Crear mensaje multipart
    msg = MIMEMultipart()
    msg['From'] = SMTP_CONFIG['user']
    msg['To'] = recipient
    msg['Subject'] = f'Factura Electrónica #{invoice_id} - Mercado IRSI'
    
    # Cuerpo del mensaje
    body = f"""
Estimado/a Cliente,

Adjunto encontrará su factura electrónica #{invoice_id} correspondiente a su compra en Mercado IRSI.

Detalles de la transacción:
- ID de Transacción: {invoice_id}
- Fecha de emisión: {datetime.datetime.now().strftime('%Y-%m-%d')}

Gracias por su preferencia.

Atentamente,
Mercado IRSI
Sistema Automatizado de Facturación

---
Este es un correo automático, por favor no responda.
Para consultas: soporte@mercadoirsi.com
Web: www.mercadoirsi.com
"""
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # Adjuntar PDF
    try:
        with open(pdf_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(pdf_path)}'
            )
            msg.attach(part)
        
        return msg
    except FileNotFoundError:
        logging.error(f"Archivo PDF no encontrado: {pdf_path}")
        return None
    except Exception as e:
        logging.error(f"Error adjuntando PDF {pdf_path}: {str(e)}")
        return None

def send_email(message, recipient):
    """Envía correo electrónico usando SMTP"""
    try:
        # Conectar al servidor SMTP
        server = smtplib.SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port'])
        
        if SMTP_CONFIG['use_tls']:
            server.starttls()
        
        # Autenticarse
        server.login(SMTP_CONFIG['user'], SMTP_CONFIG['password'])
        
        # Enviar mensaje
        text = message.as_string()
        server.sendmail(SMTP_CONFIG['user'], recipient, text)
        server.quit()
        
        return True, "Enviado exitosamente"
    
    except smtplib.SMTPAuthenticationError:
        return False, "Error de autenticación SMTP"
    except smtplib.SMTPRecipientsRefused:
        return False, "Destinatario rechazado"
    except smtplib.SMTPServerDisconnected:
        return False, "Servidor SMTP desconectado"
    except Exception as e:
        return False, f"Error SMTP: {str(e)}"

def log_envio(pdf_file, email, status):
    """Registra resultado de envío en log CSV"""
    with open(LOG_ENVIOS, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([pdf_file, email, status])

def log_daily(message):
    """Registra mensaje en log diario"""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_DIARIO, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp} [ENVIADOR] {message}\n")

def update_pending_file(successful_rows):
    """Actualiza archivo de pendientes eliminando líneas exitosas"""
    if not os.path.exists(PENDING_FILE):
        return
    
    # Leer todas las líneas
    with open(PENDING_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Filtrar líneas exitosas
    remaining_lines = []
    for i, line in enumerate(lines):
        if i not in successful_rows:
            remaining_lines.append(line)
    
    # Escribir líneas restantes
    with open(PENDING_FILE, 'w', encoding='utf-8') as f:
        f.writelines(remaining_lines)

def process_pending_emails():
    """Procesa archivo de pendientes y envía correos"""
    
    if not os.path.exists(PENDING_FILE):
        logging.error(f"Archivo de pendientes no encontrado: {PENDING_FILE}")
        return
    
    # Inicializar log de envíos si no existe
    if not os.path.exists(LOG_ENVIOS):
        with open(LOG_ENVIOS, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['pdf_file', 'email', 'status'])
    
    successful_rows = []
    total_processed = 0
    successful_count = 0
    failed_count = 0
    
    log_daily("=== INICIO DE ENVÍO DE CORREOS ===")
    
    try:
        with open(PENDING_FILE, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            
            for row_num, row in enumerate(reader):
                if len(row) < 2:
                    continue
                
                pdf_path = row[0].strip()
                email = row[1].strip()
                total_processed += 1
                
                logging.info(f"Procesando {total_processed}: {pdf_path} -> {email}")
                
                # Validar email
                if not validate_email(email):
                    logging.error(f"Email inválido: {email}")
                    log_envio(pdf_path, email, "Email inválido")
                    failed_count += 1
                    continue
                
                # Verificar que el PDF existe
                if not os.path.exists(pdf_path):
                    logging.error(f"PDF no encontrado: {pdf_path}")
                    log_envio(pdf_path, email, "PDF no encontrado")
                    failed_count += 1
                    continue
                
                # Extraer ID de factura del nombre del archivo
                invoice_id = os.path.basename(pdf_path).replace('factura_', '').replace('.pdf', '')
                
                # Crear mensaje
                message = create_email_message(email, pdf_path, invoice_id)
                if message is None:
                    log_envio(pdf_path, email, "Error creando mensaje")
                    failed_count += 1
                    continue
                
                # Enviar correo
                success, result = send_email(message, email)
                
                if success:
                    logging.info(f"✅ Enviado exitosamente: {pdf_path} -> {email}")
                    log_envio(pdf_path, email, "exitoso")
                    successful_rows.append(row_num)
                    successful_count += 1
                else:
                    logging.error(f"❌ Error enviando: {pdf_path} -> {email} - {result}")
                    log_envio(pdf_path, email, "fallido")
                    failed_count += 1
    
    except Exception as e:
        logging.error(f"Error procesando archivo de pendientes: {str(e)}")
        return
    
    # Actualizar archivo de pendientes eliminando líneas exitosas
    update_pending_file(successful_rows)
    
    # Log final
    log_daily(f"Total procesados: {total_processed}")
    log_daily(f"Exitosos: {successful_count}")
    log_daily(f"Fallidos: {failed_count}")
    log_daily("=== FIN DE ENVÍO DE CORREOS ===")
    
    # Resumen en pantalla
    print(f"\n=== RESUMEN DE ENVÍO ===")
    print(f"Total procesados: {total_processed}")
    print(f"Exitosos: {successful_count}")
    print(f"Fallidos: {failed_count}")
    print(f"Log de envíos: {LOG_ENVIOS}")
    
    return successful_count, failed_count, total_processed

def generate_daily_report():
    """Genera reporte diario usando awk sobre log_envios.csv"""
    
    if not os.path.exists(LOG_ENVIOS):
        logging.warning("No hay log de envíos para generar reporte")
        return
    
    log_daily("=== GENERANDO REPORTE DIARIO ===")
    
    try:
        # Leer estadísticas del log de envíos
        total_emails = 0
        successful_emails = 0
        failed_emails = 0
        
        with open(LOG_ENVIOS, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                total_emails += 1
                if row['status'] == 'exitoso':
                    successful_emails += 1
                else:
                    failed_emails += 1
        
        # Leer estadísticas de ventas del log diario
        total_vendido = 0
        pagos_completos = 0
        
        # Buscar información de montos en el log diario
        if os.path.exists(LOG_DIARIO):
            with open(LOG_DIARIO, 'r', encoding='utf-8') as f:
                for line in f:
                    if 'Monto total procesado' in line:
                        # Extraer monto del log
                        import re
                        match = re.search(r'₡(\d+)', line)
                        if match:
                            total_vendido = int(match.group(1))
                    elif 'Pagos completos' in line:
                        # Extraer número de pagos completos
                        match = re.search(r'Pagos completos: (\d+)', line)
                        if match:
                            pagos_completos = int(match.group(1))
        
        # Crear reporte
        report = f"""
=== REPORTE DIARIO DE FACTURACIÓN ===
Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ENVÍO DE CORREOS:
- Total de correos procesados: {total_emails}
- Envíos exitosos: {successful_emails}
- Envíos fallidos: {failed_emails}
- Tasa de éxito: {(successful_emails/total_emails*100) if total_emails > 0 else 0:.1f}%

VENTAS:
- Total vendido: ₡{total_vendido:,}
- Pagos completos: {pagos_completos}

ARCHIVOS GENERADOS:
- Log de envíos: {LOG_ENVIOS}
- Log diario: {LOG_DIARIO}

=== FIN DEL REPORTE ===
"""
        
        # Guardar reporte
        report_file = f"reporte_diario_{datetime.datetime.now().strftime('%Y%m%d')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        log_daily(f"Reporte diario generado: {report_file}")
        
        # Mostrar reporte en pantalla
        print(report)
        
        return report_file
        
    except Exception as e:
        logging.error(f"Error generando reporte diario: {str(e)}")
        return None

def send_admin_report(report_file):
    """Envía reporte diario al administrador"""
    
    admin_email = "admin@mercadoirsi.com"  # Cambiar por email del admin
    
    if not report_file or not os.path.exists(report_file):
        logging.error("No hay reporte para enviar al administrador")
        return
    
    try:
        # Crear mensaje para administrador
        msg = MIMEMultipart()
        msg['From'] = SMTP_CONFIG['user']
        msg['To'] = admin_email
        msg['Subject'] = f'Reporte Diario de Facturación - {datetime.datetime.now().strftime("%Y-%m-%d")}'
        
        # Leer contenido del reporte
        with open(report_file, 'r', encoding='utf-8') as f:
            report_content = f.read()
        
        body = f"""
Estimado Administrador,

Adjunto encontrará el reporte diario de facturación y envío de correos.

{report_content}

Atentamente,
Sistema Automatizado de Facturación
Mercado IRSI
"""
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Adjuntar archivo de reporte
        with open(report_file, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(report_file)}'
            )
            msg.attach(part)
        
        # Enviar
        success, result = send_email(msg, admin_email)
        
        if success:
            logging.info(f"✅ Reporte enviado al administrador: {admin_email}")
            log_daily(f"Reporte enviado al administrador: {admin_email}")
        else:
            logging.error(f"❌ Error enviando reporte al administrador: {result}")
            log_daily(f"Error enviando reporte al administrador: {result}")
    
    except Exception as e:
        logging.error(f"Error enviando reporte al administrador: {str(e)}")

def main():
    """Función principal"""
    
    logging.info("=== INICIANDO SISTEMA DE ENVÍO DE FACTURAS ===")
    
    # Verificar configuración SMTP
    if SMTP_CONFIG['user'] == 'tu_correo@gmail.com':
        print("⚠️  ADVERTENCIA: Debe configurar las credenciales SMTP en SMTP_CONFIG")
        print("   Edite las variables 'user' y 'password' con sus credenciales reales")
        
        # Para demostración, usar modo simulado
        print("   Ejecutando en modo SIMULADO (no se enviarán correos reales)")
        global send_email
        send_email = lambda msg, recipient: (True, "Simulado - no enviado")
    
    # Procesar envíos pendientes
    try:
        successful, failed, total = process_pending_emails()
        
        # Generar y enviar reporte diario
        report_file = generate_daily_report()
        if report_file:
            send_admin_report(report_file)
        
        logging.info("=== SISTEMA DE ENVÍO COMPLETADO ===")
        
        # Código de salida
        if failed > 0:
            sys.exit(1)  # Indica que hubo errores
        else:
            sys.exit(0)  # Éxito completo
            
    except KeyboardInterrupt:
        logging.info("Proceso interrumpido por el usuario")
        sys.exit(130)
    except Exception as e:
        logging.error(f"Error fatal en el sistema: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()