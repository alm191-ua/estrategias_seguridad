import PySimpleGUI as sg
import os
from datetime import datetime
import shutil
import sys
import threading
import logging
import json
import os
sys.path.append('..')
sys.path.append('../sockets')
from Cifrado import is_unsafe_mode as ium
import GetDataUploaded as gdu
from sockets import SocketCliente
sg.theme('Material2')

data = []
cliente = SocketCliente.SocketCliente()

is_unsafe_mode_active = False

class ClienteUI:
    def __init__(self, username="", cliente=None):
        self.main_window = None
        self.add_window = None
        self.share_window = None
        self.show_files_window = None
        self.data = []
        if cliente:
            self.cliente = cliente
        else:
            self.cliente = SocketCliente.SocketCliente()
        self.is_unsafe_mode_active = False
        self.username = username
        self.user_public_key = None
        self.shared_with = {}  
        self.usuarios = []
        self.public_keys = []
        
    def run(self):
        main_window = self.create_main_window()
        add_window = None
        show_files_window = None
        share_window = None
        #Linux
        main_window.set_icon('icono.png')
        #Windows
        #main_window.set_icon('icono.ico')

        # block -UNSAFE- to permanently checked the checkbox
        if self.cliente.MALICIOSO:
            main_window['-UNSAFE-'].update(disabled=True, value=True)
            self.update_unsafe_mode_text(main_window, True)

        while True:
            window, event, values = sg.read_all_windows()
            
            if event == sg.WINDOW_CLOSED and window == main_window:
                try:
                    self.cliente.disconnect()
                except Exception as e:
                    logging.error(f'Error al desconectar del servidor: {e}')
                break
            elif event == sg.WINDOW_CLOSED and window == add_window:
                add_window.close()
                add_window = None
                continue
            elif event == sg.WINDOW_CLOSED and window == show_files_window:
                show_files_window.close()
                show_files_window = None
                continue
            elif event == sg.WINDOW_CLOSED and window == share_window:
                share_window.close()
                share_window = None
                continue
            elif event == '-UNSAFE-':
                self.is_unsafe_mode_active = values['-UNSAFE-']
                self.update_unsafe_mode_text(window, self.is_unsafe_mode_active)
            #Evento para abrir la ventana de añadir
            if event == '-ADD-' and not add_window:
                add_window = self.create_add_window()
            #Evento para guardar los archivos
            if event == '-SAVE-':
                title = values['-TITLE-'].strip()
                description = values['-DESCRIPTION-'].strip()
                file_paths = values['-FILEPATH-'].strip().split(';')
                
                shared_users = [usuario for usuario in self.usuarios if values.get(f'-SHARE-{usuario}-', False)]
                shared_public_keys = [self.public_keys[self.usuarios.index(usuario)] for usuario in shared_users]
                print("Compartido con:", shared_users)
                
                # insertar el usuario actual en la lista de usuarios con los que se comparte, al incio
                shared_users.insert(0, self.username)
                shared_public_keys.insert(0, self.user_public_key)

                if not title or not description or not file_paths:
                    sg.popup('Por favor, completa todos los campos: Título, Descripción y Archivos.', title='Campos Requeridos')
                else:
                    valid_files = [file_path for file_path in file_paths if os.path.isfile(file_path)]
                    if not valid_files:
                        sg.popup_error('Algunos archivos no existen. Por favor, verifica las rutas.', title='Error')
                        continue
                    try:
                        ium(self.is_unsafe_mode_active)
                        print("Enviando archivos...")
                        self.cliente.send_encrypted_files(valid_files, title, description, self.username, shared_users, shared_public_keys)
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
                    self.data = gdu.listar_los_zips(self.cliente.FOLDER, self.username)
            if '-SHARE-' in event:
                usuario = event.split('-SHARE-')[1]
                self.shared_with[usuario] = not self.shared_with[usuario]  # Toggle share status  
            #Evento para abrir la ventana de archivos
            if event == '-SEE-':
                if values['-TABLE-']:
                    selected_row_index = values['-TABLE-'][0] 
                    
                    selected_item = self.data[selected_row_index]
                    try:
                        show_files_window = self.create_files_window(selected_item)
                    except Exception as e:
                        sg.popup_error(f'Error al mostrar los archivos: {e}', title='Error')
                else:
                    sg.popup("Por favor, selecciona un elemento de la lista.")
            #Evento para descargar archivos    
            if event == '-DOWNLOAD-' and show_files_window is not None:
                selected_files = values['-FILES_LIST-']
                if selected_files:
                    folder_path = sg.popup_get_folder('Seleccione la carpeta de destino')
                    if folder_path:
                        nombre_Fichero="File"+selected_item[4]
                        try:
                            print("Cliente malicioso activado: " + self.cliente.MALICIOSO)
                            self.cliente.get_file(nombre_Fichero)
                        except FileNotFoundError as e:
                            sg.popup_error(f'Error al buscar el archivo: {e}', title='Error')
                        except Exception as e:
                            sg.popup_error(f'Error al descargar el archivo: {e}', title='Error')
                        
                        directorio_files=self.cliente.UnzipFolder(nombre_Fichero)
                        for file_name in selected_files:
                            file_name = ''.join(file_name)
                            gdu.get_file(file_name, directorio_files,folder_path)
                            pass
                        try:
                            shutil.rmtree(directorio_files)
                        except:
                            pass
                        sg.popup(f'Archivos descargados en: {folder_path}')
            #Evento para mostrar la información de un documento
            if event == '-INFO JSON-':
                if values['-TABLE-']:
                    selected_row_indices = values['-TABLE-']
                    for index in selected_row_indices:
                        selected_item = self.data[index]
                        file_name = "File"+selected_item[4]
                        json_path = os.path.join(f'files_{self.username}', file_name, file_name + ".json")
                        self.show_json_info(json_path)
                else:
                    sg.popup("Por favor, selecciona un elemento de la lista.")
            #Evento para buscar los datos
            elif event == '-BUSCAR DATOS-':
                window['-CARGANDO-'].update(visible=True)
                threading.Thread(target=self.cargar_datos, args=(window,), daemon=True).start()
            #Evento para cargar los datos
            elif event == '-DATOS CARGADOS-':
                if values[event]:  # Esta es la lista de datos cargados
                    self.data = values[event]
                    window['-TABLE-'].update(values=self.data)
                    window['-CARGANDO-'].update(visible=False)
                else:
                    sg.popup("No se encontraron datos. Por favor, intenta nuevamente.")
                    window['-CARGANDO-'].update(visible=False)
            #Evento para mostrar un error
            elif event == '-ERROR-':
                window['-CARGANDO-'].update(visible=False)

        main_window.close()
        logging.info('Cerrando la aplicación...')
        if add_window:
            add_window.close()
        if show_files_window:
            show_files_window.close()
        if share_window:
            share_window.close()
        try:
            shutil.rmtree(self.cliente.FOLDER)
        except:
            pass
        
    
    def compartir_con_usuario(self, filepath, usuario):
        if os.path.exists(filepath):
            try:
                self.cliente.send_encrypted_files([filepath], usuario)
                sg.popup(f'Archivo compartido con éxito con {usuario}!', title='Compartido Exitoso')
            except Exception as e:
                sg.popup_error(f'Error al compartir el archivo con {usuario}: {e}', title='Error')
        else:
            sg.popup_error('Archivo no existe. Verifica la ruta.', title='Error de Archivo')


    def cargar_datos(self, window):
        self.cliente.choose_opt(5)
        try:
            data_cargada = gdu.listar_los_zips(self.cliente.FOLDER, self.username)
            if data_cargada:
                window.write_event_value('-DATOS CARGADOS-', data_cargada)
            else:
                window.write_event_value('-DATOS CARGADOS-', [])
        except Exception as e:
            logging.error(f'Error al cargar datos: {e}')
            window.write_event_value('-ERROR-', str(e))



    def update_unsafe_mode_text(self,window, is_unsafe_mode):
        """
        Actualiza el texto de la ventana principal para indicar si el modo inseguro está activado o no.
        """
        if self.cliente.MALICIOSO:
            is_unsafe_mode = True
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
            sg.Button('Añadir', key='-ADD-', button_color=('white', 'green'), font=("Helvetica", 12), visible=not self.cliente.MALICIOSO),
            sg.Text('', size=(10, 1)),
            sg.Button('Archivos', key='-SEE-', button_color=('white', 'blue'), font=("Helvetica", 12)),
            sg.Text('', size=(10, 1)),
            sg.Button('Buscar Datos', key='-BUSCAR DATOS-', button_color=('white', 'brown'), font=("Helvetica", 12)),
            sg.Button('Info Documento', key='-INFO JSON-', button_color=('white', 'orange'), font=("Helvetica", 12))]
        ]

        layout = [
            [sg.Column(user_display_column, justification='right', vertical_alignment='top'), sg.Column(unsafe_mode_column, vertical_alignment='top', justification='left')],
            [sg.Text('Cargando datos, por favor espera...', key='-CARGANDO-', visible=False)],
            [sg.Text('Documentos:', font=("Helvetica", 12))],
            [sg.Table(values=self.data, headings=['Número', 'Título', 'Descripción', 'Tiempo de Creación'], max_col_width=25,
                      auto_size_columns=True, display_row_numbers=True,
                      justification='left', num_rows=10, key='-TABLE-',
                      row_height=15, text_color='black', alternating_row_color='lightblue')],
            [sg.Text('Documentos Compartidos:', font=("Helvetica", 12))],
            [sg.Table(values=self.data, headings=['Número', 'Título', 'Descripción', 'Tiempo de Creación', 'Autor'], max_col_width=25,
                      auto_size_columns=True, display_row_numbers=True,
                      justification='left', num_rows=10, key='-SHARETABLE-',
                      row_height=15, text_color='black', alternating_row_color='lightblue')],
            [sg.Column(buttons_column, element_justification='center')]
        ]
        
        window = sg.Window('Administrador de Archivos', layout, finalize=True, element_justification='center')
        logging.info('Ejecutando la aplicación...')
        return window
        

    def create_add_window(self, update=False):
        input_size = (25, 1)
        label_size = (10, 1)
        button_size = (10, 1)
        padding = ((5, 5), (10, 10))

        users, public_keys = self.cliente.get_public_keys()
        # get the user index in users list that matches the username
        # and the public key of the user
        user_index = users.index(self.username)
        self.user_public_key = public_keys[user_index]

        self.usuarios = [user for user in users if user != self.username]
        self.public_keys = [key for key in public_keys if key != self.user_public_key]
        # usuarios = self.cargar_usuarios()
        user_sharing_rows = [
            [sg.Checkbox(usuario, key=f'-SHARE-{usuario}-', font=("Helvetica", 10), pad=padding)]
            for usuario in self.usuarios
        ]
            
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
            [sg.Column(user_sharing_rows, scrollable=True, vertical_scroll_only=True, size=(None, 100))],
            [sg.Button('Guardar', key='-SAVE-', button_color=('white', 'blue'), size=button_size, font=("Helvetica", 12), pad=padding)],
        ]

        return sg.Window('Añadir Nuevo Archivo', layout, finalize=True, disable_close=False, element_justification='center')


    def cargar_usuarios(self):
        path_to_json = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'server', 'users.json')
        try:
            with open(path_to_json, 'r') as file:
                data = json.load(file)
            self.usuarios = [user for user in data if user != self.username]  # Actualizar la variable de instancia
            return self.usuarios
        except Exception as e:
            sg.popup_error(f"Error al cargar usuarios: {e}")
            return []
        

    def create_files_window(self,item):
        """
        Crea la ventana para mostrar los archivos de un elemento seleccionado.
        """
        files = self.cliente.get_files_in_zip("File"+item[4])
        file_list = [[file] for file in files]  
        layout = [
            [sg.Text(f'Archivos del elemento seleccionado: {item[1]}')],
            [sg.Listbox(values=file_list, size=(100, 10), select_mode='extended', key='-FILES_LIST-')],       
            [sg.Button('Descargar Archivo', key='-DOWNLOAD-')]
        ]
        return sg.Window('Archivo Comprimidos', layout, finalize=True)
    
    def show_json_info(self, json_path):
        """
        Muestra la información de un archivo JSON.
        """
        if not os.path.exists(json_path):
            sg.popup_error(f"El archivo JSON no existe: {json_path}")
            return

        try:
            with open(json_path, 'r') as file:
                data = json.load(file)

            title = data.get('title', 'Sin título')
            description = data.get('description', 'Sin descripción')
            time = data.get('time', 'Sin tiempo especificado')
            files = data.get('files', [])

            if not files:  # Si no hay archivos, mostrar mensaje relevante
                sg.popup_error("No hay archivos listados en el JSON.")
                return

            info_layout = [
                [sg.Text(f"Title: {title}")],
                [sg.Text(f"Description: {description}")],
                [sg.Text(f"Time: {time}")],
                [sg.Text("Files:")] + [sg.Text(f) for f in files]
            ]

            info_window = sg.Window("Info JSON", info_layout, modal=True)
            while True:
                event, _ = info_window.read()
                if event == sg.WINDOW_CLOSED:
                    break
            info_window.close()

        except json.JSONDecodeError:
            sg.popup_error("Error al decodificar el archivo JSON.")
        except Exception as e:
            sg.popup_error(f"Error al cargar la información JSON: {e}")



if __name__ == '__main__':
    ui = ClienteUI()
    ui.run()