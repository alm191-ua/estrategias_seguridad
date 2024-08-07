import string
import random
import hashlib
import bcrypt
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import pyotp 
import qrcode
from PIL import ImageQt

KEY_SIZE = 2048

AMBIGUOUS = '01lIOo'

VOWELS_MIN = 'aeiou'
VOWELS_MAJ = 'AEIOU'
CONSONANTS_MIN = 'bcdfghjklmnpqrstvwxyz'
CONSONANTS_MAJ = 'BCDFGHJKLMNPQRSTVWXYZ'
# GRAPHIES = ['ch', 'll', 'rr', 'rs', 'st', 'rt']

# intercalate vowels and consonants, or know graphies like ch or ll, rr, etc.
# lo de las grafías mejor no :)
def next_char(char, lowercase=True, uppercase=True):
    """
    Returns the next character in the sequence of easy to say characters.

    Args:
        char (str): The current character.

    Returns:
        str: The next character in the sequence.
    """
    vowels = (VOWELS_MIN if lowercase else '') + (VOWELS_MAJ if uppercase else '')
    consonants = (CONSONANTS_MIN if lowercase else '') + (CONSONANTS_MAJ if uppercase else '')
    if not lowercase and not uppercase:
        vowels = VOWELS_MIN
        consonants = CONSONANTS_MIN
    if char in vowels:
        return random.choice(consonants)
    elif char in consonants:
        return random.choice(vowels)
    else:
        return random.choice(consonants)

def easy_to_say_password(length, lowercase=True, uppercase=True):
    """
    Generates a random (and secure) password of the specified length, using only easy to say characters.
    The password will alternate between vowels and consonants, and only letters will be used.
    If no character type is selected, lowercase characters will be used by default.
    
    Args:
        length (int): The length of the password.
        lowercase (bool): Whether to include lowercase characters.
        uppercase (bool): Whether to include uppercase characters.

    Returns:
        str: The generated password.
    """
    characters = ''
    if lowercase:
        characters += string.ascii_lowercase
    if uppercase:
        characters += string.ascii_uppercase
    if not characters:
        characters = string.ascii_lowercase

    first_char = random.choice(characters)
    password = str(first_char)
    for i in range(length-1):
        password += next_char(password[-1], lowercase, uppercase)

    return password


def generate_password(length=8, use_uppercase=True, use_lowercase=True, use_digits=True, use_punctuation=True, easy_to_read=False, easy_to_say=False):
    """
    Generates a random password considering the given parameters.

    Args:
        length (int): The length of the password.
        use_uppercase (bool, optional): Include uppercase letters. Defaults to True.
        use_lowercase (bool, optional): Include lowercase letters. Defaults to True.
        use_digits (bool, optional): Include digits. Defaults to True.
        use_punctuation (bool, optional): Include punctuation. Defaults to True.
        easy_to_read (bool, optional): Generate a password that is easy to read. Defaults to False.
        easy_to_say (bool, optional): Generate a password that is easy to say. Defaults to False.

    Returns:
        str: The generated password.
    """
    if easy_to_read or easy_to_say:
        use_digits = False
        use_punctuation = False

    characters = ''
    if use_uppercase:
        characters += string.ascii_uppercase
    if use_lowercase:
        characters += string.ascii_lowercase
    if use_digits:
        characters += string.digits
    if use_punctuation:
        characters += string.punctuation
    if easy_to_say:
        return easy_to_say_password(length, use_lowercase, use_uppercase)

    if easy_to_read:
        characters = ''.join(c for c in characters if c not in 'l1Io0O')

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

def generate_pub_priv_keys():
    """
    Generates a pair of public and private keys using RSA.

    Returns:
        tuple: A tuple containing the public and private keys.
    """
    key = RSA.generate(KEY_SIZE)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return public_key, private_key

def cipher_data(data, public_key):
    """
    Ciphers data using the public key.

    Args:
        data (str): The data to cipher.
        public_key (str): The public key.

    Returns:
        str(hex): The ciphered data.
    """
    key = RSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(key)
    if type(data) is not bytes:
        data = data.encode('utf-8')
    ctext = cipher.encrypt(data)
    # print("The cipher text type is: ", type(ctext))
    return ctext.hex()

def decipher_data(data, private_key):
    """
    Deciphers data using the private key.

    Args:
        data (str): The data to decipher.
        private_key (str): The private key.

    Returns:
        str: The deciphered data.
    """
    key = RSA.import_key(private_key)
    cipher = PKCS1_OAEP.new(key)
    return cipher.decrypt(bytes.fromhex(data))

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

def gen_otp_key():
    """
    Generates an OTP key.

    Returns:
        str: The OTP key.
    """
    return pyotp.random_base32()

def gen_otp_uri(account_name, key):
    """
    Generates an OTP URI.

    Args:
        account_name (str): The account name.
        key (str): The key.

    Returns:
        str: The OTP URI.
    """
    return pyotp.totp.TOTP(key).provisioning_uri(
        name='login:'+account_name, 
        issuer_name='ES')

def verify_otp(key, code):
    """
    Verifies an OTP code.

    Args:
        key (str): The key.
        code (str): The code.

    Returns:
        bool: True if the code is valid, False otherwise.
    """
    totp = pyotp.TOTP(key)
    return totp.verify(code)

def generate_otp_qr(uri):
    """
    Generates a QR code for an OTP URI.

    Args:
        uri (str): The URI.

    Returns:
        None
    """
    return ImageQt(qrcode.make(uri))

if __name__ == '__main__':
    passwd = generate_password(12, mode=1)
    print(f"Generated password: {passwd}")
    data_key, login_key = generate_keys(passwd)
    print(f"Data key: {data_key}")
    print(f"Login key: {login_key}")