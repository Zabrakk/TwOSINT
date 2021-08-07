import pytest
from src.api_handler import APIHandler
api_handler = APIHandler()

"""
Tests the different functionalities of the APIHandler class.
Note: Only tests URL related functions, not the actual call
"""


def test_decide_num_to_get():
    # Normal number of tweets
    assert api_handler.decide_num_to_get(5) == (5, 5)
    assert api_handler.decide_num_to_get(50) == (50, 50)
    assert api_handler.decide_num_to_get(100) == (100, 100)
    assert api_handler.decide_num_to_get(101) == (101, 100)
    assert api_handler.decide_num_to_get(3200) == (3200, 100)
    # Too small number of tweets
    assert api_handler.decide_num_to_get(4) == (5, 5)
    assert api_handler.decide_num_to_get(0) == (5, 5)
    assert api_handler.decide_num_to_get(-1) == (5, 5)
    # Too many tweets
    assert api_handler.decide_num_to_get(3201) == (3200, 100)
    assert api_handler.decide_num_to_get(4444444444444444444) == (3200, 100)
    # Replies excluded
    assert api_handler.decide_num_to_get(799, include_replies=False) == (799, 100)
    assert api_handler.decide_num_to_get(4, include_replies=False) == (5, 5)
    assert api_handler.decide_num_to_get(801, include_replies=False) == (800, 100)


def test_check_time_format():
    # Valid times
    assert api_handler.check_time_format('2020-15-15T10:10:52Z')
    assert api_handler.check_time_format('2020-10-10T10:10:52Z')
    assert api_handler.check_time_format('2020-15-05T10:10:52Z')
    # Invalid times
    assert not api_handler.check_time_format('202-15-15T10:10:52Z')
    assert not api_handler.check_time_format('2020-15-5T10:10:52Z')
    assert not api_handler.check_time_format('2020-15-15T10:10:5Z')
    assert not api_handler.check_time_format('2020-15-15T10:1052Z')
    assert not api_handler.check_time_format('202015-15T10:10:52Z')
    assert not api_handler.check_time_format('2020-15-15 10:10:52Z')
    assert not api_handler.check_time_format('2020-15-15Z10:10:52')
    assert not api_handler.check_time_format('2020-15-15Z10:10:52T')


def test_create_get_profile_url():
    assert api_handler.create_get_profile_url('test_user') == \
        'https://api.twitter.com/2/users/by/username/{}?user.fields=id,name,description,created_at,location,url,profile_image_url,public_metrics,verified'.format('test_user')


def test_create_get_tweets_url():
    id = '123'
    # Basic call with no optional params
    result = api_handler.create_get_tweets_url(id, 100)
    assert 'https://api.twitter.com/2/users/{}/tweets?'.format(id) in result
    assert 'max_results=100' in result
    assert not result.endswith('&')
    result = api_handler.create_get_tweets_url(id, 6)
    assert 'max_results=6' in result
    # Exclude retweets
    result = api_handler.create_get_tweets_url(id, 5, retweets=False)
    assert 'exclude=retweets' in result
    assert not result.endswith('&')
    # Exclude replies
    result = api_handler.create_get_tweets_url(id, 5, replies=False)
    assert 'exclude=replies' in result
    assert not result.endswith('&')
    # Exclude retweets and replies
    result = api_handler.create_get_tweets_url(id, 5, retweets=False, replies=False)
    assert 'exclude=retweets,replies' in result
    assert not result.endswith('&')
    # End time
    result = api_handler.create_get_tweets_url(id, 5, end_time='2015-10-10T10:10:01Z')
    assert 'end_time=2015-10-10T10:10:01Z' in result
    assert not result.endswith('&')
    # Invalid end time value
    result = api_handler.create_get_tweets_url(id, 5, end_time='2015-10-10 10:10:01')
    assert result is None
    # Start time
    result = api_handler.create_get_tweets_url(id, 5, start_time='2015-10-10T10:10:01Z')
    assert 'start_time=2015-10-10T10:10:01Z' in result
    assert not result.endswith('&')
    # Invalid start time value
    result = api_handler.create_get_tweets_url(id, 5, start_time='2015-10-10 10:10:01')
    assert result is None
    # All parameters together
    result = api_handler.create_get_tweets_url(id, 5, retweets=False, replies=False, start_time='2015-10-10T10:10:01Z', end_time='2017-10-10T10:10:01Z')
    assert 'https://api.twitter.com/2/users/{}/tweets?'.format(id) in result
    assert 'max_results=5&' in result
    assert '&exclude=retweets,replies&' in result
    assert '&start_time=2015-10-10T10:10:01Z&' in result
    assert '&end_time=2017-10-10T10:10:01Z' in result
    assert not result.endswith('&')


