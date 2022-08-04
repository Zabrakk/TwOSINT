import pytest
from src.argument_validator import validate_args, correct_num_of_tweets, check_time_format

"""
Tests the validation of user provided optional parameters
"""


class ArgsTester:
    def __init__(self) -> None:
        self.n = None
        self.start_time = None
        self.end_time = None


def test_check_num_tweets():
    # Correct number of tweets
    assert correct_num_of_tweets(5)
    args = ArgsTester()
    args.n = 5
    assert validate_args(args)
    # Incorrect number of tweets
    assert not correct_num_of_tweets(1)
    assert not correct_num_of_tweets(-1)
    assert not correct_num_of_tweets('a')
    assert not correct_num_of_tweets(None)
    assert not correct_num_of_tweets(3202)


def testcheck_time_format():
    # Correct times
    assert check_time_format('2020-15-15T10:10:52Z', 'Incorrect format')
    assert check_time_format('2020-10-10T10:10:52Z', 'Incorrect format')
    assert check_time_format('2020-15-05T10:10:52Z', 'Incorrect format')
    # Incorrect times
    assert not check_time_format('202-15-15T10:10:52Z', 'Incorrect format')
    assert not check_time_format('2020-15-5T10:10:52Z', 'Incorrect format')
    assert not check_time_format('2020-15-15T10:10:5Z', 'Incorrect format')
    assert not check_time_format('2020-15-15T10:1052Z', 'Incorrect format')
    assert not check_time_format('202015-15T10:10:52Z', 'Incorrect format')
    assert not check_time_format('2020-15-15 10:10:52Z', 'Incorrect format')
    assert not check_time_format('2020-15-15Z10:10:52', 'Incorrect format')
    assert not check_time_format('2020-15-15Z10:10:52T', 'Incorrect format')