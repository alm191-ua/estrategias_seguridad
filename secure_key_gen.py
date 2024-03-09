import string
import random

def generate_password(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

def generate_key(length):
    key = generate_password(length)
    return bytes(key, 'utf-8')
    