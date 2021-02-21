import os
import pytest
from src.authentication import Authentication

"""
Tests the different functionalities of the Authentication class
"""


def test_from_arg():
    auth = Authentication()
    token = 'test_arg'
    assert auth.get_token(token)
    assert auth.get_header() == {'Authorization': 'Bearer {}'.format(token)}


def test_from_environment():
    auth = Authentication()
    token = 'test_environment'
    old_val = None
    try:
        old_val = os.environ['BEARER_TOKEN']
    except KeyError:
        pass
    os.environ['BEARER_TOKEN'] = token
    assert auth.get_token(None)
    assert auth.get_header() == {'Authorization': 'Bearer {}'.format(token)}
    del os.environ['BEARER_TOKEN']
    if old_val:
        os.environ['BEARER_TOKEN'] = old_val


def test_create_auth_file():
    auth = Authentication()
    filename = 'test/test_auth_file.txt'
    auth.create_auth_file(filename)
    assert os.path.exists(filename)
    assert open(filename, 'r').read() == 'bearer_token='
    if os.path.exists(filename):
        os.remove(filename)


def test_from_file():
    auth = Authentication()
    token = 'test_file'
    filename = 'test/test_auth_file.txt'
    open(filename, 'w').write('bearer_token={}'.format(token))
    assert auth.get_token(None, filename)
    assert auth.get_header() == {'Authorization': 'Bearer {}'.format(token)}
    os.remove(filename)
