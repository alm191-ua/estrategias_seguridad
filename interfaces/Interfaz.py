import PySimpleGUI as sg
import os
from datetime import datetime
import shutil
import sys
import threading
import logging
sys.path.append('..')
sys.path.append('../sockets')
from Cifrado import ZipAndEncryptFile as zp
from Cifrado import is_unsafe_mode as ium
import GetDataUploaded as gdu
from sockets import SocketCliente
sg.theme('Material2')

data = []
cliente = SocketCliente.SocketCliente()

is_unsafe_mode_active = False

class ClienteUI:
    def __init__(self, username=""):
        self.main_window = None
        self.add_window = None
        self.show_files_window = None
        self.data = []
        self.cliente = SocketCliente.SocketCliente()
        self.is_unsafe_mode_active = False
        self.username = username
        self.conectar_al_servidor()

    def conectar_al_servidor(self):
        try:
            self.cliente.connect()
        except Exception as e:
            sg.popup_error(f"Error al conectar con el servidor: {e}")
    
    def run(self):
        main_window = self.create_main_window()
        add_window = None
        show_files_window = None

        while True:
            window, event, values = sg.read_all_windows()
            
            if event == sg.WINDOW_CLOSED and window == main_window:
                break
            elif event == sg.WINDOW_CLOSED and window == add_window:
                add_window.close()
                add_window = None
            elif event == sg.WINDOW_CLOSED and window == show_files_window:
                show_files_window.close()
                show_files_window = None
            elif event == '-UNSAFE-':
                self.is_unsafe_mode_active = values['-UNSAFE-']
                self.update_unsafe_mode_text(window, self.is_unsafe_mode_active)

            if event == '-ADD-' and not add_window:
                add_window = self.create_add_window()
            
            if event == '-SAVE-':
                title = values['-TITLE-'].strip()
                description = values['-DESCRIPTION-'].strip()
                file_paths = values['-FILEPATH-'].strip().split(';')  # Asume que los archivos están separados por ';'

                if not title or not description or not file_paths:
                    sg.popup('Por favor, completa todos los campos: Título, Descripción y Archivos.', title='Campos Requeridos')
                else:
                    valid_files = [file_path for file_path in file_paths if os.path.isfile(file_path)]
                    if not valid_files:
                        sg.popup_error('Algunos archivos no existen. Por favor, verifica las rutas.', title='Error')
                        continue  # Vuelve al inicio del bucle para que el usuario pueda corregirlo
                    
                    try:
                        if not self.cliente.conn:
                            self.conectar_al_servidor()

                        self.cliente.send_encrypted_files(valid_files, title, description)
                        sg.popup('Documentos enviados y guardados con éxito', title='Guardado Exitoso')
                    except Exception as e:
                        sg.popup_error(f'Error al enviar los documentos: {e}', title='Error')

                    now = datetime.now()
                    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
                    nuevo_documento = [len(self.data) + 1, title, description, current_time]
                    self.data.append(nuevo_documento)
                    main_window['-TABLE-'].update(values=self.data)
                    add_window.close()
                    add_window = None
                    self.data = gdu.listar_los_zips()


            if event == '-SEE-':
                if values['-TABLE-']:
                    selected_row_index = values['-TABLE-'][0] 
                    
                    selected_item = self.data[selected_row_index]
                    show_files_window = self.create_files_window(selected_item)
                else:
                    sg.popup("Por favor, selecciona un elemento de la lista.")
                    
            if event == '-DOWNLOAD-' and show_files_window is not None:
                selected_files = values['-FILES_LIST-']
                if selected_files:
                    folder_path = sg.popup_get_folder('Seleccione la carpeta de destino')
                    if folder_path:
                        nombre_Fichero="File"+selected_item[4]
                        print(nombre_Fichero)
                        directorio_files=gdu.UnzipFolder(nombre_Fichero)
                        for file_name in selected_files:
                            file_name = ''.join(file_name)
                            gdu.get_file(file_name, directorio_files,folder_path)
                            pass
                        shutil.rmtree(directorio_files)
                        sg.popup(f'Archivos descargados en: {folder_path}')
            if event == '-INFO JSON-':
                if values['-TABLE-']:
                    selected_row_indices = values['-TABLE-']
                    for index in selected_row_indices:
                        selected_item = self.data[index]
                        file_name = "File"+selected_item[4]
                        json_path = os.path.join("files", file_name, file_name + ".json")
                        self.show_json_info(json_path)
                else:
                    sg.popup("Por favor, selecciona un elemento de la lista.")
            elif event == '-BUSCAR DATOS-':
                window['-CARGANDO-'].update(visible=True)
                threading.Thread(target=self.cargar_datos, args=(window,), daemon=True).start()
            elif event == '-DATOS CARGADOS-':
                if values[event]: 
                    self.data = values[event]
                    window['-TABLE-'].update(values=self.data)
                    window['-CARGANDO-'].update(visible=False)  
                else:
                    sg.popup("Error al cargar los datos. Por favor, intenta nuevamente.")
            elif event == '-ERROR-':
                window['-CARGANDO-'].update(visible=False)

        main_window.close()
        logging.info('Cerrando la aplicación...')
        if add_window:
            add_window.close()
        if show_files_window:
            show_files_window.close()


    def cargar_datos(self,window):
        try:
            data_cargada = gdu.listar_los_zips()
            if not data_cargada:
                sg.popup('No se encontraron datos')
            else:
                window.write_event_value('-DATOS CARGADOS-', data_cargada)
        except Exception as e:
            logging.error(f'Error al cargar datos: {e}')
            # print("Error al cargar datos:", e)
            window.write_event_value('-ERROR-', str(e)) 


    def update_unsafe_mode_text(self,window, is_unsafe_mode):
        text_color = 'red' if is_unsafe_mode else 'green'
        text = 'Modo Inseguro Activado' if is_unsafe_mode else 'Modo Seguro Activado'
        window['-UNSAFE-MODE-TEXT-'].update(text, text_color=text_color)

    def create_main_window(self):
        
        headings = ['Número', 'Título', 'Descripción', 'Tiempo de Creación']
        
        user_display_column = [
            [sg.Text(f'Usuario: {self.username}', justification='right')]
        ]
        
        unsafe_mode_column = [
            [sg.Checkbox('', default=False, enable_events=True, key='-UNSAFE-'),
             sg.Text('Modo Seguro Activado', key='-UNSAFE-MODE-TEXT-', text_color='green')]
        ]
        
        buttons_column = [
            [sg.Text('', size=(10, 1)),
            sg.Button('Añadir', key='-ADD-', button_color=('white', 'green'), font=("Helvetica", 12)),
            sg.Text('', size=(10, 1)),
            sg.Button('Archivos', key='-SEE-', button_color=('white', 'blue'), font=("Helvetica", 12)),
            sg.Text('', size=(10, 1)),
            sg.Button('Buscar Datos', key='-BUSCAR DATOS-', button_color=('white', 'brown'), font=("Helvetica", 12)),
            sg.Button('Info Documento', key='-INFO JSON-', button_color=('white', 'orange'), font=("Helvetica", 12))]
        ]

        
        layout = [
            [sg.Column(user_display_column, justification='right', vertical_alignment='top'), sg.Column(unsafe_mode_column, vertical_alignment='top', justification='left')],
            [sg.Text('Cargando datos, por favor espera...', key='-CARGANDO-', visible=False)],
            [sg.Table(values=self.data, headings=['Número', 'Título', 'Descripción', 'Tiempo de Creación'], max_col_width=25,
                      auto_size_columns=True, display_row_numbers=True,
                      justification='left', num_rows=10, key='-TABLE-',
                      row_height=25, text_color='black', alternating_row_color='lightblue')],
            [sg.Column(buttons_column, element_justification='center')]
        ]
        
        window = sg.Window('Administrador de Archivos', layout, finalize=True, element_justification='center')
        logging.info('Ejecutando la aplicación...')
        return window

        

    def create_add_window(self):
        input_size = (25, 1)
        label_size = (10, 1)
        button_size = (10, 1)
        padding = ((5, 5), (10, 10))
        
        layout = [
            [sg.Frame(layout=[
                [sg.Text('Título', size=label_size, font=("Helvetica", 10), pad=padding),
                sg.InputText(key='-TITLE-', font=("Helvetica", 10), size=input_size, pad=padding)],
                [sg.Text('Descripción', size=label_size, font=("Helvetica", 10), pad=padding),
                sg.InputText(key='-DESCRIPTION-', font=("Helvetica", 10), size=input_size, pad=padding)],
                [sg.Text('Archivos', size=label_size, font=("Helvetica", 10), pad=padding),
                sg.InputText(key='-FILEPATH-', font=("Helvetica", 10), size=input_size, pad=padding),
                sg.FilesBrowse('Buscar', file_types=(("Todos los Archivos", "*.*"),), target='-FILEPATH-', font=("Helvetica", 10), pad=padding)],
            ], title="", border_width=0)],
            [sg.Button('Guardar', key='-SAVE-', button_color=('white', 'blue'), size=button_size, font=("Helvetica", 12), pad=((5,5),(20,10)))]
        ]
        return sg.Window('Añadir Nuevo Archivo', layout, finalize=True, disable_close=False, element_justification='center')


    def create_files_window(self,item):
        files = gdu.get_files_in_zip("File"+item[4])  # Obtener la lista de archivos contenidos en el elemento seleccionado
        file_list = [[file] for file in files]  # Convertir la lista de archivos en un formato adecuado para la ventana

        layout = [
            [sg.Text(f'Archivos del elemento seleccionado: {item[1]}')],
            [sg.Listbox(values=file_list, size=(100, 10), select_mode='extended', key='-FILES_LIST-')],  # Listbox con select_mode='extended'        
            [sg.Button('Descargar Archivo', key='-DOWNLOAD-')]
        ]
        return sg.Window('Archivo Comprimidos', layout, finalize=True)
    
    def show_json_info(self, json_path):
        try:
            title, description, time, decrypted_files = self.cliente.get_json_info(json_path)
            info_layout = [
                [sg.Text(f"Title: {title}")],
                [sg.Text(f"Description: {description}")],
                [sg.Text(f"Time: {time}")],
                [sg.Text("Files:")]] + [[sg.Text(f)] for f in decrypted_files]
            
            info_window = sg.Window("Info JSON", info_layout, modal=True)
            while True:
                event, values = info_window.read()
                if event == sg.WINDOW_CLOSED:
                    break
            info_window.close()
        except Exception as e:
            sg.popup_error(f"Error al cargar la información JSON: {e}")


if __name__ == '__main__':
    ui = ClienteUI()
    ui.run()