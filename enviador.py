#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Envío Automatizado de Facturas por Correo
Procesa archivo pendientes_envio.csv y envía facturas por correo electrónico

Autor: Sistema de Facturación Mercado IRSI
Versión: 2.0
Fecha: 2024
"""

import csv
import smtplib
import os
import re
import sys
import datetime
import json
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class EmailConfig:
    """Configuración de correo electrónico"""
    server: str
    port: int
    user: str
    password: str
    use_tls: bool


@dataclass
class PathConfig:
    """Configuración de rutas del sistema"""
    pending_file: str
    log_envios: str
    log_diario: str
    log_enviador: str
    reports_dir: str


class ConfigManager:
    """Gestor de configuración del sistema"""
    
    def __init__(self, config_dir: str = "."):
        self.config_dir = Path(config_dir)
        self.smtp_config = self._load_smtp_config()
        self.path_config = self._load_path_config()
        self.admin_email = self._load_admin_email()
    
    def _load_smtp_config(self) -> EmailConfig:
        """Carga configuración SMTP desde archivo externo"""
        config_file = self.config_dir / "config_smtp.py"
        
        if not config_file.exists():
            raise FileNotFoundError(
                f"Archivo de configuración SMTP no encontrado: {config_file}\n"
                "Ejecute setup.sh para crear los archivos de configuración"
            )
        
        # Importar configuración dinámicamente
        import importlib.util
        spec = importlib.util.spec_from_file_location("config_smtp", config_file)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        
        smtp_dict = config_module.SMTP_CONFIG
        
        # Validar configuración
        if smtp_dict['user'] == 'tu_correo@gmail.com':
            raise ValueError(
                "Credenciales SMTP no configuradas. "
                "Edite config_smtp.py con sus credenciales reales"
            )
        
        return EmailConfig(**smtp_dict)
    
    def _load_path_config(self) -> PathConfig:
        """Carga configuración de rutas desde archivo externo"""
        config_file = self.config_dir / "config.sh"
        
        if not config_file.exists():
            # Usar rutas por defecto si no existe configuración
            return PathConfig(
                pending_file="temp/pendientes_envio.csv",
                log_envios="logs/envios/log_envios.csv",
                log_diario="logs/log_diario.log",
                log_enviador="logs/envios/enviador.log",
                reports_dir="logs/reportes"
            )
        
        # Leer configuración desde archivo bash
        paths = {}
        with open(config_file, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    paths[key.strip()] = value.strip().strip('"')
        
        return PathConfig(
            pending_file=paths.get('PENDING_FILE', 'temp/pendientes_envio.csv'),
            log_envios=paths.get('SHIPMENT_LOG', 'logs/envios/log_envios.csv'),
            log_diario=paths.get('DAILY_LOG', 'logs/log_diario.log'),
            log_enviador="logs/envios/enviador.log",
            reports_dir=paths.get('REPORTS_DIR', 'logs/reportes')
        )
    
    def _load_admin_email(self) -> str:
        """Carga email del administrador desde configuración"""
        config_file = self.config_dir / "config.sh"
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if 'ADMIN_EMAIL=' in line:
                        return line.split('=', 1)[1].strip().strip('"')
        
        return "admin@mercadoirsi.com"


class EmailValidator:
    """Validador de correos electrónicos"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida formato de correo electrónico usando regex"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None


class EmailMessageBuilder:
    """Constructor de mensajes de correo"""
    
    def __init__(self, smtp_config: EmailConfig):
        self.smtp_config = smtp_config
    
    def create_invoice_message(self, recipient: str, pdf_path: str, invoice_id: str) -> Optional[MIMEMultipart]:
        """Crea mensaje de correo con factura adjunta"""
        
        msg = MIMEMultipart()
        msg['From'] = self.smtp_config.user
        msg['To'] = recipient
        msg['Subject'] = f'Factura Electrónica #{invoice_id} - Mercado IRSI'
        
        body = self._create_email_body(invoice_id)
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Adjuntar PDF
        if not self._attach_pdf(msg, pdf_path):
            return None
        
        return msg
    
    def create_admin_report_message(self, admin_email: str, report_file: str) -> Optional[MIMEMultipart]:
        """Crea mensaje de reporte para administrador"""
        
        msg = MIMEMultipart()
        msg['From'] = self.smtp_config.user
        msg['To'] = admin_email
        msg['Subject'] = f'Reporte Diario de Facturación - {datetime.datetime.now().strftime("%Y-%m-%d")}'
        
        body = self._create_admin_report_body(report_file)
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Adjuntar archivo de reporte
        if not self._attach_pdf(msg, report_file):
            return None
        
        return msg
    
    def _create_email_body(self, invoice_id: str) -> str:
        """Crea el cuerpo del mensaje para facturas"""
        return f"""
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
    
    def _create_admin_report_body(self, report_file: str) -> str:
        """Crea el cuerpo del mensaje para reportes de administrador"""
        return f"""
