import PySimpleGUI as sg
import os
from CrearZipYCodificar import ZipFile as zp


def create_main_window():
    layout = [
        [sg.Listbox(values=[], size=(60, 20), key='-FILE LIST-')],
        [sg.Button('Añadir', key='-ADD-', button_color=('white', 'blue'))]
    ]
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
        # Recoge el título y la descripción del documento desde la interfaz
        title = values['-TITLE-']
        description = values['-DESCRIPTION-']
        
        # Suponiendo que '-FILEPATH-' contiene la ruta de los archivos seleccionados, separados por ";"
        # Aquí se separan las rutas de archivos en una lista
        files = values['-FILEPATH-'].split(';')  # Esto podría necesitar ajustes dependiendo de tu implementación específica

        try:
            zp(files)
            sg.popup('Documento guardado con éxito')
        except Exception as e:
            sg.popup_error(f'Error al guardar el documento: {e}')

        file_info = {
            'title': title,
            'description': description,
            'files': files
        }
        file_list.append(file_info)
        main_window['-FILE LIST-'].update([f"{file['title']} - {file['description']}" for file in file_list])

        add_window.close()
        add_window = None


main_window.close()
if add_window:
    add_window.close()
