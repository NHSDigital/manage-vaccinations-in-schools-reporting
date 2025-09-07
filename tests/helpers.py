from os import urandom


def create_random_token():
    return urandom(16).hex()
