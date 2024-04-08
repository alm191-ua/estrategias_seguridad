import sys
import socket
sys.path.append('./sockets')
# Importar la clase SocketCliente del módulo SocketCliente ademas de con la creación de __init__.py
from sockets import SocketCliente
from PyQt5 import QtWidgets, QtGui, QtCore
sys.path.append('..')  # Ajusta según sea necesario para tu estructura de proyecto
from interfaces.Interfaz import ClienteUI
from utils.secure_key_gen import generate_password

class LoginForm(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        #Se crea una instancia de la clase SocketCliente
        self.cliente = SocketCliente.SocketCliente()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Login")
        self.setFixedSize(600, 400)
        self.setStyleSheet("background-color: #2c3e51;")

        layout = QtWidgets.QVBoxLayout()

        # Campo de texto para el usuario
        self.username_line_edit = QtWidgets.QLineEdit()
        self.username_line_edit.setPlaceholderText("Usuario")
        self.username_line_edit.setStyleSheet("height: 40px; margin: 20px; padding: 5px; border-radius: 10px; color: #ecf0f1; background: #34495e;")
        layout.addWidget(self.username_line_edit)

        # Campo de texto para la contraseña
        self.password_line_edit = QtWidgets.QLineEdit()
        self.password_line_edit.setPlaceholderText("Contraseña")
        self.password_line_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_line_edit.setStyleSheet("height: 40px; margin: 20px; padding: 5px; border-radius: 10px; color: #ecf0f1; background: #34495e;")
        layout.addWidget(self.password_line_edit)

        # Botón para iniciar sesión
        login_button = QtWidgets.QPushButton("Iniciar Sesión")
        login_button.setStyleSheet("QPushButton { background-color: #3498db; color: #ecf0f1; border-radius: 10px; padding: 10px; } QPushButton:hover { background-color: #2980b9; }")
        # Conectar el botón con la función de comprobar usuario
        login_button.clicked.connect(lambda: self.comprobar_usuario(self.username_line_edit.text(), self.password_line_edit.text()))
        layout.addWidget(login_button)

        # Enlace para registrarse
        register_label = QtWidgets.QLabel("No tienes cuenta? Regístrate aquí")
        register_label.setStyleSheet("color: #ecf0f1; text-decoration: underline; margin-top: 15px;")
        layout.addWidget(register_label)

        register_label.mousePressEvent = self.open_register_window

        self.setLayout(layout)

    def open_register_window(self, event):
        self.registration_form = RegistrationForm()
        self.registration_form.show()
        
    def comprobar_usuario(self, username, password):
        try:
            self.cliente.connect()
            self.cliente.username = username
            self.cliente.password = password
            success = self.cliente.log_in()
            if success:
                QtWidgets.QMessageBox.information(self, "Éxito", "Inicio de sesión exitoso.")
                self.close()
                ui = ClienteUI(username)
                ui.run()
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos.")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", str(e))
            print(e)
            


