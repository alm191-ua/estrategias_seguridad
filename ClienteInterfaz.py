import sys
import socket
sys.path.append('./sockets')
#Importar la clase SocketCliente del módulo SocketCliente ademas de con la creación de __init__.py
from sockets import SocketCliente
from PyQt5 import QtWidgets, QtGui, QtCore
sys.path.append('..')
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

        #Campo de texto para el usuario
        self.username_line_edit = QtWidgets.QLineEdit()
        self.username_line_edit.setPlaceholderText("Usuario")
        self.username_line_edit.setStyleSheet("height: 40px; margin: 20px; padding: 5px; border-radius: 10px; color: #ecf0f1; background: #34495e;")
        layout.addWidget(self.username_line_edit)

        #Campo de texto para la contraseña
        self.password_line_edit = QtWidgets.QLineEdit()
        self.password_line_edit.setPlaceholderText("Contraseña")
        self.password_line_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_line_edit.setStyleSheet("height: 40px; margin: 20px; padding: 5px; border-radius: 10px; color: #ecf0f1; background: #34495e;")
        layout.addWidget(self.password_line_edit)

        #Botón para iniciar sesión
        login_button = QtWidgets.QPushButton("Iniciar Sesión")
        login_button.setStyleSheet("QPushButton { background-color: #3498db; color: #ecf0f1; border-radius: 10px; padding: 10px; } QPushButton:hover { background-color: #2980b9; }")
        #Conectar el botón con la función de comprobar usuario
        login_button.clicked.connect(lambda: self.comprobar_usuario(self.username_line_edit.text(), self.password_line_edit.text()))
        layout.addWidget(login_button)

        #Enlace para registrarse
        register_label = QtWidgets.QLabel("No tienes cuenta? Regístrate aquí")
        register_label.setStyleSheet("color: #ecf0f1; text-decoration: underline; margin-top: 15px;")
        layout.addWidget(register_label)

        register_label.mousePressEvent = self.open_register_window

        self.setLayout(layout)

    def open_register_window(self, event):
        #Abrir la ventana de registro
        self.registration_form = RegistrationForm()
        self.registration_form.show()
        
    def comprobar_usuario(self, username, password):
        """
        Comprueba si el usuario y la contraseña son correctos y muestra un mensaje de éxito o error.
        """
        try:
            self.cliente.connect()
            self.cliente.username = username
            self.cliente.password = password
            success = self.cliente.log_in()
            if success:
                QtWidgets.QMessageBox.information(self, "Éxito", "Inicio de sesión exitoso.")
                self.close()
                ui = ClienteUI(username, self.cliente)
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

        main_layout = QtWidgets.QVBoxLayout(self)

        #Campo de texto para el usuario
        self.username_line_edit = QtWidgets.QLineEdit()
        self.username_line_edit.setPlaceholderText("Nuevo Usuario")
        self.username_line_edit.setStyleSheet("height: 40px; margin: 20px; padding: 5px; border-radius: 10px; color: #ecf0f1; background: #34495e;")
        main_layout.addWidget(self.username_line_edit)

        #Campo de texto para la contraseña
        self.password_line_edit = QtWidgets.QLineEdit()
        self.password_line_edit.setPlaceholderText("Nueva Contraseña")
        self.password_line_edit.setStyleSheet("height: 40px; margin: 20px; padding: 5px; border-radius: 10px; color: #ecf0f1; background: #34495e;")
        main_layout.addWidget(self.password_line_edit)
        
        #Botón para registrar
        register_button = QtWidgets.QPushButton("Registrar")
        register_button.setStyleSheet("QPushButton { background-color: #3498db; color: #ecf0f1; border-radius: 10px; padding: 10px; } QPushButton:hover { background-color: #2980b9; }")
        #Conectar el botón con la función de registrar usuario
        register_button.clicked.connect(self.register_user)
        main_layout.addWidget(register_button)

        #Slider para seleccionar la longitud
        self.length_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.length_slider.setMinimum(5)
        self.length_slider.setMaximum(15)
        self.length_slider.setValue(8)
        self.length_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.length_slider.setTickInterval(1)
        main_layout.addWidget(self.length_slider)

        #Crear un layout horizontal para los checkboxes
        checkboxes_layout = QtWidgets.QHBoxLayout()

        #Añadir checkboxes para tipos de caracteres
        char_types_layout = QtWidgets.QVBoxLayout()
        self.uppercase_checkbox = QtWidgets.QCheckBox("Incluir mayúsculas")
        self.lowercase_checkbox = QtWidgets.QCheckBox("Incluir minúsculas", checked=True)
        self.digits_checkbox = QtWidgets.QCheckBox("Incluir números")
        self.punctuation_checkbox = QtWidgets.QCheckBox("Incluir símbolos")
        char_types_layout.addWidget(self.uppercase_checkbox)
        char_types_layout.addWidget(self.lowercase_checkbox)
        char_types_layout.addWidget(self.digits_checkbox)
        char_types_layout.addWidget(self.punctuation_checkbox)

        #Añadir checkboxes para facilidades
        facilities_layout = QtWidgets.QVBoxLayout()
        self.easy_to_read_checkbox = QtWidgets.QCheckBox("Fácil de leer")
        self.easy_to_say_checkbox = QtWidgets.QCheckBox("Fácil de decir")
        facilities_layout.addWidget(self.easy_to_read_checkbox)
        facilities_layout.addWidget(self.easy_to_say_checkbox)

        #Añadir los layouts de checkboxes al layout horizontal
        checkboxes_layout.addLayout(char_types_layout)
        checkboxes_layout.addLayout(facilities_layout)

        #Añadir el layout de checkboxes al layout principal
        main_layout.addLayout(checkboxes_layout)

        #Botón para generar contraseña
        generate_password_button = QtWidgets.QPushButton("Generar Contraseña")
        generate_password_button.setStyleSheet("QPushButton { background-color: #3498db; color: #ecf0f1; border-radius: 10px; padding: 10px; } QPushButton:hover { background-color: #2980b9; }")
        #Conectar el botón con la función de generar contraseña
        generate_password_button.clicked.connect(self.generate_password)
        main_layout.addWidget(generate_password_button)
        

    def generate_password(self):
        length = self.length_slider.value()
        use_uppercase = self.uppercase_checkbox.isChecked()
        use_lowercase = self.lowercase_checkbox.isChecked()
        use_digits = self.digits_checkbox.isChecked()
        use_punctuation = self.punctuation_checkbox.isChecked()
        easy_to_read = self.easy_to_read_checkbox.isChecked()
        easy_to_say = self.easy_to_say_checkbox.isChecked()
        password = generate_password(length=length, use_uppercase=use_uppercase, use_lowercase=use_lowercase, use_digits=use_digits, use_punctuation=use_punctuation, easy_to_read=easy_to_read, easy_to_say=easy_to_say)
        self.password_line_edit.setText(password)



    def register_user(self):
        """
        Registra un nuevo usuario en el servidor.
        """
        username = self.username_line_edit.text()
        password = self.password_line_edit.text()
        try:
            cliente = SocketCliente.SocketCliente()
            cliente.connect() 
            cliente.username = username
            cliente.password = password
            success = cliente.register_user() 
            if success:
                QtWidgets.QMessageBox.information(self, "Éxito", "Usuario registrado correctamente.")
                self.close()
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "No se pudo registrar el usuario.")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", str(e))

app = QtWidgets.QApplication(sys.argv)
login_form = LoginForm()
login_form.show()
sys.exit(app.exec_())