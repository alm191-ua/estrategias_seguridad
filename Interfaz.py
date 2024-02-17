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
        [sg.Button('Añadir', key='-ADD-', button_color=('white', 'blue'))]
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
    return sg.Window('Añadir Nuevo Archivo', layout, finalize=True, disable_close=True)

file_list = []

main_window = create_main_window()
add_window = None

while True:
    window, event, values = sg.read_all_windows()
    
    if event == sg.WINDOW_CLOSED and window == main_window:
        break
    elif event == sg.WINDOW_CLOSED and window == add_window:
        add_window.close()
        add_window = None

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



main_window.close()
if add_window:
    add_window.close()
