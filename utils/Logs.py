import logging
import os

NOMBRE_PROYECTO = "estrategias_seguridad"

class LoggerConfigurator:
    LOG_FILE_PATH = 'logs/'

    @staticmethod
    def configure_log():
        directorio = LoggerConfigurator.LOG_FILE_PATH
        
        ProyectoEncontrad = False
        for root, dirs, files in os.walk('/'):
            # Busca el directorio deseado en la lista de directorios
            if NOMBRE_PROYECTO in dirs:
                # Si lo encuentra, devuelve la ruta completa del directorio
                ruta_logs = os.path.join(root, NOMBRE_PROYECTO, LoggerConfigurator.LOG_FILE_PATH)
                ProyectoEncontrad = True
                break  # Detener la búsqueda después de encontrar el directorio
        
        if ProyectoEncontrad:
            if not os.path.exists(ruta_logs):
                os.makedirs(ruta_logs)
                logging.info('Log directory created')

            directorio = os.path.join(ruta_logs, 'logfile.log')  # Ruta completa del archivo de registro
            logging.basicConfig(filename=directorio, level=logging.INFO, format='%(asctime)s - %(message)s')
            logging.info('Log file created')
        else:
            os.makedirs(os.path.join(NOMBRE_PROYECTO, LoggerConfigurator.LOG_FILE_PATH))
            directorio = os.path.join(NOMBRE_PROYECTO, LoggerConfigurator.LOG_FILE_PATH, 'logfile.log')
            
            logging.basicConfig(filename=directorio, level=logging.INFO, format='%(asctime)s - %(message)s')
            logging.info('Log directory created')
        

    @staticmethod
    def Subdirectory(subdirectory):
        logging.info('Subdirectory created for: ' + subdirectory)
