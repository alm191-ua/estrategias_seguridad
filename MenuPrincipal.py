import subprocess
import PySimpleGUI as sg

sg.theme('Material2')  

def main():
    button_size = (25, 2)
    font_spec = ("Helvetica", 14)
    layout = [
        [sg.Text("Elige una opción para ejecutar:", font=("Helvetica", 18), pad=(0, 20))],
        [sg.Button("Administrador de Documentos", key="-INTERFAZ-", size=button_size, font=font_spec, mouseover_colors='#D3D3D3')],
        [sg.Button("Cliente Malicioso", key="-CLIENTE-", size=button_size, font=font_spec, mouseover_colors='#D3D3D3')],
        [sg.Button("Salir", key="Exit", size=button_size, font=font_spec)]
    ]
    window = sg.Window("Menú Principal", layout, element_justification='c', margins=(100, 50), finalize=True, use_default_focus=False)

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, "Exit"):
            break
        elif event == "-INTERFAZ-":
            window.hide()  
            subprocess.run(["python", "Interfaz.py"])
            window.un_hide()
        elif event == "-CLIENTE-":
            window.hide()
            subprocess.run(["python", "ClienteMalicioso.py"])
            window.un_hide()

    window.close()

if __name__ == "__main__":
    main()