class RegistrationForm(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Registro")
        self.setFixedSize(600, 400)
        self.setStyleSheet("background-color: #2c3e51;")

        layout = QtWidgets.QVBoxLayout()

        self.username_line_edit = QtWidgets.QLineEdit()
        self.username_line_edit.setPlaceholderText("Nuevo Usuario")
        self.username_line_edit.setStyleSheet("height: 40px; margin: 20px; padding: 5px; border-radius: 10px; color: #ecf0f1; background: #34495e;")
        layout.addWidget(self.username_line_edit)

        self.password_line_edit = QtWidgets.QLineEdit()
        self.password_line_edit.setPlaceholderText("Nueva Contraseña")
        self.password_line_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_line_edit.setStyleSheet("height: 40px; margin: 20px; padding: 5px; border-radius: 10px; color: #ecf0f1; background: #34495e;")
        layout.addWidget(self.password_line_edit)

        register_button = QtWidgets.QPushButton("Registrar")
        register_button.setStyleSheet("QPushButton { background-color: #3498db; color: #ecf0f1; border-radius: 10px; padding: 10px; } QPushButton:hover { background-color: #2980b9; }")
        register_button.clicked.connect(self.register_user)
        layout.addWidget(register_button)

        # Estilización del QComboBox para seleccionar la complejidad de la contraseña
        self.complexity_combo = QtWidgets.QComboBox()
        self.complexity_combo.addItem("Baja", 0)
        self.complexity_combo.addItem("Media", 1)
        self.complexity_combo.addItem("Alta", 2)
        self.complexity_combo.setStyleSheet("QComboBox { height: 40px; margin: 20px; padding: 5px; border-radius: 10px; color: #ecf0f1; background: #34495e; }")

        # Estilización del botón para generar la contraseña
        generate_password_button = QtWidgets.QPushButton("Generar Contraseña")
        generate_password_button.setStyleSheet("QPushButton { background-color: #3498db; color: #ecf0f1; border-radius: 10px; padding: 10px; } QPushButton:hover { background-color: #2980b9; }")
        generate_password_button.clicked.connect(self.generate_password)

        layout.addWidget(self.complexity_combo)
        layout.addWidget(generate_password_button)

        self.setLayout(layout)

        
    def generate_password(self):
        complexity = self.complexity_combo.currentData()
        if complexity == 0:
            # Baja complejidad: solo letras minúsculas y longitud 8
            password = generate_password(length=8, uppercase=False, digits=False, punctuation=False)
        elif complexity == 1:
            # Complejidad media: letras y números, longitud 10
            password = generate_password(length=10, uppercase=True, punctuation=False)
        else:
            # Alta complejidad: todos los caracteres, longitud 12
            password = generate_password(length=12)
        
        self.password_line_edit.setText(password)


    def register_user(self):
        username = self.username_line_edit.text()
        password = self.password_line_edit.text()
        try:
            cliente = SocketCliente.SocketCliente()  # Crear una nueva instancia para el registro
            cliente.connect()  # Conectar con el servidor
            cliente.username = username
            cliente.password = password
            success = cliente.register_user()  # Intentar registrar el usuario
            if success:
                QtWidgets.QMessageBox.information(self, "Éxito", "Usuario registrado correctamente.")
                self.close()  # Cerrar la ventana de registro o abrir la ventana de login
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "No se pudo registrar el usuario.")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", str(e))
            

class InterfazCliente(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Cliente")
        self.setFixedSize(600, 400)
        self.setStyleSheet("background-color: #2c3e51;")

        layout = QtWidgets.QVBoxLayout()

        self.message_list = QtWidgets.QListWidget()
        self.message_list.setStyleSheet("background: #34495e; color: #ecf0f1; padding: 10px; border-radius: 10px; margin: 20px;")
        layout.addWidget(self.message_list)

        self.message_line_edit = QtWidgets.QLineEdit()
        self.message_line_edit.setStyleSheet("height: 40px; margin: 20px; padding: 5px; border-radius: 10px; color: #ecf0f1; background: #34495e;")
        layout.addWidget(self.message_line_edit)

        send_button = QtWidgets.QPushButton("Enviar")
        send_button.setStyleSheet("QPushButton { background-color: #3498db; color: #ecf0f1; border-radius: 10px; padding: 10px; } QPushButton:hover { background-color: #2980b9; }")
        send_button.clicked.connect(self.enviar_mensaje)
        layout.addWidget(send_button)

        self.setLayout(layout)

    def enviar_mensaje(self):
        message = self.message_line_edit.text()
        self.cliente.enviar_mensaje(message)
        self.message_line_edit.clear()

    def recibir_mensaje(self, message):
        self.message_list.addItem(message)

app = QtWidgets.QApplication(sys.argv)
login_form = LoginForm()
login_form.show()
sys.exit(app.exec_())