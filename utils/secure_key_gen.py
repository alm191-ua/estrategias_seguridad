import string
import random
import hashlib

AMBIGUOUS = '01lIO'
MORE_AMBIGUOUS = '1lIO0oO'

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


def generate_password(length, mode=0, uppercase=True, lowercase=True, digits=True, punctuation=True):
    """
    Generates a random (and secure) password of the specified length.

    Args:
        length (int): The length of the password.
        mode (int, optional): The mode of the password. Defaults to 0.
            0: All characters allowed.
            1: Easy to say characters only (avoid numbers and punctuation).
            2: Easy to read characters only (avoid similar/ambiguous characters and punctuation).
        uppercase (bool, optional): Include uppercase letters. Defaults to True.
        lowercase (bool, optional): Include lowercase letters. Defaults to True.
        digits (bool, optional): Include digits. Defaults to True.
        punctuation (bool, optional): Include punctuation. Defaults to True.

    Returns:
        str: The generated password.

    Raises:
        ValueError: If no characters are selected for password generation.
    """
    characters = ''
    if mode == 1:
        digits = False
        punctuation = False
    elif mode == 2:
        digits = False
        punctuation = False
        uppercase = True
        lowercase = True
    
    if uppercase:
        characters += string.ascii_uppercase
    if lowercase:
        characters += string.ascii_lowercase
    if digits:
        characters += string.digits
    if punctuation:
        characters += string.punctuation

    if mode == 1:
        characters = ''.join([c for c in characters if c not in AMBIGUOUS])
    elif mode == 2:
        characters = ''.join([c for c in characters if c not in MORE_AMBIGUOUS])

    if not characters:
        raise ValueError("No characters selected for password generation.")

    if mode == 1:
        password = easy_to_say_password(length, characters)
    else:
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

if __name__ == '__main__':
    passwd = generate_password(12, mode=1)
    print(f"Generated password: {passwd}")
    data_key, login_key = generate_keys(passwd)
    print(f"Data key: {data_key}")
    print(f"Login key: {login_key}")