def test_update_url_results_num():
    old_num_to_get = 15
    new_num_to_get = 7
    url = api_handler.create_get_tweets_url('123', old_num_to_get)
    assert '?max_results={}'.format(new_num_to_get) in api_handler.update_url_results_num(url, old_num_to_get, new_num_to_get)[0]
    url = api_handler.create_get_tweets_url('123', old_num_to_get, retweets=False, start_time='2015-10-10T10:10:01Z')
    assert '?max_results={}&'.format(new_num_to_get) in api_handler.update_url_results_num(url, old_num_to_get, new_num_to_get)[0]
    assert api_handler.update_url_results_num(url, old_num_to_get, new_num_to_get)[1] == 7
    new_num_to_get = 4
    url = api_handler.create_get_tweets_url('123', old_num_to_get)
    assert '?max_results={}'.format(5) in api_handler.update_url_results_num(url, old_num_to_get, new_num_to_get)[0]
    assert api_handler.update_url_results_num(url, old_num_to_get, new_num_to_get)[1] == 5


def test_update_pagination_token():
    id = '123'
    token = 'the_token'
    url = api_handler.create_get_tweets_url(id, 5, retweets=False)
    url = api_handler.update_pagination_token(url, token)
    assert '&pagination_token={}'.format(token) in url
    assert not url.endswith('&')
    new_token = 'the_new_token'
    url = api_handler.update_pagination_token(url, new_token)
    assert '&pagination_token={}'.format(new_token) in url
    assert not 'pagination_token={}'.format(token) in url
    assert not url.endswith('&')


def test_append_response_json():
    data = {
        'tweets': [],
        'others_tweets': [],
        'includes': []
    }
    # All values present, no includes
    resonse_json = {
        'data': [
            {'test': 't'}, {'test2': 't2'}
        ],
        'tweets': [
            {'t': 't'}
        ]
    }
    result = api_handler.append_response_json(data, resonse_json)
    assert len(result['tweets']) == 2
    assert len(result['others_tweets']) == 1
    assert len(result['includes']) == 0
    # All values present, no tweets
    resonse_json = {
        'data': [
            {'test': 't'}
        ],
        'includes': [
            {'include1': 'i1'}
        ]
    }
    result = api_handler.append_response_json(data, resonse_json)
    assert len(result['tweets']) == 3
    assert len(result['others_tweets']) == 1
    assert len(result['includes']) == 1
    # Only tweets present
    resonse_json = {
        'data': [
            {'test': 't'}
        ]
    }
    result = api_handler.append_response_json(data, resonse_json)
    assert len(result['tweets']) == 4
    assert len(result['others_tweets']) == 1
    assert len(result['includes']) == 1
    # All values present
    resonse_json = {
        'data': [
            {'test': 't'}
        ],
        'tweets': [
            {'t': 't'}
        ],
        'includes': [
            {'include1': 'i1'}
        ]
    }
    result = api_handler.append_response_json(data, resonse_json)
    assert len(result['tweets']) == 5
    assert len(result['others_tweets']) == 2
    assert len(result['includes']) == 2