Estimado Administrador,

Adjunto encontrará el reporte diario de facturación y envío de correos.

Atentamente,
Sistema Automatizado de Facturación
Mercado IRSI
"""
    
    def _attach_pdf(self, msg: MIMEMultipart, file_path: str) -> bool:
        """Adjunta archivo PDF al mensaje"""
        try:
            with open(file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(file_path)}'
                )
                msg.attach(part)
            return True
        except FileNotFoundError:
            logging.error(f"Archivo no encontrado: {file_path}")
            return False
        except Exception as e:
            logging.error(f"Error adjuntando archivo {file_path}: {str(e)}")
            return False


class EmailSender:
    """Enviador de correos electrónicos"""
    
    def __init__(self, smtp_config: EmailConfig):
        self.smtp_config = smtp_config
    
    def send_email(self, message: MIMEMultipart, recipient: str) -> Tuple[bool, str]:
        """Envía correo electrónico usando SMTP"""
        try:
            server = smtplib.SMTP(self.smtp_config.server, self.smtp_config.port)
            
            if self.smtp_config.use_tls:
                server.starttls()
            
            server.login(self.smtp_config.user, self.smtp_config.password)
            
            text = message.as_string()
            server.sendmail(self.smtp_config.user, recipient, text)
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


class LogManager:
    """Gestor de logs del sistema"""
    
    def __init__(self, path_config: PathConfig):
        self.path_config = path_config
        self._setup_logging()
    
    def _setup_logging(self):
        """Configura el sistema de logging"""
        # Crear directorio de logs si no existe
        log_dir = Path(self.path_config.log_enviador).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(self.path_config.log_enviador, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    def log_shipment(self, pdf_file: str, email: str, status: str):
        """Registra resultado de envío en log CSV"""
        # Crear directorio si no existe
        log_dir = Path(self.path_config.log_envios).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        with open(self.path_config.log_envios, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([pdf_file, email, status])
    
    def log_daily(self, message: str):
        """Registra mensaje en log diario"""
        # Crear directorio si no existe
        log_dir = Path(self.path_config.log_diario).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.path_config.log_diario, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} [ENVIADOR] {message}\n")


class PendingFileManager:
    """Gestor del archivo de pendientes"""
    
    def __init__(self, pending_file: str):
        self.pending_file = pending_file
    
    def update_pending_file(self, successful_rows: List[int]):
        """Actualiza archivo de pendientes eliminando líneas exitosas"""
        if not os.path.exists(self.pending_file):
            return
        
        with open(self.pending_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        remaining_lines = [line for i, line in enumerate(lines) if i not in successful_rows]
        
        with open(self.pending_file, 'w', encoding='utf-8') as f:
            f.writelines(remaining_lines)


class ReportGenerator:
    """Generador de reportes diarios"""
    
    def __init__(self, path_config: PathConfig, log_manager: LogManager):
        self.path_config = path_config
        self.log_manager = log_manager
    
    def generate_daily_report(self) -> Optional[str]:
        """Genera reporte diario usando datos de logs"""
        
        if not os.path.exists(self.path_config.log_envios):
            logging.warning("No hay log de envíos para generar reporte")
            return None
        
        self.log_manager.log_daily("=== GENERANDO REPORTE DIARIO ===")
        
        try:
            stats = self._calculate_statistics()
            report = self._create_report_content(stats)
            report_file = self._save_report(report)
            
            self.log_manager.log_daily(f"Reporte diario generado: {report_file}")
            print(report)
            
            return report_file
            
        except Exception as e:
            logging.error(f"Error generando reporte diario: {str(e)}")
            return None
    
    def _calculate_statistics(self) -> Dict:
        """Calcula estadísticas de envíos y ventas"""
        stats = {
            'total_emails': 0,
            'successful_emails': 0,
            'failed_emails': 0,
            'total_vendido': 0,
            'pagos_completos': 0
        }
        
        # Estadísticas de envíos
        if os.path.exists(self.path_config.log_envios):
            with open(self.path_config.log_envios, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    stats['total_emails'] += 1
                    if row['status'] == 'exitoso':
                        stats['successful_emails'] += 1
                    else:
                        stats['failed_emails'] += 1
        
        # Estadísticas de ventas desde log diario
        if os.path.exists(self.path_config.log_diario):
            with open(self.path_config.log_diario, 'r', encoding='utf-8') as f:
                for line in f:
                    if 'Monto total procesado' in line:
                        match = re.search(r'L(\d+)', line)
                        if match:
                            stats['total_vendido'] = int(match.group(1))
                    elif 'Pagos completos' in line:
                        match = re.search(r'Pagos completos: (\d+)', line)
                        if match:
                            stats['pagos_completos'] = int(match.group(1))
        
        return stats
    
    def _create_report_content(self, stats: Dict) -> str:
        """Crea contenido del reporte"""
        success_rate = (stats['successful_emails']/stats['total_emails']*100) if stats['total_emails'] > 0 else 0
        
        return f"""
