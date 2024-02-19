import CrearZipYCodificar as cz
import os
import zipfile
import json
import datetime
import shutil


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
                data['time'],  # Fecha y hora de creación
                data['id']
            ]
            nuevos_documentos.append(nuevo_documento)
        nuevos_documentos_ordenados = sorted(nuevos_documentos, key=lambda x: x[3])
        for i, doc in enumerate(nuevos_documentos_ordenados):
            doc[0] = i + 1
        return nuevos_documentos_ordenados
    else:
        return []

def getDataFromJSON(carpeta,directorio):
    path = os.path.join(directorio,carpeta, f"{carpeta}{cz.FILES_COMPRESSION_FORMAT}{cz.FILES_ENCODE_FORMAT}")
    if cz.UnZipJSON(path):
        json_path = os.path.join(directorio,carpeta, f"{carpeta}.json")
        with open(json_path, 'r') as json_file:
            data = json.load(json_file)
            os.remove(json_path)
        return data
    else:
        return None

def get_files_in_zip(file):
    directorioProyecto=cz.buscar_proyecto()
    if not directorioProyecto:
        print("No se ha encontrado el proyecto")
        return []
    directorio=os.path.join(directorioProyecto,DIRECTORIO_ARCHIVOS,file)
    archivo=os.path.join(directorio,file+".zip.enc")
    cz.UnZipFiles(archivo)
    nuevo_directorio=os.path.join(directorio,file)
    all_files = os.listdir(nuevo_directorio)
    shutil.rmtree(nuevo_directorio)
    all_files = [f for f in all_files if f != file + ".json"]
    return all_files


def get_file(file,directorio_file,target_folder):
    print(file)
    directorioProyecto = cz.buscar_proyecto()
    if not directorioProyecto:
        print("No se ha encontrado el proyecto")
        return None

    # Construir la ruta del archivo ZIP
    directorio = os.path.join(directorioProyecto, DIRECTORIO_ARCHIVOS, directorio_file)
    archivo = os.path.join(directorio, directorio_file + ".zip.enc")

    # Descomprimir el archivo ZIP
    cz.UnZipFiles(archivo)

    directorio=os.path.join(directorio,directorio_file)
    # Construir la ruta del archivo deseado dentro del directorio descomprimido
    archivo_deseado = os.path.join(directorio, file)

    # Verificar si el archivo deseado existe
    if os.path.exists(archivo_deseado):
        shutil.move(archivo_deseado, target_folder)
        shutil.rmtree(directorio)
        return True
    else:
        print(f"El archivo '{file}' no se encontró en el ZIP.")
        return None
    '''
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        return zip_ref.namelist()
    '''