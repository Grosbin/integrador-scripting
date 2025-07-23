#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar configuración SMTP
Verifica que las credenciales sean correctas antes de ejecutar el enviador principal
"""

import smtplib
import sys
from pathlib import Path

def test_smtp_connection():
    """Prueba la conexión SMTP con las credenciales configuradas"""
    
    try:
        # Importar configuración
        config_file = Path("config_smtp.py")
        if not config_file.exists():
            print("❌ Error: Archivo config_smtp.py no encontrado")
            return False
        
        # Importar configuración dinámicamente
        import importlib.util
        spec = importlib.util.spec_from_file_location("config_smtp", config_file)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        
        smtp_config = config_module.SMTP_CONFIG
        
        print("🔧 Probando configuración SMTP...")
        print(f"   Servidor: {smtp_config['server']}")
        print(f"   Puerto: {smtp_config['port']}")
        print(f"   Usuario: {smtp_config['user']}")
        print(f"   TLS: {'Sí' if smtp_config['use_tls'] else 'No'}")
        
        # Probar conexión
        print("\n📡 Conectando al servidor SMTP...")
        server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
        
        if smtp_config['use_tls']:
            print("🔒 Iniciando TLS...")
            server.starttls()
        
        print("🔐 Autenticando...")
        server.login(smtp_config['user'], smtp_config['password'])
        
        print("✅ ¡Autenticación exitosa!")
        server.quit()
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Error de autenticación: {e}")
        print("\n💡 Posibles soluciones:")
        print("   1. Verifica que la verificación en 2 pasos esté activada")
        print("   2. Genera una nueva contraseña de aplicación")
        print("   3. Asegúrate de usar la contraseña de aplicación, no la normal")
        return False
        
    except smtplib.SMTPConnectError as e:
        print(f"❌ Error de conexión: {e}")
        print("   Verifica tu conexión a internet y la configuración del servidor")
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    """Función principal"""
    print("=== PRUEBA DE CONFIGURACIÓN SMTP ===\n")
    
    success = test_smtp_connection()
    
    if success:
        print("\n🎉 ¡Configuración SMTP correcta!")
        print("   Puedes ejecutar enviador.py con confianza")
    else:
        print("\n⚠️  Configuración SMTP incorrecta")
        print("   Revisa config_smtp.py antes de ejecutar enviador.py")
        sys.exit(1)

if __name__ == "__main__":
    main() 