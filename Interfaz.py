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
        [sg.Button('Añadir', key='-ADD-', button_color=('white', 'green'), size=(10, 1), font=("Helvetica", 12)),
         sg.Button('Archivos', key='-SEE-', button_color=('white', 'blue'))
         ]
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
