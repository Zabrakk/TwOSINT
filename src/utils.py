import os


def print_error(err: str) -> None:
    print('\033[91m#: ' + err + '\033[0m')


def create_folder(dir: str) -> None:
    try:
        if not os.path.exists(dir):
            os.mkdir(dir)
    except OSError as e:
        print_error(e)