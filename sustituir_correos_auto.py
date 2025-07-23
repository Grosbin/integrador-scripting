#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script automático para sustituir correos en pendientes_envio.csv por correos de prueba
Uso: python3 sustituir_correos_auto.py [porcentaje]
"""

import csv
import random
import sys
from pathlib import Path

# Correos de prueba para sustituir
CORREOS_PRUEBA = [
    'riveramax380@gmail.com',
    'jeffreynuyens@ufm.edu', 
    'robertobetancourth69@gmail.com'
]

def sustituir_correos_automatico(archivo_csv: str = "temp/pendientes_envio.csv", porcentaje: float = 0.3):
    """
    Sustituye automáticamente correos por correos de prueba
    
    Args:
        archivo_csv: Ruta al archivo pendientes_envio.csv
        porcentaje: Porcentaje de correos a sustituir (0.0 a 1.0)
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
    num_sustituciones = max(1, int(len(filas) * porcentaje))
    print(f"Sustituyendo {num_sustituciones} correos por correos de prueba ({porcentaje*100:.0f}%)")
    
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
    
    print(f"\nArchivo {archivo_csv} actualizado exitosamente")
    print("Ahora puedes ejecutar: python3 enviador.py")
    
    return True

def main():
    """Función principal"""
    
    # Obtener porcentaje desde argumentos de línea de comandos
    porcentaje = 0.3  # Default 30%
    
    if len(sys.argv) > 1:
        try:
            porcentaje = float(sys.argv[1])
                    if porcentaje < 0.0 or porcentaje > 1.0:
            print("Advertencia: Porcentaje inválido, usando 0.3 (30%)")
            porcentaje = 0.3
    except ValueError:
        print("Advertencia: Porcentaje inválido, usando 0.3 (30%)")
        porcentaje = 0.3
    
    print("=== SUSTITUCIÓN AUTOMÁTICA DE CORREOS DE PRUEBA ===\n")
    
    print(f"Correos de prueba disponibles:")
    for i, correo in enumerate(CORREOS_PRUEBA, 1):
        print(f"   {i}. {correo}")
    
    print(f"\nSustituyendo {porcentaje*100:.0f}% de los correos automáticamente...")
    
    if sustituir_correos_automatico(porcentaje=porcentaje):
        print("\nProceso completado exitosamente")
    else:
        print("\nError en el proceso")
        sys.exit(1)

if __name__ == "__main__":
    main() 