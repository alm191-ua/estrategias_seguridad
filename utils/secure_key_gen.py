import string
import random
import hashlib

def generate_password(length):
    """
    Generates a random (and secure) password of the specified length.

    Args:
        length (int): The length of the password.

    Returns:
        str: The generated password.
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

def generate_keys(passwd):
    """
    Generates data and login keys using SHA-3 (SHA3-512).\n
    The resulting hash is divided into two parts, each 256 bits long.

    Args:
        passwd (str): The password to hash.

    Returns:
        tuple: A tuple containing the data and login keys.

    """

    # Codificar la contraseña como bytes
    psswd_bytes = passwd.encode('utf-8')
    full_hash = hashlib.sha3_512(psswd_bytes).hexdigest()

    # Generar clave de datos utilizando SHA-3 (SHA3-512 / 2)
    # cada caracter en hexadecimal son 4 bits (un nibble)
    # por lo que 64 caracteres son 256 bits
    data_key = full_hash[:64]

    # Generar clave de login utilizando SHA-3 (SHA3-512 / 2)
    login_key = full_hash[64:]

    return data_key, login_key