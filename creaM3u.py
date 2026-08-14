"""
Script para organizar juegos multidisco en carpetas y crear listas de reproducción .m3u.

Este script busca archivos con patrón (disc N), los agrupa por nombre base,
crea carpetas para cada juego y genera un archivo .m3u ordenado.
"""

import os
import re
import sys
import time
from collections import defaultdict

# Obtener directorio de trabajo (como parámetro o por entrada)
if len(sys.argv) > 1:
    directorio = sys.argv[1]
else:
    directorio = input("Introduce el directorio sobre el que trabajar: ")

# Validar que el directorio exista
if not os.path.isdir(directorio):
    print("El directorio no existe.")
    sys.exit()

# Diccionario para agrupar archivos multidisco por nombre base del juego
# Estructura: {nombre_juego: [archivo1, archivo2, ...]}
juegos_multidisco = defaultdict(list)

# Fase 1: Escanear archivos y agrupar por juego multidisco
print("Fase 1: Escaneando archivos...")
for archivo in os.listdir(directorio):
    ruta_completa = os.path.join(directorio, archivo)
    
    # Procesar solo archivos (no directorios)
    if os.path.isfile(ruta_completa):
        # Buscar patrón "(disc N)" en el nombre del archivo
        match = re.search(r'(.*?)\s*\(disc\s*(\d+)\)', archivo, re.IGNORECASE)
        
        if match:
            # Extraer nombre base del juego (todo antes de "disc N")
            nombre_base = match.group(1).strip()
            # Almacenar archivo en lista del juego correspondiente
            juegos_multidisco[nombre_base].append(archivo)
            print(f"  Encontrado: {archivo} -> {nombre_base}")

print(f"Se encontraron {len(juegos_multidisco)} juegos multidisco.\n")
time.sleep(1)  # Pausa breve para mejorar la legibilidad de la salida

# Fase 2: Procesar juegos multidisco (con 2 o más discos)
print("Fase 2: Procesando juegos multidisco...")
for nombre_base, archivos in juegos_multidisco.items():
    if len(archivos) > 1:  # Solo procesar si hay múltiples discos
        print(f"\n  Procesando: {nombre_base} ({len(archivos)} discos)")

        ruta_m3u = os.path.join(directorio, f"{nombre_base}.m3u")
        
        # Verificar si el archivo .m3u ya existe y preguntar al usuario si desea procesar el juego o no
        if os.path.exists(ruta_m3u):
            respuesta = input(f"    El archivo '{nombre_base}.m3u' ya existe. ¿Deseas procesar este juego? (s/n): ").lower()
            if respuesta.lower() != 's':
                print(f"    Jego no procesado: {nombre_base}")
                continue
        
        # Crear carpeta para el juego
        directorio_juego = os.path.join(directorio, nombre_base)
        if not os.path.exists(directorio_juego):
            os.makedirs(directorio_juego)
            print(f"    Carpeta creada: {nombre_base}")
        else:
            print(f"    Carpeta ya existe: {nombre_base}")
        
        # Función auxiliar para extraer número de disco del nombre de archivo
        def get_disc_number(x):
            """Extrae el número de disco del nombre del archivo para ordenamiento."""
            match = re.search(r'\(disc\s*(\d+)\)', x, re.IGNORECASE)
            return int(match.group(1)) if match else 0
        
        # Ordenar archivos por número de disco y moverlos a la carpeta del juego
        archivos_ordenados = []
        for archivo in sorted(archivos, key=get_disc_number):
            ruta_origen = os.path.join(directorio, archivo)
            ruta_destino = os.path.join(directorio_juego, archivo)
            
            # Mover archivo si no existe ya en destino
            if not os.path.exists(ruta_destino):
                os.rename(ruta_origen, ruta_destino)
                print(f"    Movido: {archivo}")
            else:
                print(f"    Ya existe: {archivo}")
            
            archivos_ordenados.append(archivo)
        
        # Crear archivo .m3u con la lista de discos ordenados  
        with open(ruta_m3u, 'w', encoding='utf-8') as m3u:
            for archivo in archivos_ordenados:
                m3u.write(os.path.join(nombre_base, f"{archivo}\n"))
        print(f"    Archivo .m3u creado: {nombre_base}.m3u")
        time.sleep(1)
        
        # Informar al usuario del procesamiento completado
        print(f"  ✓ Procesado: {nombre_base} ({len(archivos)} discos)")

print("\n¡Proceso completado!")