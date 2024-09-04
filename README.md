# Proyecto de Estrategias de Seguridad

Este repositorio contiene la implementación de un sistema de archivos seguro con una interfaz gráfica que permite encriptar y desencriptar archivos, así como gestionar su acceso de manera segura o insegura.

> NOTA: Para más detalles ver la memoria del proyecto [aquí](ES-Practica3.pdf).

## Integrantes
- Alejandro Molines Molina
- Akira Llorens Montero
- Hugo Hernández López

## Curso
2023/2024

## Índice
1. [Descripción general de los archivos entregados](#descripción-general-de-los-archivos)
2. [Cómo ejecutar la aplicación](#como-ejecutar-la-aplicacion)
3. [Funcionalidades de la Aplicación de Cifrado](#funcionalidades-de-la-aplicacion-de-cifrado)
4. [Funcionalidades del Cliente Malicioso](#funcionalidades-del-cliente-malicioso)

## Descripción general de los archivos

La estructura del proyecto se organiza en dos directorios principales: `Servidor` y `Cliente`, cada uno con sus respectivos archivos y subdirectorios.

### Directorio Servidor
- **certificates/**: Certificados y claves SSL.
- **logs/**: Registros de eventos y errores.
- **server/**: Datos de usuarios (`users.json`), documentos encriptados, claves, y archivos JSON.
- **sockets/**: Módulos para la gestión de conexiones (incluye `socketServidor.py`).
- **utils/**: Herramientas de soporte, como la generación de claves.

### Directorio Cliente
- **certificates/**: Certificados para la verificación del servidor.
- **files/**: Archivos del cliente para enviar al servidor.
- **interfaces/**: Interfaz gráfica (`Interfaz.py`) y cliente malicioso (`ClienteMalicioso.py`).
- **logs/**: Registros de eventos y errores del cliente.
- **sockets/**: Gestión de conexiones del cliente (incluye `socketCliente.py`).
- **utils/**: Scripts auxiliares para tareas como encriptación de archivos.
- **ClienteInterfaz.py**: Registro e inicio de sesión mediante interfaz.
- **GetDataUploaded.py**: Organización de documentos y recuperación de metadatos.

### Archivos Comunes
- **config.json**: Configuración necesaria para la comunicación.
- **requirements.txt**: Dependencias necesarias para ejecutar la aplicación.
- **Cifrado.py**: Métodos para el cifrado y descifrado de documentos.

## Cómo ejecutar la aplicación

Para ejecutar la aplicación basta con descomprimir [este fichero](ejecutables/Servidor.zip) y ejecutar el ejecutable que contiene y [el ejecutable del cliente](ejecutables/ClienteInterfaz.exe).

## Funcionalidades de la Aplicación de Cifrado

### Interfaz de Usuario
- **Inicio de Sesión**: Los usuarios pueden autenticarse mediante una interfaz gráfica que solicita nombre de usuario y contraseña.
- **Registro de Usuarios**: Permite crear nuevas cuentas con validaciones de seguridad, incluyendo:
  - Nombre de usuario con al menos 5 caracteres.
  - Contraseña con un mínimo de 8 caracteres.
  - Opción de autenticación de doble factor (OTP) con generación de código QR para aplicaciones como Google Authenticator.
- **Modo Seguro/Inseguro**: La aplicación permite alternar entre modos de seguridad, activando o desactivando ciertas restricciones.

### Gestión de Archivos
- **Añadir Archivos**:
  - Los usuarios pueden seleccionar múltiples archivos para comprimir y cifrar.
  - Se debe proporcionar un título y una descripción para cada conjunto de archivos.
  - Opción para compartir archivos con otros usuarios registrados seleccionándolos de una lista.
- **Visualización de Archivos**:
  - Listado de archivos propios y compartidos por otros usuarios.
  - Información detallada de cada archivo, incluyendo título, descripción, fecha de creación y autor.
- **Descarga de Archivos**:
  - Los usuarios pueden descargar archivos individuales o múltiples archivos desde un archivo comprimido.
  - Los archivos se descifran automáticamente al ser descargados, utilizando la clave almacenada asociada al usuario.

### Seguridad y Cifrado
- **Cifrado de Archivos**:
  - Utiliza el algoritmo AES-256 en modo CTR para cifrar archivos.
  - Genera una clave de cifrado única para cada archivo, almacenada de forma segura.
- **Autenticación de Doble Factor (OTP)**:
  - Los usuarios pueden habilitar la autenticación OTP durante el registro.
  - Al iniciar sesión, se solicita un token temporal generado por una aplicación de autenticación compatible.
- **Compartir Archivos**:
  - Los archivos compartidos se cifran utilizando claves públicas de los usuarios destinatarios.
  - Solo los usuarios autorizados pueden descifrar y acceder a los archivos compartidos con ellos.

## Funcionalidades del Cliente Malicioso

### Acceso en Modo Inseguro
- **Servidor en Modo Inseguro**: El cliente malicioso puede acceder a documentos cuando el servidor está configurado en modo inseguro.
- **Acceso sin Autenticación**:
  - Es posible acceder a la aplicación sin proporcionar un nombre de usuario o contraseña.
  - Los usuarios pueden ver todos los documentos almacenados en el servidor, independientemente de su propietario.

### Descifrado de Documentos
- **Descarga de Archivos Cifrados con Claves Inseguras**:
  - Permite descargar y descifrar archivos que fueron cifrados con contraseñas o claves inseguras.
  - Si un documento fue cifrado de forma segura, el cliente malicioso no podrá acceder a su contenido y recibirá un mensaje de error.
- **Interfaz de Usuario**:
  - Similar a la aplicación principal pero con funcionalidades limitadas.
  - No permite subir nuevos documentos al servidor.
  - Muestra una lista completa de documentos disponibles en el servidor para su visualización y descarga.

### Limitaciones y Advertencias
- **Limitaciones**:
  - El cliente malicioso no puede acceder a documentos cifrados de forma segura.
  - No puede subir documentos ni modificar los existentes.
- **Advertencias de Seguridad**:
  - El uso del cliente malicioso demuestra la importancia de mantener el servidor en modo seguro.
  - Destaca la necesidad de utilizar contraseñas y claves seguras para proteger los documentos.

---

Estas funcionalidades permiten a los usuarios interactuar con un sistema de archivos cifrado, ofreciendo opciones de seguridad avanzadas como el cifrado AES-256, autenticación de doble factor y compartición segura de archivos. El cliente malicioso sirve como una herramienta para evidenciar las vulnerabilidades que existen cuando se utilizan claves inseguras o se opera en modo inseguro.



