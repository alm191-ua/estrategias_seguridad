import PySimpleGUI as sg
import os
from CrearZipYCodificar import decrypt_file_unsafe

def create_main_window():
    layout = [
        [sg.Text('File')],
        [sg.FileBrowse('Buscar Archivos', file_types=(("Ficheros encriptados", "*.enc"),), target='-FILEPATH-'),
            sg.InputText(key='-FILEPATH-')],
        [sg.Text('Target folder')],
        [sg.FolderBrowse(target='input'), sg.InputText(key='input'),]
        [sg.Button('Decrypt', key='decrypt')]
    ]
    return sg.Window('Descifrador', layout, finalize=True)

window = create_main_window()
while True:
    event, values = window.read()
    print("a")
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    if event == '-FILEPATH-':
        folder = values['-FILEPATH-']
        print(folder)  