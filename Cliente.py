import sys
from PyQt5 import QtWidgets, QtGui, QtCore

class LoginForm(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Interfaz Cliente")
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

        # Botón del ojo para mostrar/ocultar contraseña
        self.toggle_password_button = QtWidgets.QPushButton(self)
        self.toggle_password_button.setIcon(QtGui.QIcon("eye_icon.png"))  # Asegúrate de tener un ícono 'eye_icon.png'
        self.toggle_password_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.toggle_password_button.setStyleSheet("background: transparent; border: none;")
        self.toggle_password_button.clicked.connect(self.toggle_password_visibility)
        layout.addWidget(self.toggle_password_button)

        # Botón para iniciar sesión
        login_button = QtWidgets.QPushButton("Iniciar Sesión")
        login_button.setStyleSheet("QPushButton { background-color: #3498db; color: #ecf0f1; border-radius: 10px; padding: 10px; } QPushButton:hover { background-color: #2980b9; }")
        layout.addWidget(login_button)

        # Enlace para registrarse
        register_label = QtWidgets.QLabel("No tienes cuenta? Regístrate aquí")
        register_label.setStyleSheet("color: #ecf0f1; text-decoration: underline; margin-top: 15px;")
        layout.addWidget(register_label)

        register_label.mousePressEvent = self.open_register_window

        self.setLayout(layout)

    def open_register_window(self, event):
        print("Abriendo ventana de registro...")

    def toggle_password_visibility(self):
        if self.password_line_edit.echoMode() == QtWidgets.QLineEdit.Password:
            self.password_line_edit.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.password_line_edit.setEchoMode(QtWidgets.QLineEdit.Password)

app = QtWidgets.QApplication(sys.argv)
login_form = LoginForm()
login_form.show()
sys.exit(app.exec_())
