"""
Script para organizar juegos multidisco en carpetas y crear listas de reproducción .m3u.

Este script busca archivos con patrón (disc N), los agrupa por nombre base,
crea carpetas para cada juego y genera un archivo .m3u ordenado.

Script to organize multi-disc games in folders and create .m3u playlists.

This script searches for files with the pattern (disc N), groups them by base name,
creates folders for each game and generates an ordered .m3u file.
"""

__version__ = "1.0.0"

import locale
import os
import re
import sys
import time
from collections import defaultdict


# Detecta el idioma del sistema operativo y devuelve True si es español
def detecta_idioma_español():
    """Detecta si el idioma del sistema operativo es español."""
    idioma_sistema = locale.getdefaultlocale()[0]
    return idioma_sistema.startswith('es') if idioma_sistema else False

es_español = detecta_idioma_español()

# Diccionario de traducciones
TRADUCCIONES = {
    'es': {
        'intro': 'Introduce el directorio sobre el que trabajar: ',
        'dir_no_existe': 'El directorio no existe.',
        'fase1': 'Fase 1: Escaneando archivos...',
        'encontrado': 'Encontrado',
        'encontrados': 'Se encontraron',
        'juegos_multi': 'juegos multidisco',
        'fase2': 'Fase 2: Procesando juegos multidisco...',
        'procesando': 'Procesando',
        'discos': 'discos',
        'archivo_existe': 'El archivo',
        'ya_existe': 'ya existe. ¿Deseas procesar este juego?',
        'juego_no_procesado': 'Juego no procesado',
        'carpeta_creada': 'Carpeta creada',
        'carpeta_existe': 'Carpeta ya existe',
        'movido': 'Movido',
        'ya_existe_archivo': 'Ya existe',
        'm3u_creado': 'Archivo .m3u creado',
        'procesado': 'Procesado',
        'completado': '¡Proceso completado!'
    },
    'en': {
        'intro': 'Enter the directory to work on: ',
        'dir_no_existe': 'The directory does not exist.',
        'fase1': 'Phase 1: Scanning files...',
        'encontrado': 'Found',
        'encontrados': 'Found',
        'juegos_multi': 'multi-disc games',
        'fase2': 'Phase 2: Processing multi-disc games...',
        'procesando': 'Processing',
        'discos': 'discs',
        'archivo_existe': 'The file',
        'ya_existe': 'already exists. Do you want to process this game?',
        'juego_no_procesado': 'Game not processed',
        'carpeta_creada': 'Folder created',
        'carpeta_existe': 'Folder already exists',
        'movido': 'Moved',
        'ya_existe_archivo': 'Already exists',
        'm3u_creado': '.m3u file created',
        'procesado': 'Processed',
        'completado': 'Process completed!'
    }
}

idioma = 'es' if es_español else 'en'

def t(clave):
    """Obtiene la traducción de una clave."""
    return TRADUCCIONES[idioma].get(clave, clave)

# Obtener directorio de trabajo (como parámetro o por entrada)
if len(sys.argv) > 1:
    directorio = sys.argv[1]
else:
    directorio = input(t('intro'))

# Validar que el directorio exista
if not os.path.isdir(directorio):
    print(t('dir_no_existe'))
    sys.exit()

log_path = os.path.join(directorio, 'creaM3u.log')

# Crear/limpiar el archivo de log para registrar todos los mensajes
if os.path.exists(log_path):
    os.remove(log_path)


def registrar_mensaje(mensaje):
    """Muestra el mensaje por consola y lo guarda en el archivo de log."""
    print(mensaje)
    with open(log_path, 'a', encoding='utf-8') as archivo_log:
        archivo_log.write(f"{mensaje}\n")

# Diccionario para agrupar archivos multidisco por nombre base del juego
# Estructura: {nombre_juego: [archivo1, archivo2, ...]}
juegos_multidisco = defaultdict(list)

# Fase 1: Escanear archivos y agrupar por juego multidisco
registrar_mensaje(t('fase1'))
for archivo in os.listdir(directorio):
    ruta_completa = os.path.join(directorio, archivo)
    
    # Procesar solo archivos (no directorios)
    if os.path.isfile(ruta_completa):
        # Buscar patrón "(disc N)" o "[disc N]" en el nombre del archivo
        match = re.search(r'(.*?)\s*[\(\[]disc\s*(\d+)[\)\]]', archivo, re.IGNORECASE)
        
        if match:
            # Extraer nombre base del juego (todo antes de "disc N")
            nombre_base = match.group(1).strip()
            # Almacenar archivo en lista del juego correspondiente
            juegos_multidisco[nombre_base].append(archivo)
            registrar_mensaje(f"  {t('encontrado')}: {archivo} -> {nombre_base}")

registrar_mensaje(f"{t('encontrados')} {len(juegos_multidisco)} {t('juegos_multi')}.\n")
time.sleep(1)  # Pausa breve para mejorar la legibilidad de la salida

# Fase 2: Procesar juegos multidisco (con 2 o más discos)
registrar_mensaje(t('fase2'))
for nombre_base, archivos in juegos_multidisco.items():
    if len(archivos) > 1:  # Solo procesar si hay múltiples discos
        registrar_mensaje(f"\n  {t('procesando')}: {nombre_base} ({len(archivos)} {t('discos')})")

        ruta_m3u = os.path.join(directorio, f"{nombre_base}.m3u")
        
        # Verificar si el archivo .m3u ya existe y preguntar al usuario si desea procesar el juego o no
        if os.path.exists(ruta_m3u):
            respuesta = input(f"    {t('archivo_existe')} '{nombre_base}.m3u' {t('ya_existe')} (s/n): ").lower()
            registrar_mensaje(f"    {t('archivo_existe')} '{nombre_base}.m3u' {t('ya_existe')} (s/n): {respuesta}")
            if respuesta.lower() != 's' and respuesta.lower() != 'y':
                registrar_mensaje(f"    {t('juego_no_procesado')}: {nombre_base}")
                continue
        
        # Crear carpeta para el juego
        directorio_juego = os.path.join(directorio, nombre_base)
        if not os.path.exists(directorio_juego):
            os.makedirs(directorio_juego)
            registrar_mensaje(f"    {t('carpeta_creada')}: {nombre_base}")
        else:
            registrar_mensaje(f"    {t('carpeta_existe')}: {nombre_base}")
        
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
                registrar_mensaje(f"    {t('movido')}: {archivo}")
            else:
                registrar_mensaje(f"    {t('ya_existe_archivo')}: {archivo}")
            
            archivos_ordenados.append(archivo)
        
        # Crear archivo .m3u con la lista de discos ordenados  
        with open(ruta_m3u, 'w', encoding='utf-8') as m3u:
            for archivo in archivos_ordenados:
                m3u.write(os.path.join(nombre_base, f"{archivo}\n"))
        registrar_mensaje(f"    {t('m3u_creado')}: {nombre_base}.m3u")
        time.sleep(1)
        
        # Informar al usuario del procesamiento completado
        registrar_mensaje(f"  ✓ {t('procesado')}: {nombre_base} ({len(archivos)} {t('discos')})")

registrar_mensaje(f"\n{t('completado')}")