import PySimpleGUI as sg
import os
import sys
import logging
sys.path.append('..')
from CrearZipYCodificar import decrypt_file_unsafe

# default folder
folder = os.path.join(os.path.expanduser("~"), "Downloads")

def create_main_window():
    layout = [
        [sg.Text('File')],
        [sg.FileBrowse('Search files', file_types=(("Ficheros encriptados", "*.enc"),), target='-FILEPATH-'),
            sg.InputText(key='-FILEPATH-')],
        [sg.Text('Target folder')],
        [sg.FolderBrowse('Select folder', target='-FOLDER-'), sg.InputText(key='-FOLDER-'),],
        [sg.Button('Decrypt', key='-DECRYPT-'), sg.Text(key='-OUTPUT-', size=(40, 2), text_color='red')],
    ]
    return sg.Window('Decrypter', layout, finalize=True)

window = create_main_window()
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    if event == '-DECRYPT-':
        new_folder = values['-FOLDER-']
        if new_folder:
            folder = new_folder
        else:
            print("Default folder:", folder)
        if not os.path.exists(folder):
            logging.warning("Folder does not exist")
            window['-OUTPUT-'].update("Folder does not exist")
            continue

        file = values['-FILEPATH-']
        if not file:
            logging.info("No file selected")
            window['-OUTPUT-'].update("No file selected")
            continue
        if not os.path.exists(file):
            logging.warning("File does not exist")
            window['-OUTPUT-'].update("File does not exist")
            continue
        try:
            decrypt_file_unsafe(file, folder)
            window['-OUTPUT-'].update("File decrypted")
        except Exception as e:
            logging.warning(f'Error decrypting file: {e}')
            window['-OUTPUT-'].update(f'Error decrypting file: {e}')