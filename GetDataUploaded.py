import CrearZipYCodificar as cz
import os
import zipfile
import json
import datetime


DIRECTORIO_ARCHIVOS = "files"
def listar_los_zips():
    directorioProyecto=cz.buscar_proyecto()
    if not directorioProyecto:
        return []
    directorio=cz.buscar_directorio(DIRECTORIO_ARCHIVOS,directorioProyecto)
    if directorio:
        carpetas = os.listdir(directorio)
        nuevos_documentos = []
        for index,carpeta in enumerate(carpetas):
            data = getDataFromJSON(carpeta, directorio)
            if not data:
                continue
            nuevo_documento = [
                index+ 1,  # ID del nuevo documento
                data['title'],  # Título
                data['description'],  # Descripción
                data['time']  # Fecha y hora de creación
            ]
            nuevos_documentos.append(nuevo_documento)
        nuevos_documentos_ordenados = sorted(nuevos_documentos, key=lambda x: x[3])
        for i, doc in enumerate(nuevos_documentos_ordenados):
            doc[0] = i + 1
        return nuevos_documentos_ordenados
    else:
        return []

def getDataFromJSON(carpeta,directorio):
    if cz.UnZipJSON(directorio+'/'+carpeta+'/'+carpeta+".zip.enc"):
        json_path = os.path.join(directorio,carpeta, f"{carpeta}.json")
        with open(json_path, 'r') as json_file:
            data = json.load(json_file)
            os.remove(json_path)
        return data
    else:
        return None



listar_los_zips()