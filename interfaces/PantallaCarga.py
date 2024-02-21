import PySimpleGUI as sg
import threading
import os
import subprocess


sg.theme('Material2')  # Choose a visually appealing theme

layout = [
    [sg.Text('Cargando Interfaz...', font=("Helvetica", 18), justification='center')],
    [sg.Text('', size=(30, 1), font=("Helvetica", 12), justification='center', key='-PROGRESS-')],
    #[sg.Image(filename='loading.gif', key='-IMAGE-')],  # Replace 'loading.gif' with your desired loading animation
]

window = sg.Window('Cargando...', layout, no_titlebar=True, grab_anywhere=True, keep_on_top=True)


def load_main_interface():
    subprocess.run(['python', 'Interfaz.py'])  # Launch the main interface


# Start a separate thread to load the main interface
thread = threading.Thread(target=load_main_interface)
thread.start()

while True:
    event, values = window.read(timeout=100)

    if event == sg.WINDOW_CLOSED:
        break

    # Update the progress bar with a simple animation
    progress_text = window['-PROGRESS-'].get()
    if progress_text == '':
        window['-PROGRESS-'].update('...')
    elif progress_text == '...':
        window['-PROGRESS-'].update(' ..')
    elif progress_text == ' ..':
        window['-PROGRESS-'].update('  .')
    else:
        window['-PROGRESS-'].update('')

    if os.path.exists('carga_completada.txt'):
        os.remove('carga_completada.txt')
        window.close()
        break
    # Check if the main interface has finished loading
    if not thread.is_alive() :
        window.close()  # Close the loading screen
        break

window.close()
