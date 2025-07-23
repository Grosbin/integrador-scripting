#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para sustituir correos en pendientes_envio.csv por correos de prueba
Permite verificar si los correos están llegando correctamente
"""

import csv
import random
from pathlib import Path

# Correos de prueba para sustituir
CORREOS_PRUEBA = [
    'riveramax380@gmail.com',
    'jeffreynuyens@ufm.edu', 
    'robertobetancourth69@gmail.com'
]

def sustituir_correos_prueba(archivo_csv: str, porcentaje_sustitucion: float = 0.3):
    """
    Sustituye un porcentaje de correos en el archivo CSV por correos de prueba
    
    Args:
        archivo_csv: Ruta al archivo pendientes_envio.csv
        porcentaje_sustitucion: Porcentaje de correos a sustituir (0.0 a 1.0)
    """
    
    if not Path(archivo_csv).exists():
        print(f"Error: Archivo no encontrado: {archivo_csv}")
        return False
    
    # Leer el archivo original
    filas = []
    with open(archivo_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:  # Verificar que tenga al menos 2 columnas
                filas.append(row)
    
    if not filas:
        print("Error: El archivo está vacío o no tiene datos válidos")
        return False
    
    print(f"Total de filas encontradas: {len(filas)}")
    
    # Calcular cuántas filas sustituir
    num_sustituciones = max(1, int(len(filas) * porcentaje_sustitucion))
    print(f"Sustituyendo {num_sustituciones} correos por correos de prueba")
    
    # Seleccionar filas aleatorias para sustituir
    indices_sustitucion = random.sample(range(len(filas)), num_sustituciones)
    
    # Realizar sustituciones
    correos_originales = []
    for i in indices_sustitucion:
        correos_originales.append(filas[i][1])  # Guardar correo original
        filas[i][1] = random.choice(CORREOS_PRUEBA)  # Sustituir por correo de prueba
    
    # Guardar archivo modificado
    with open(archivo_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(filas)
    
    # Mostrar resumen
    print("\nSustituciones realizadas:")
    for i, correo_original in zip(indices_sustitucion, correos_originales):
        print(f"   Fila {i+1}: {correo_original} -> {filas[i][1]}")
    
    print(f"\nCorreos de prueba utilizados:")
    for correo in CORREOS_PRUEBA:
        count = sum(1 for fila in filas if fila[1] == correo)
        if count > 0:
            print(f"   {correo}: {count} envíos")
    
    return True

def mostrar_estado_actual(archivo_csv: str):
    """Muestra el estado actual del archivo CSV"""
    
    if not Path(archivo_csv).exists():
        print(f"Error: Archivo no encontrado: {archivo_csv}")
        return
    
    filas = []
    with open(archivo_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                filas.append(row)
    
    if not filas:
        print("El archivo está vacío")
        return
    
    print(f"Estado actual de {archivo_csv}:")
    print(f"   Total de filas: {len(filas)}")
    
    # Contar correos de prueba
    correos_prueba_count = {}
    for correo in CORREOS_PRUEBA:
        count = sum(1 for fila in filas if fila[1] == correo)
        if count > 0:
            correos_prueba_count[correo] = count
    
    if correos_prueba_count:
        print("   Correos de prueba encontrados:")
        for correo, count in correos_prueba_count.items():
            print(f"      {correo}: {count}")
    else:
        print("   No hay correos de prueba en el archivo")

def main():
    """Función principal"""
    
    archivo_csv = "temp/pendientes_envio.csv"
    
    print("=== SUSTITUCIÓN DE CORREOS DE PRUEBA ===\n")
    
    # Mostrar estado actual
    mostrar_estado_actual(archivo_csv)
    
    print(f"\nCorreos de prueba disponibles:")
    for i, correo in enumerate(CORREOS_PRUEBA, 1):
        print(f"   {i}. {correo}")
    
    # Preguntar si realizar sustitución
    respuesta = input(f"\n¿Deseas sustituir correos en {archivo_csv}? (s/n): ").lower().strip()
    
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        porcentaje = input("Porcentaje de correos a sustituir (0.1-1.0, default 0.3): ").strip()
        
        try:
            porcentaje = float(porcentaje) if porcentaje else 0.3
                    if porcentaje < 0.1 or porcentaje > 1.0:
            print("Advertencia: Porcentaje inválido, usando 0.3 (30%)")
            porcentaje = 0.3
    except ValueError:
        print("Advertencia: Porcentaje inválido, usando 0.3 (30%)")
        porcentaje = 0.3
    
    print(f"\nSustituyendo {porcentaje*100:.0f}% de los correos...")
        
        if sustituir_correos_prueba(archivo_csv, porcentaje):
            print(f"\nArchivo {archivo_csv} actualizado exitosamente")
            print("Ahora puedes ejecutar: python3 enviador.py")
        else:
            print("Error al actualizar el archivo")
    else:
        print("Operación cancelada")

if __name__ == "__main__":
    main() 