=== REPORTE DIARIO DE FACTURACIÓN ===
Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ENVÍO DE CORREOS:
- Total de correos procesados: {stats['total_emails']}
- Envíos exitosos: {stats['successful_emails']}
- Envíos fallidos: {stats['failed_emails']}
- Tasa de éxito: {success_rate:.1f}%

VENTAS:
- Total vendido: L{stats['total_vendido']:,}
- Pagos completos: {stats['pagos_completos']}

ARCHIVOS GENERADOS:
- Log de envíos: {self.path_config.log_envios}
- Log diario: {self.path_config.log_diario}

=== FIN DEL REPORTE ===
"""
    
    def _save_report(self, report_content: str) -> str:
        """Guarda el reporte en archivo"""
        # Crear directorio si no existe
        reports_dir = Path(self.path_config.reports_dir)
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = reports_dir / f"reporte_diario_{datetime.datetime.now().strftime('%Y%m%d')}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return str(report_file)


class EmailProcessor:
    """Procesador principal de envío de correos"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.path_config = config_manager.path_config
        self.smtp_config = config_manager.smtp_config
        
        # Inicializar componentes
        self.log_manager = LogManager(self.path_config)
        self.email_validator = EmailValidator()
        self.message_builder = EmailMessageBuilder(self.smtp_config)
        self.email_sender = EmailSender(self.smtp_config)
        self.pending_manager = PendingFileManager(self.path_config.pending_file)
        self.report_generator = ReportGenerator(self.path_config, self.log_manager)
    
    def process_pending_emails(self) -> Tuple[int, int, int]:
        """Procesa archivo de pendientes y envía correos"""
        
        if not os.path.exists(self.path_config.pending_file):
            logging.error(f"Archivo de pendientes no encontrado: {self.path_config.pending_file}")
            return 0, 0, 0
        
        # Inicializar log de envíos si no existe
        self._initialize_shipment_log()
        
        successful_rows = []
        total_processed = 0
        successful_count = 0
        failed_count = 0
        
        self.log_manager.log_daily("=== INICIO DE ENVÍO DE CORREOS ===")
        
        try:
            with open(self.path_config.pending_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                
                for row_num, row in enumerate(reader):
                    if len(row) < 2:
                        continue
                    
                    pdf_path = row[0].strip()
                    email = row[1].strip()
                    total_processed += 1
                    
                    logging.info(f"Procesando {total_processed}: {pdf_path} -> {email}")
                    
                    # Procesar envío
                    success = self._process_single_email(pdf_path, email, row_num, successful_rows)
                    
                    if success:
                        successful_count += 1
                    else:
                        failed_count += 1
        
        except Exception as e:
            logging.error(f"Error procesando archivo de pendientes: {str(e)}")
            return 0, 0, 0
        
        # Actualizar archivo de pendientes
        self.pending_manager.update_pending_file(successful_rows)
        
        # Log final
        self._log_final_summary(total_processed, successful_count, failed_count)
        
        return successful_count, failed_count, total_processed
    
    def _initialize_shipment_log(self):
        """Inicializa el archivo de log de envíos"""
        if not os.path.exists(self.path_config.log_envios):
            log_dir = Path(self.path_config.log_envios).parent
            log_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.path_config.log_envios, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['pdf_file', 'email', 'status'])
    
    def _process_single_email(self, pdf_path: str, email: str, row_num: int, successful_rows: List[int]) -> bool:
        """Procesa un solo envío de correo"""
        
        # Validar email
        if not self.email_validator.validate_email(email):
            logging.error(f"Email inválido: {email}")
            self.log_manager.log_shipment(pdf_path, email, "Email inválido")
            return False
        
        # Verificar que el PDF existe
        if not os.path.exists(pdf_path):
            logging.error(f"PDF no encontrado: {pdf_path}")
            self.log_manager.log_shipment(pdf_path, email, "PDF no encontrado")
            return False
        
        # Extraer ID de factura del nombre del archivo
        invoice_id = os.path.basename(pdf_path).replace('factura_', '').replace('.pdf', '')
        
        # Crear mensaje
        message = self.message_builder.create_invoice_message(email, pdf_path, invoice_id)
        if message is None:
            self.log_manager.log_shipment(pdf_path, email, "Error creando mensaje")
            return False
        
        # Enviar correo
        success, result = self.email_sender.send_email(message, email)
        
        if success:
            logging.info(f"Enviado exitosamente: {pdf_path} -> {email}")
            self.log_manager.log_shipment(pdf_path, email, "exitoso")
            successful_rows.append(row_num)
            return True
        else:
            logging.error(f"Error enviando: {pdf_path} -> {email} - {result}")
            self.log_manager.log_shipment(pdf_path, email, "fallido")
            return False
    
    def _log_final_summary(self, total: int, successful: int, failed: int):
        """Registra resumen final del procesamiento"""
        self.log_manager.log_daily(f"Total procesados: {total}")
        self.log_manager.log_daily(f"Exitosos: {successful}")
        self.log_manager.log_daily(f"Fallidos: {failed}")
        self.log_manager.log_daily("=== FIN DE ENVÍO DE CORREOS ===")
        
        # Resumen en pantalla
        print(f"\n=== RESUMEN DE ENVÍO ===")
        print(f"Total procesados: {total}")
        print(f"Exitosos: {successful}")
        print(f"Fallidos: {failed}")
        print(f"Log de envíos: {self.path_config.log_envios}")
    
    def send_admin_report(self, report_file: str):
        """Envía reporte diario al administrador"""
        
        if not report_file or not os.path.exists(report_file):
            logging.error("No hay reporte para enviar al administrador")
            return
        
        try:
            message = self.message_builder.create_admin_report_message(
                self.config_manager.admin_email, report_file
            )
            
            if message is None:
                logging.error("Error creando mensaje para administrador")
                return
            
            success, result = self.email_sender.send_email(message, self.config_manager.admin_email)
            
            if success:
                logging.info(f"Reporte enviado al administrador: {self.config_manager.admin_email}")
                self.log_manager.log_daily(f"Reporte enviado al administrador: {self.config_manager.admin_email}")
            else:
                logging.error(f"Error enviando reporte al administrador: {result}")
                self.log_manager.log_daily(f"Error enviando reporte al administrador: {result}")
        
        except Exception as e:
            logging.error(f"Error enviando reporte al administrador: {str(e)}")


def main():
    """Función principal del sistema de envío"""
    
    try:
        # Cargar configuración
        config_manager = ConfigManager()
        
        # Crear procesador de correos
        processor = EmailProcessor(config_manager)
        
        logging.info("=== INICIANDO SISTEMA DE ENVÍO DE FACTURAS ===")
        
        # Procesar envíos pendientes
        successful, failed, total = processor.process_pending_emails()
        
        # Generar y enviar reporte diario
        report_file = processor.report_generator.generate_daily_report()
        if report_file:
            processor.send_admin_report(report_file)
        
        logging.info("=== SISTEMA DE ENVÍO COMPLETADO ===")
        
        # Código de salida
        if failed > 0:
            sys.exit(1)  # Indica que hubo errores
        else:
            sys.exit(0)  # Éxito completo
            
    except KeyboardInterrupt:
        logging.info("Proceso interrumpido por el usuario")
        sys.exit(130)
    except FileNotFoundError as e:
        print(f"Error de configuracion: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error de configuracion: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error fatal en el sistema: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()