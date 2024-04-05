import PySimpleGUI as sg
import os
from datetime import datetime
import shutil
import sys
import threading
import logging
sys.path.append('..')
sys.path.append('./sockets')
from Cifrado import ZipAndEncryptFile as zp
from Cifrado import is_unsafe_mode as ium
import GetDataUploaded as gdu
from sockets import SocketCliente
import time
sg.theme('Material2')

data = []
cliente = SocketCliente.SocketCliente()
cliente.connect()
cliente.username = 'Hugo'
cliente.password = 'Hugo'
cliente.choose_opt(2)


is_unsafe_mode_active = False

def cargar_datos(window):
    cliente.choose_opt(5)
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


def update_unsafe_mode_text(window, is_unsafe_mode):
    text_color = 'red' if is_unsafe_mode else 'green'
    text = 'Modo Inseguro Activado' if is_unsafe_mode else 'Modo Seguro Activado'
    window['-UNSAFE-MODE-TEXT-'].update(text, text_color=text_color)

def create_main_window():
    headings = ['Número', 'Título', 'Descripción', 'Tiempo de Creación']


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
         sg.Button('Buscar Datos', key='-BUSCAR DATOS-', button_color=('white', 'brown'), font=("Helvetica", 12))]
    ]

    layout = [
        [sg.Column(unsafe_mode_column, vertical_alignment='top', justification='left')],
        [sg.Text('Cargando datos, por favor espera...', key='-CARGANDO-', visible=False)],
        [sg.Table(values=data, headings=headings, max_col_width=25,
                  auto_size_columns=True, display_row_numbers=True,
                  justification='left', num_rows=10, key='-TABLE-',
                  row_height=25, text_color='black', alternating_row_color='lightblue')],
        [sg.Column(buttons_column, element_justification='center')]
    ]

    window = sg.Window('Administrador de Archivos', layout, finalize=True, element_justification='center')
    logging.info('Ejecutando la aplicación...')
    return window

    

def create_add_window():
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


def create_files_window(item):
    files = gdu.get_files_in_zip("File"+item[4])  # Obtener la lista de archivos contenidos en el elemento seleccionado
    file_list = [[file] for file in files]  # Convertir la lista de archivos en un formato adecuado para la ventana

    layout = [
        [sg.Text(f'Archivos del elemento seleccionado: {item[1]}')],
        [sg.Listbox(values=file_list, size=(100, 10), select_mode='extended', key='-FILES_LIST-')],  # Listbox con select_mode='extended'        
        [sg.Button('Descargar Archivo', key='-DOWNLOAD-')]
    ]
    return sg.Window('Archivo Comprimidos', layout, finalize=True)




def main():
    
    global data
    global is_unsafe_mode_active
    data = []
    # cliente = SocketCliente.SocketCliente()
    # cliente.connect()

    is_unsafe_mode_active = False

    file_list = []

    main_window = create_main_window()
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
            is_unsafe_mode_active = values['-UNSAFE-']
            update_unsafe_mode_text(window, is_unsafe_mode_active)


        if event == '-ADD-' and not add_window:
            add_window = create_add_window()
        
        if event == '-SAVE-':
            title = values['-TITLE-'].strip()
            description = values['-DESCRIPTION-'].strip()
            files = values['-FILEPATH-'].strip()

            if not title or not description or not files:
                sg.popup('Por favor, completa todos los campos: Título, Descripción y Archivos.', title='Campos Requeridos')
            else:
                unsafe_mode = is_unsafe_mode_active
                valid_files = [f.strip() for f in files.split(';') if os.path.exists(f.strip())]

                try:
                    ium(unsafe_mode)
                    # zp(valid_files, title, description)
                    
                    cliente.ZipAndEncryptFile(valid_files, title, description)
                    sg.popup('Documento guardado con éxito', title='Guardado Exitoso')
                except Exception as e:
                    sg.popup_error(f'Error al guardar el documento: {e}', title='Error')

                now = datetime.now()
                current_time = now.strftime("%Y-%m-%d %H:%M:%S")

                nuevo_documento = [len(data) + 1, title, description, current_time]
                data.append(nuevo_documento)

                main_window['-TABLE-'].update(values=data)

                add_window.close()
                add_window = None
                data = gdu.listar_los_zips()

        if event == '-SEE-':
            if values['-TABLE-']:
                selected_row_index = values['-TABLE-'][0] 
                
                selected_item = data[selected_row_index]
                try:
                    show_files_window = create_files_window(selected_item)
                except Exception as e:
                    sg.popup_error(f'Error al mostrar los archivos: {e}', title='Error')
            else:
                sg.popup("Por favor, selecciona un elemento de la lista.")
                
        if event == '-DOWNLOAD-' and show_files_window is not None:
            selected_files = values['-FILES_LIST-']
            if selected_files:
                folder_path = sg.popup_get_folder('Seleccione la carpeta de destino')
                if folder_path:
                    nombre_Fichero="File"+selected_item[4]
                    try:
                        cliente.get_file(nombre_Fichero)
                    except FileNotFoundError as e:
                        sg.popup_error(f'Error al buscar el archivo: {e}', title='Error')
                    except Exception as e:
                        sg.popup_error(f'Error al descargar el archivo: {e}', title='Error')
                    
                    directorio_files=gdu.UnzipFolder(nombre_Fichero)
                    for file_name in selected_files:
                        file_name = ''.join(file_name)
                        gdu.get_file(file_name, directorio_files,folder_path)
                        pass
                    try:
                        shutil.rmtree(directorio_files)
                    except:
                        pass
                    sg.popup(f'Archivos descargados en: {folder_path}')
        elif event == '-BUSCAR DATOS-':
            window['-CARGANDO-'].update(visible=True)
            threading.Thread(target=cargar_datos, args=(window,), daemon=True).start()
        elif event == '-DATOS CARGADOS-':
            if values[event]: 
                data = values[event]
                window['-TABLE-'].update(values=data)
                window['-CARGANDO-'].update(visible=False)  
            else:
                sg.popup("Error al cargar los datos. Por favor, intenta nuevamente.")
        elif event == '-ERROR-':
            window['-CARGANDO-'].update(visible=False)

    main_window.close()
    logging.info('Cerrando la aplicación...')
    cliente.disconnect()
    if add_window:
        add_window.close()
    if show_files_window:
        show_files_window.close()
    try:

        shutil.rmtree('files')
    except:
        pass

if __name__ == '__main__':
    
    main()