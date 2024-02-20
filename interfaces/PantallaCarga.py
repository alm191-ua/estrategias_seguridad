import tkinter as tk
import time
import tkinter.ttk as ttk

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Pantalla de carga")
ancho_pantalla = ventana.winfo_screenwidth()
alto_pantalla = ventana.winfo_screenheight()
x = (ancho_pantalla - ventana.winfo_width()) / 2
y = (alto_pantalla - ventana.winfo_height()) / 2
ventana.geometry("+%d+%d" % (x, y))

# Crear una etiqueta para el mensaje de carga
etiqueta_mensaje = tk.Label(text="Cargando...")
etiqueta_mensaje.pack()

# Crear una barra de progreso
barra_progreso = tk.ttk.Progressbar(orient="horizontal", length=200, mode="indeterminate")
barra_progreso.pack()

# Función para cargar la interfaz "Interfaz.py"
def cargar_interfaz():
    # Ocultar la pantalla de carga
    ventana.withdraw()

    # Importar la interfaz "Interfaz.py"
    import Interfaz

    # Crear una instancia de la interfaz
    interfaz = Interfaz.create_main_window()

    # Mostrar la interfaz
    interfaz.mainloop()

# Simular el proceso de carga
for i in range(100):
    # Actualizar la barra de progreso
    barra_progreso.step()
    # Simular tiempo de carga
    ventana.update()
    time.sleep(0.05)

# Cambiar el mensaje y la barra de progreso al finalizar
etiqueta_mensaje.config(text="¡Carga completada!")
barra_progreso.stop()

# Cargar la interfaz "Interfaz.py" después de 2 segundos
ventana.after(2000, cargar_interfaz)

# Mostrar la ventana hasta que se cierre
ventana.mainloop()