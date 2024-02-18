import PySimpleGUI as sg
import os
from datetime import datetime
from CrearZipYCodificar import ZipFile as zp
import GetDataUploaded as gdu
from Logs import LoggerConfigurator 

data = gdu.listar_los_zips()

def create_main_window():
    headings = ['Número', 'Título', 'Descripción', 'Tiempo de Creación']
    layout = [
        [sg.Table(values=data, headings=headings, max_col_width=25,
                  auto_size_columns=True, display_row_numbers=False, 
                  justification='right', num_rows=10, key='-TABLE-')],
        [sg.Button('Añadir', key='-ADD-', button_color=('white', 'blue')),
         sg.Button('Archivos', key='-SEE-', button_color=('white', 'blue'))
         ]
    ]
    LoggerConfigurator.configure_log()
    LoggerConfigurator.Subdirectory("Interfaz")
    return sg.Window('Administrador de Archivos', layout, finalize=True)

def create_add_window():
    layout = [
        [sg.Text('Título'), sg.InputText(key='-TITLE-')],
        [sg.Text('Descripción'), sg.InputText(key='-DESCRIPTION-')],
        [sg.FilesBrowse('Buscar Archivos', file_types=(("Todos los Archivos", "*.*"),), target='-FILEPATH-'),
         sg.InputText(key='-FILEPATH-')],
        [sg.Button('Guardar', key='-SAVE-')]
    ]
    #ventana se finaliza después de su creación (finalize=True) y se desactiva el botón de cierre (disable_close=True)
    return sg.Window('Añadir Nuevo Archivo', layout, finalize=True)


def create_files_window(item):
    files = gdu.get_files_in_zip("File"+item[4])  # Obtener la lista de archivos contenidos en el elemento seleccionado
    file_list = [[file] for file in files]  # Convertir la lista de archivos en un formato adecuado para la ventana

    layout = [
        [sg.Text(f'Archivos del elemento seleccionado: {item[1]}')],
        [sg.Listbox(values=file_list, size=(100, 10), select_mode='extended', key='-FILES_LIST-')],  # Listbox con select_mode='extended'        
        [sg.Button('Descargar Archivo', key='-DOWNLOAD-')]
    ]
    return sg.Window('Archivo Comprimidos', layout, finalize=True)

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

    if event == '-ADD-' and not add_window:
        add_window = create_add_window()
    
    if event == '-SAVE-':
        title = values['-TITLE-']
        description = values['-DESCRIPTION-']
        files = values['-FILEPATH-'].split(';')  # Convierte la cadena en una lista

        # Asegúrate de que cada archivo en files es un path válido antes de proceder
        valid_files = [file for file in files if os.path.isfile(file)]

        try:
            zp(valid_files,title,description)  # Asegúrate de que la función ZipFile ahora acepta una lista de archivos
            sg.popup('Documento guardado con éxito')
        except Exception as e:
            sg.popup_error(f'Error al guardar el documento: {e}')

        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")

        # Construye un nuevo registro para la tabla
        nuevo_documento = [len(data) + 1, title, description, current_time]

        # Añade el nuevo documento a la lista de datos
        data.append(nuevo_documento)
        # Actualiza la tabla en la ventana principal
        main_window['-TABLE-'].update(values=data)

        add_window.close()
        add_window = None
        data=gdu.listar_los_zips()
    if event == '-SEE-':        
        
        selected_row_index = values['-TABLE-'][0]
        

        # Verificar si se seleccionó una fila
        if selected_row_index is not None:
            # Obtener los detalles del elemento seleccionado de la lista 'data'
            selected_item = data[selected_row_index]

            # Crear una ventana para mostrar los archivos contenidos en el elemento seleccionado
            show_files_window = create_files_window(selected_item)
    if event == '-DOWNLOAD-' and show_files_window is not None:
        selected_files = values['-FILES_LIST-']
        if selected_files:
            folder_path = sg.popup_get_folder('Seleccione la carpeta de destino')
            if folder_path:
                for file_name in selected_files:
                    file_name = ''.join(file_name)
                    gdu.get_file(file_name, "File"+selected_item[4],folder_path)
                    # Aquí puedes agregar el código para copiar el archivo a la carpeta de destino
                    pass
                sg.popup(f'Archivos descargados en: {folder_path}')



main_window.close()
if add_window:
    add_window.close()
if show_files_window:
    show_files_window.close()
