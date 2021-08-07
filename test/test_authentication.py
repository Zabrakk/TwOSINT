import os
import pytest
from src.authentication import Authentication

"""
Tests the different functionalities of the Authentication class
"""


def test_from_arg():
    auth = Authentication(save_token=False)
    token = 'test_arg'
    assert auth.get_token(token)
    assert auth.get_header() == {'Authorization': 'Bearer {}'.format(token)}


def test_from_environment():
    auth = Authentication(save_token=False)
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
    filename = 'test/test_auth_file.txt'
    auth = Authentication(save_token=False)
    auth.store_token_to_file(filename, 'token')
    assert not os.path.exists(filename)

    auth = Authentication(save_token=True)
    auth.store_token_to_file(filename, 'token')
    assert os.path.exists(filename)
    with open(filename, 'r') as f:
        assert f.read() == 'bearer_token=token'
    if os.path.exists(filename):
        os.remove(filename)


def test_from_file():
    auth = Authentication(save_token=False)
    token = 'test_file'
    filename = 'test/test_auth_file.txt'
    open(filename, 'w').write('bearer_token={}'.format(token))
    assert auth.get_token(None, filename)
    assert auth.get_header() == {'Authorization': 'Bearer {}'.format(token)}
    os.remove(filename)
