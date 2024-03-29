import sys
import socket
sys.path.append('./sockets')
import SocketPadre
import SocketCliente
import SocketServidor
from PyQt5 import QtWidgets, QtGui, QtCore
import os
import json

class LoginForm(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
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
        #Enviar mensaje a SockerServidor y que este lo compruebe y si esta bien que reciba el True
        #y si esta mal que reciba el False
        self.cliente = SocketCliente.SocketCliente()
        #Pasar contraseña y usuario
        self.cliente.username = username
        self.cliente.password = password
        self.cliente.start()
        self.cliente.choose_option(1)
        if self.cliente.comprobar_usuario(username, password):
            self.interfaz_cliente = InterfazCliente()
            self.interfaz_cliente.cliente = self.cliente
            self.interfaz_cliente.show()
            self.close()
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos.")
            


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

        self.setLayout(layout)

    def register_user(self):
        username = self.username_line_edit.text()
        password = self.password_line_edit.text()

        # Aquí deberías verificar y almacenar el usuario
        if username and password:  # Asegurarse de que ambos campos estén llenos
            users_file = "server/users.json"
            if os.path.exists(users_file):
                with open(users_file, "r") as file:
                    users = json.load(file)
            else:
                users = []

            # Verificar si el usuario ya existe
            for user in users:
                if user["username"] == username:
                    QtWidgets.QMessageBox.warning(self, "Error", "El usuario ya existe.")
                    return

            # Añadir nuevo usuario
            new_user = {"id": len(users) + 1, "username": username, "password": password}
            users.append(new_user)
            print(new_user)
            with open(users_file, "w") as file:
                json.dump(users, file, indent=4)

            QtWidgets.QMessageBox.information(self, "Éxito", "Usuario registrado exitosamente.")
            self.close()
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Por favor, rellene todos los campos.")
            

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