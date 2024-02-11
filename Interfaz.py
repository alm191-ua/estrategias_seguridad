import PySimpleGUI as sg
#para el manejo de archivos
import os

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
        [sg.FileBrowse('Buscar Archivos', file_types=(("Todos los Archivos", "*.*"),), target='-FILEPATH-'),
         sg.InputText(key='-FILEPATH-')],
        [sg.Button('Guardar', key='-SAVE-')]
    ]
    return sg.Window('Añadir Nuevo Archivo', layout, modal=False)


file_list = []

main_window = create_main_window()
add_window = None
while True:
    window, event, values = sg.read_all_windows()
    
    if event == sg.WINDOW_CLOSED:
        if window == main_window: 
            break
        elif window == add_window:
            add_window.close()
            add_window = None
    
    if event == '-ADD-':
        #comprobacion de que vaya a esta instruccion
        print("add")
        add_window = create_add_window()
    
    if event == '-SAVE-':
        file_info = {
            'title': values['-TITLE-'],
            'description': values['-DESCRIPTION-'],
            'path': values['-FILEPATH-']
        }
        file_list.append(file_info)
        main_window['-FILE LIST-'].update([f"{file['title']} - {file['description']}" for file in file_list])
        add_window.close()
        add_window = None

main_window.close()
if add_window:
    add_window.close()
