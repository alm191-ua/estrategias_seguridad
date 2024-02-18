import PySimpleGUI as sg
import os
from datetime import datetime
from CrearZipYCodificar import ZipFile as zp
import GetDataUploaded as gdu
from Logs import LoggerConfigurator 

sg.theme('Material2')

data = gdu.listar_los_zips()

def create_main_window():
    headings = ['Número', 'Título', 'Descripción', 'Tiempo de Creación']
    layout = [
        [sg.Table(values=data, headings=headings, max_col_width=25,
                  auto_size_columns=True, display_row_numbers=True, 
                  justification='left', num_rows=10, key='-TABLE-', 
                  row_height=25, text_color='black', alternating_row_color='lightblue')],
        [sg.Button('Añadir', key='-ADD-', button_color=('white', 'green'), size=(10, 1), font=("Helvetica", 12))]
    ]
    LoggerConfigurator.configure_log()
    LoggerConfigurator.Subdirectory("Interfaz")
    return sg.Window('Administrador de Archivos', layout, finalize=True, element_justification='center')

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
    return sg.Window('Añadir Nuevo Archivo', layout, finalize=True, disable_close=True, element_justification='center')

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
        files = values['-FILEPATH-'].split(';')
    
        valid_files = [f for f in files if os.path.exists(f)]

        try:
            zp(valid_files, title, description) 
            sg.popup('Documento guardado con éxito')
        except Exception as e:
            sg.popup_error(f'Error al guardar el documento: {e}')

        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")

        nuevo_documento = [len(data) + 1, title, description, current_time]
        data.append(nuevo_documento)
        main_window['-TABLE-'].update(values=data)

        add_window.close()
        add_window = None

main_window.close()
if add_window:
    add_window.close()
