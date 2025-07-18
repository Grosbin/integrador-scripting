#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Generación de Compras Simuladas
Simula transacciones comerciales usando Faker y las exporta a CSV
"""

import csv
import random
import datetime
from faker import Faker
import os
import sys

# Configuración inicial
fake = Faker('es_ES')  # Configurar para español
Faker.seed(0)
random.seed(0)

def generar_id_transaccion():
    """Genera un ID único de transacción"""
    return random.randint(100000, 999999)

def generar_ip():
    """Genera una IP aleatoria"""
    return f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"

def generar_compra():
    """Genera una compra simulada con todos los campos requeridos"""
    
    # Simular errores aleatorios (5% de probabilidad)
    if random.random() < 0.05:
        raise Exception("Error simulado en la generación de compra")
    
    # Generar datos del cliente
    nombre = fake.name()
    correo = fake.email()
    telefono = fake.phone_number()
    direccion = fake.address().replace('\n', ', ')
    ciudad = fake.city()
    
    # Generar datos de la compra
    id_transaccion = generar_id_transaccion()
    cantidad = random.randint(1, 10)
    monto = random.randint(5000, 100000)  # Montos en colones
    
    # Tipo de pago
    pago = random.choice(['Pago completo', 'Pago parcial'])
    
    # Estado del pago (90% exitoso, 10% fallido)
    estado_pago = 'Exitoso' if random.random() < 0.9 else 'Fallido'
    
    # IP y timestamp
    ip = generar_ip()
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    fecha_emision = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # Observaciones aleatorias
    observaciones_posibles = [
        "Cliente nuevo",
        "Cliente frecuente",
        "Promoción aplicada",
        "Descuento especial",
        "Compra regular",
        "Cliente VIP"
    ]
    observaciones = f'"{random.choice(observaciones_posibles)}"'
    
    return {
        'id_transaccion': id_transaccion,
        'fecha_emision': fecha_emision,
        'nombre': nombre,
        'correo': correo,
        'telefono': telefono,
        'direccion': direccion,
        'ciudad': ciudad,
        'cantidad': cantidad,
        'monto': monto,
        'pago': pago,
        'estado_pago': estado_pago,
        'ip': ip,
        'timestamp': timestamp,
        'observaciones': observaciones
    }

def generar_lote_compras(num_compras=10, archivo_salida=None):
    """Genera un lote de compras y las guarda en CSV"""
    
    if archivo_salida is None:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        archivo_salida = f'compras_lote_{timestamp}.csv'
    
    compras = []
    errores = []
    
    print(f"Generando {num_compras} compras simuladas...")
    
    for i in range(num_compras):
        try:
            compra = generar_compra()
            compras.append(compra)
            print(f"Compra {i+1}/{num_compras} generada: ID {compra['id_transaccion']}")
        except Exception as e:
            error_msg = f"Error en compra {i+1}: {str(e)}"
            errores.append(error_msg)
            print(error_msg)
    
    # Guardar compras en CSV
    if compras:
        with open(archivo_salida, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'id_transaccion', 'fecha_emision', 'nombre', 'correo', 
                'telefono', 'direccion', 'ciudad', 'cantidad', 'monto', 
                'pago', 'estado_pago', 'ip', 'timestamp', 'observaciones'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(compras)
        
        print(f"\n✅ {len(compras)} compras guardadas en {archivo_salida}")
    
    # Guardar errores si los hay
    if errores:
        archivo_errores = f'errores_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        with open(archivo_errores, 'w', encoding='utf-8') as f:
            f.write('\n'.join(errores))
        print(f"⚠️  {len(errores)} errores guardados en {archivo_errores}")
    
    return archivo_salida, len(compras), len(errores)

def main():
    """Función principal"""
    # Crear directorio de salida si no existe
    if not os.path.exists('datos'):
        os.makedirs('datos')
    
    # Cambiar al directorio de datos
    os.chdir('datos')
    
    # Obtener número de compras desde argumentos o usar valor por defecto
    num_compras = 10
    if len(sys.argv) > 1:
        try:
            num_compras = int(sys.argv[1])
        except ValueError:
            print("Error: El número de compras debe ser un entero")
            sys.exit(1)
    
    # Generar lote de compras
    archivo, exitosas, errores = generar_lote_compras(num_compras)
    
    # Resumen
    print(f"\n=== RESUMEN DE GENERACIÓN ===")
    print(f"Compras exitosas: {exitosas}")
    print(f"Errores: {errores}")
    print(f"Archivo generado: {archivo}")
    
    # Generar archivo de empleados de ejemplo para temporadas altas
    generar_empleados_ejemplo()

def generar_empleados_ejemplo():
    """Genera un archivo de empleados de ejemplo para el módulo de PowerShell"""
    empleados = []
    
    for i in range(5):
        empleado = {
            'nombre_completo': fake.name(),
            'correo': fake.email(),
            'departamento': random.choice(['Ventas', 'Almacén', 'Atención al Cliente', 'Seguridad']),
            'fecha_inicio': datetime.datetime.now().strftime('%Y-%m-%d'),
            'tipo_contrato': 'Temporal'
        }
        empleados.append(empleado)
    
    with open('empleados.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['nombre_completo', 'correo', 'departamento', 'fecha_inicio', 'tipo_contrato']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(empleados)
    
    print(f"✅ Archivo empleados.csv generado con {len(empleados)} empleados de ejemplo")

if __name__ == "__main__":
    main()