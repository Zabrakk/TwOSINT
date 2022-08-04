import re
from argparse import Namespace
# TwOSINT files
from src.utils import print_error


def validate_args(args: Namespace) -> bool:
    if not correct_num_of_tweets(args.n):
        return False
    if args.start_time and not correct_start_time(args.start_time):
        return False
    if args.end_time and not correct_end_time(args.end_time):
        return False
    return True


def correct_num_of_tweets(val: int) -> bool:
    if val in range(5, 3201):
        return True
    print_error('Set -n to be between 5-3200')
    return False


def correct_start_time(val: str) -> bool:
    return check_time_format(val, 'Incorrect start_time format!')


def correct_end_time(val: str) -> bool:
    return check_time_format(val, 'Incorrect end_time format!')


def check_time_format(time_str: str, error_str: str) -> bool:
    """
    Ensures that the "YYYY-mm-ddThh:mm:ssT" format is used for timestamps
    :param time_str: Datetime as string
    :param error_str: Error to display if format is incorrect
    :return: True if correct; False otherwise
    """
    if re.search(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", time_str):
        return True
    print_error(error_str)
    return False
