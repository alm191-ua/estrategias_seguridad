import string
import random
import hashlib
import bcrypt

AMBIGUOUS = '01lIOo'

VOWELS = 'aeiouAEIOU'
CONSONANTS = 'bcdfghjklmnpqrstvwxyzBDFGHJKLMNPQRSTVWXYZ'
# GRAPHIES = ['ch', 'll', 'rr', 'rs', 'st', 'rt']

# intercalate vowels and consonants, or know graphies like ch or ll, rr, etc.
# lo de las grafías mejor no :)
def next_char(char):
    """
    Returns the next character in the sequence of easy to say characters.

    Args:
        char (str): The current character.

    Returns:
        str: The next character in the sequence.
    """
    if char in VOWELS:
        return random.choice(CONSONANTS)
    elif char in CONSONANTS:
        return random.choice(VOWELS)
    else:
        return VOWELS[0]

def easy_to_say_password(length, characters):
    """
    Generates a random (and secure) password of the specified length, using only easy to say characters.

    Args:
        length (int): The length of the password.
        characters (str): The characters to use for password generation.

    Returns:
        str: The generated password.
    """
    first_char = random.choice(characters)
    password = str(first_char)
    for i in range(length-1):
        password += next_char(password[-1])

    return password


def generate_password(length=8, use_uppercase=True, use_lowercase=True, use_digits=True, use_punctuation=True):
    """
    Generates a random password.
    
    Args:
        length (int): Length of the password. Min 5, Max 15.
        use_uppercase (bool): Include uppercase letters if True.
        use_lowercase (bool): Include lowercase letters if True.
        use_digits (bool): Include digits if True.
        use_punctuation (bool): Include punctuation symbols if True.
        
    Returns:
        str: The generated password.
    """
    if length < 5 or length > 15:
        raise ValueError("Length must be between 5 and 15.")
    
    characters = ""
    if use_uppercase:
        characters += string.ascii_uppercase
    if use_lowercase:
        characters += string.ascii_lowercase
    if use_digits:
        characters += string.digits
    if use_punctuation:
        characters += string.punctuation

    if not characters:
        raise ValueError("At least one character type must be selected.")
    
    return ''.join(random.choice(characters) for _ in range(length))

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
    full_hash = hashlib.sha3_256(psswd_bytes).hexdigest()

    # Generar clave de datos utilizando SHA-3 (SHA3-256 / 2)
    # cada caracter en hexadecimal son 4 bits (un nibble)
    # por lo que 32 caracteres son 128 bits
    data_key = full_hash[:32]

    # Generar clave de login utilizando SHA-3 (SHA3-256 / 2)
    login_key = full_hash[32:]

    return data_key, login_key

def hash_password(password):
    """
    Hashes a password using bcrypt.

    Args:
        password (str): The password to hash.

    Returns:
        str: The hashed password.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    return hashed

def check_password(password, hashed):
    """
    Checks if a password matches a hash.

    Args:
        password (str): The password to check.
        hashed (str): The hashed password.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

if __name__ == '__main__':
    passwd = generate_password(12, mode=1)
    print(f"Generated password: {passwd}")
    data_key, login_key = generate_keys(passwd)
    print(f"Data key: {data_key}")
    print(f"Login key: {login_key}")