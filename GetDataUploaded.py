import Cifrado as cz
import os
import json
import shutil
import logging


DIRECTORIO_ARCHIVOS = "files"

def listar_los_zips(dir, username):
    """
    Lista los documentos en el directorio de archivos.
    """
    if not cz.DIRECTORIO_PROYECTO:
        cz.buscar_proyecto()
    print('DIRECTORIO PROYECTO:', cz.DIRECTORIO_PROYECTO)
    if not cz.DIRECTORIO_PROYECTO:
        return []

    directorio_usuario = f"{DIRECTORIO_ARCHIVOS}_{username}"
    directorio_completo = os.path.join(cz.DIRECTORIO_PROYECTO, directorio_usuario)
    print(directorio_completo)


    if os.path.exists(directorio_completo):
        carpetas = os.listdir(directorio_completo)
        nuevos_documentos = []
        for index, carpeta in enumerate(carpetas):
            json_path = os.path.join(directorio_completo, carpeta, carpeta + ".json")
            if os.path.exists(json_path):
                data = getDataFromJSON(carpeta, directorio_completo)
                if data:
                    nuevo_documento = [
                            index + 1,  # ID del nuevo documento
                            data['title'],  # Título
                            data['description'],  # Descripción
                            data['time'],  # Fecha y hora de creación
                            data['size'],  # Tamaño del documento  
                            data['author'], # Dueño del documento
                            data['id']  # ID del documento
                             
                        ]
                    nuevos_documentos.append(nuevo_documento)
        nuevos_documentos_ordenados = sorted(nuevos_documentos, key=lambda x: x[3], reverse=True)
        for i, doc in enumerate(nuevos_documentos_ordenados):
            doc[0] = i + 1

        return nuevos_documentos_ordenados
    else:
        return []

def listar_los_zips_compartidos(dir, username):
    """
    Lista los documentos en el directorio de archivos.
    """
    if not cz.DIRECTORIO_PROYECTO:
        cz.buscar_proyecto()
    if not cz.DIRECTORIO_PROYECTO:
        return []

    directorio_usuario = f"{DIRECTORIO_ARCHIVOS}_{username}"
    directorio_completo = os.path.join(cz.DIRECTORIO_PROYECTO, directorio_usuario)


    if os.path.exists(directorio_completo):
        carpetas = os.listdir(directorio_completo)
        nuevos_documentos = []
        for index, carpeta in enumerate(carpetas):
            if carpeta == "shared":
                directorio_completo=os.path.join(directorio_completo, carpeta)
                archivos= os.listdir(directorio_completo)
                
                for archivo in archivos:
                    json_path = os.path.join(directorio_completo, archivo, archivo + ".json")
                    if os.path.exists(json_path):
                        data = getDataFromJSON(archivo, directorio_completo)
                        if data:
                            nuevo_documento = [
                                index + 1,  # ID del nuevo documento
                                data['title'],  # Título
                                data['description'],  # Descripción
                                data['time'],  # Fecha y hora de creación
                                data['size'],  # Tamaño del documento  
                                data['author'], # Dueño del documento
                                data['id']  # ID del documento
                                
                            ]
                            nuevos_documentos.append(nuevo_documento)
        nuevos_documentos_ordenados = sorted(nuevos_documentos, key=lambda x: x[3], reverse=True)
        for i, doc in enumerate(nuevos_documentos_ordenados):
            doc[0] = i + 1

        return nuevos_documentos_ordenados
    else:
        return []

def getDataFromJSON(fichero, directorio):
    """
    Obtiene la información del archivo JSON de un documento.

    Args:
        fichero (str): El nombre del archivo.
        directorio (str): La ruta del directorio. Normalmente es el nombre de usuario.

    Returns:
        dict: Un diccionario con la información del documento.
    """
    data=[]
    json_path = os.path.join(directorio, fichero, f"{fichero}.json")
    if os.path.exists(json_path):
        with open(json_path, 'r') as json_file:
            data = json.load(json_file)
    else:
        logging.error(f"El archivo {json_path} no existe.")
        # print(f"El archivo {json_path} no existe.")
    return data


def get_file(file, directorio_file, target_folder):
    if not cz.DIRECTORIO_PROYECTO:
        logging.warning("No se ha encontrado el proyecto")
        # print("No se ha encontrado el proyecto")
        return None

    # Construir la ruta del archivo deseado dentro del directorio descomprimido
    archivo_deseado = os.path.join(directorio_file, file)

    # Verificar si el archivo deseado existe
    if os.path.exists(archivo_deseado):
        archivo_Existente = os.path.join(target_folder, file)
        if os.path.exists(archivo_Existente):
            os.remove(archivo_Existente)
        shutil.move(archivo_deseado, target_folder)
        
        return True
    else:
        logging.warning("No se ha encontrado el proyecto")
        # print(f"El archivo '{file}' no se encontró en el ZIP.")
        return None
