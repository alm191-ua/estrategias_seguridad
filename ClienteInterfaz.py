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
        self.setStyleSheet("background-color: #2c3e51; color:white;")

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
                QtWidgets.QMessageBox().warning(self, "Error", "Usuario o contraseña incorrectos.")
                self.cliente.disconnect()

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", str(e))
            self.cliente.disconnect()
            print(e)
            


class RegistrationForm(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Registro")
        self.setFixedSize(600, 350)
        self.setStyleSheet("background-color: #2c3e51; color: white;")

        self.main_layout = QtWidgets.QVBoxLayout(self)

        #Campo de texto para el usuario
        self.username_line_edit = QtWidgets.QLineEdit()
        self.username_line_edit.setPlaceholderText("Nuevo Usuario")
        self.username_line_edit.setStyleSheet("height: 40px; margin: 20px; padding: 5px; border-radius: 10px; color: #ecf0f1; background: #34495e;")
        self.main_layout.addWidget(self.username_line_edit)

        #Campo de texto para la contraseña
        self.password_line_edit = QtWidgets.QLineEdit()
        self.password_line_edit.setPlaceholderText("Nueva Contraseña")
        self.password_line_edit.setStyleSheet("height: 40px; margin: 20px; padding: 5px; border-radius: 10px; color: #ecf0f1; background: #34495e;")
        self.main_layout.addWidget(self.password_line_edit)
        
        #Botón para registrar
        register_button = QtWidgets.QPushButton("Registrar")
        register_button.setStyleSheet("QPushButton { background-color: #3498db; color: #ecf0f1; border-radius: 10px; padding: 10px; } QPushButton:hover { background-color: #2980b9; }")
        #Conectar el botón con la función de registrar usuario
        register_button.clicked.connect(self.register_user)
        self.main_layout.addWidget(register_button)

        #Botón para mostrar layout de generación de contraseña
        show_generate_password_button = QtWidgets.QPushButton("Generador de Contraseña")
        show_generate_password_button.setStyleSheet("QPushButton { background-color: #3498db; color: #ecf0f1; border-radius: 10px; padding: 10px; } QPushButton:hover { background-color: #2980b9; }")
        show_generate_password_button.clicked.connect(self.show_generate_password_layout)
        self.main_layout.addWidget(show_generate_password_button)

        self.generate_password_layout = QtWidgets.QVBoxLayout()
        self.generate_password_layout.setEnabled(False)

        #Slider para seleccionar la longitud
        self.length_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.length_slider.setMinimum(5)
        self.length_slider.setMaximum(15)
        self.length_slider.setValue(8)
        self.length_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.length_slider.setTickInterval(1)
        self.generate_password_layout.addWidget(self.length_slider)

        #Crear un layout horizontal para los checkboxes
        checkboxes_layout = QtWidgets.QHBoxLayout()

        #Añadir checkboxes para tipos de caracteres
        char_types_layout = QtWidgets.QVBoxLayout()
        self.uppercase_checkbox = QtWidgets.QCheckBox("Incluir mayúsculas", checked=True)
        self.lowercase_checkbox = QtWidgets.QCheckBox("Incluir minúsculas", checked=True)
        self.digits_checkbox = QtWidgets.QCheckBox("Incluir números", checked=True)
        self.punctuation_checkbox = QtWidgets.QCheckBox("Incluir símbolos", checked=True)
        self.uppercase_checkbox.setStyleSheet("color: #ecf0f1;")
        self.lowercase_checkbox.setStyleSheet("color: #ecf0f1;")
        self.digits_checkbox.setStyleSheet("color: #ecf0f1;")
        self.punctuation_checkbox.setStyleSheet("color: #ecf0f1;")
        char_types_layout.addWidget(self.uppercase_checkbox)
        char_types_layout.addWidget(self.lowercase_checkbox)
        char_types_layout.addWidget(self.digits_checkbox)
        char_types_layout.addWidget(self.punctuation_checkbox)


        facilities_layout = QtWidgets.QVBoxLayout()
        self.easy_to_read_radio = QtWidgets.QRadioButton("Fácil de leer")
        self.easy_to_say_radio = QtWidgets.QRadioButton("Fácil de decir")
        self.manual_radio = QtWidgets.QRadioButton("Manual", checked=True)
        self.easy_to_read_radio.setStyleSheet("color: #ecf0f1;")
        self.easy_to_say_radio.setStyleSheet("color: #ecf0f1;")
        self.manual_radio.setStyleSheet("color: #ecf0f1;")
        facilities_layout.addWidget(self.easy_to_read_radio)
        facilities_layout.addWidget(self.easy_to_say_radio)
        facilities_layout.addWidget(self.manual_radio)


        #Añadir los layouts de checkboxes al layout horizontal
        checkboxes_layout.addLayout(char_types_layout)
        checkboxes_layout.addLayout(facilities_layout)

        #Añadir el layout de checkboxes al layout principal
        self.generate_password_layout.addLayout(checkboxes_layout)

        #Botón para generar contraseña
        generate_password_button = QtWidgets.QPushButton("Generar Contraseña")
        generate_password_button.setStyleSheet("QPushButton { background-color: #3498db; color: #ecf0f1; border-radius: 10px; padding: 10px; } QPushButton:hover { background-color: #2980b9; }")
        #Conectar el botón con la función de generar contraseña
        generate_password_button.clicked.connect(self.generate_password)
        self.generate_password_layout.addWidget(generate_password_button)
        
    def show_generate_password_layout(self):
        """
        Muestra el layout de generación de contraseña.
        """
        self.generate_password_layout.setEnabled(True)
        #Añadir el layout de generación de contraseña al layout principal
        self.main_layout.addLayout(self.generate_password_layout)
        self.setFixedSize(600, 450)
        # hide button
        self.sender().hide()


    def generate_password(self):
        length = self.length_slider.value()
        use_uppercase = self.uppercase_checkbox.isChecked()
        use_lowercase = self.lowercase_checkbox.isChecked()
        use_digits = self.digits_checkbox.isChecked()
        use_punctuation = self.punctuation_checkbox.isChecked()
        easy_to_read = self.easy_to_read_radio.isChecked()
        easy_to_say = self.easy_to_say_radio.isChecked()

        if easy_to_read and easy_to_say:
            QtWidgets.QMessageBox.warning(self, "Error", "Selecciona 'Fácil de leer' o 'Fácil de decir', no ambos.")
            return

        try:
            password = generate_password(
                length=length, 
                use_uppercase=use_uppercase, 
                use_lowercase=use_lowercase, 
                use_digits=use_digits, 
                use_punctuation=use_punctuation, 
                easy_to_read=easy_to_read, 
                easy_to_say=easy_to_say
            )
            self.password_line_edit.setText(password)
        except ValueError as e:
            QtWidgets.QMessageBox.critical(self, "Error al generar la contraseña", str(e))


    def register_user(self):
        """
        Registra un nuevo usuario en el servidor.
        """
        username = self.username_line_edit.text()
        password = self.password_line_edit.text()
        cliente = SocketCliente.SocketCliente()
        cliente.connect() 
        try:
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
        
        cliente.disconnect()

app = QtWidgets.QApplication(sys.argv)
login_form = LoginForm()
login_form.show()
sys.exit(app.exec_())