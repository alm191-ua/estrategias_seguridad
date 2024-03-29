import hashlib

def generar_claves(passwd):
    # Codificar la contraseña como bytes
    psswd_bytes = passwd.encode('utf-8')

    full_hash = hashlib.sha3_512(psswd_bytes).hexdigest()

    # Generar clave de datos utilizando SHA-3 (SHA3-512 / 2)
    # cada caracter en hexadecimal son 4 bits (un nibble)
    # por lo que 64 caracteres son 256 bits
    clave_datos = full_hash[:64]

    # Generar clave de login utilizando SHA-3 (SHA3-512 / 2)
    clave_login = full_hash[64:]

    return clave_datos, clave_login

def main():
    passwd = "hola1234"
    clave_datos, clave_login = generar_claves(passwd)
    print(f"Clave de datos: {clave_datos}")
    print(f"Clave de login: {clave_login}")

if __name__ == '__main__':
    main()