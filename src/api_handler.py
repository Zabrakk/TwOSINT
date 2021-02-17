import json
import time
import logging
import requests
# TwOSINT files
from src.authentication import Authentication

# TODO: Handling for different failures
# TODO: Allow exclusion of retweets...
# TODO: Add separate URL creation functions

class APIHandler:
    """
    Performs the Twitter API calls
    """

    def __init__(self):
        self.__logger = logging.getLogger('API_Handler')
        self.base_url = 'https://api.twitter.com/2/'

    def get_profile(self, username: str, auth: Authentication):
        """
        Calls /2/users/by/username/{username} to obtain basic info about the given user.
        API call documentation:
            https://developer.twitter.com/en/docs/twitter-api/users/lookup/api-reference/get-users-by-username-username
        :param username: Targets Twitter @ username
        :param auth: Authentication object with token
        :return: JSON with profile info; None if failed
        """
        print('Fetching profile data for {}...'.format(username))
        self.__logger.info('Fetching profile data for {}'.format(username))
        # Create request URL
        url = self.base_url + 'users/by/username/' + username
        # Specify additional information to obtain
        url += '?user.fields=id,name,description,created_at,location,profile_image_url,public_metrics,verified'
        self.__logger.info('Calling {}'.format(url))
        # Send the GET request
        response = requests.get(url, headers=auth.get_header())
        # Handle possible error codes
        if response.status_code != 200:
            print('Failed to load profile! Check logs for more info')
            self.__logger.info('Request failed. Error code: {}. Message: {}'.format(response.status_code, response.text))
            return None
        # API call done
        self.__logger.info('Request completed, profile info obtained')
        return response.json()

    def get_tweets(self, user_id: str, auth: Authentication, max_tweets: int = 5):
        """
        Calls /2/users/{id}/tweets to obtain tweets from the specified user. Can get max 3200, and minimum 5 tweets.
        API call documentation:
            https://developer.twitter.com/en/docs/twitter-api/tweets/timelines/api-reference/get-users-id-tweets
        :param user_id: ID of the user
        :param auth: Authentication object with token
        :param max_tweets: How many tweets to fetch. Defaults to 20
        :return: JSON with tweets; None if failed
        """
        num_to_get = max_tweets
        if max_tweets < 5:
            print('Can\'t request less than 5 tweets ==> Defaulting to 5')
            self.__logger.info('User requested less than 5 tweets, defaulting to 5')
            max_tweets = 5
            num_to_get = 5
        elif max_tweets > 3200:
            print('Request exceeds the 3200 tweet limit ==> Defaulting to maximum 3200')
            self.__logger.info('User requested more than 3200 tweets, defaulting to 3200')
            max_tweets = 3200
        if max_tweets > 100:
            # Can only get a maximum of 100 tweets at once
            num_to_get = 100
        print('Fetching tweets...')
        self.__logger.info('Fetching up to {} tweets for {}'.format(max_tweets, user_id))
        # Create request URL
        url = self.base_url + 'users/{}/tweets?max_results={}&'.format(user_id, num_to_get) # num_to_get
        # Specify additional information to obtain
        # Expansions
        url += 'expansions=referenced_tweets.id,attachments.media_keys&'
        # Basic info
        url += 'tweet.fields=author_id,text,created_at,lang,public_metrics,in_reply_to_user_id,geo&'
        # Location
        url += 'place.fields=country,name,place_type,geo&'
        # Media
        url += 'media.fields=type,preview_image_url,url'

        # Response data is stored here
        data = {
            'tweets': [],
            'others_tweets': [],
            'includes': []
        }
        response = None
        while len(data['tweets']) < max_tweets:
            self.__logger.info('Calling {}'.format(url))
            # Send the GET request
            response = requests.get(url, headers=auth.get_header())
            # Handle possible error codes
            if response.status_code != 200:
                print('Failed to load tweets! Check logs for more info')
                self.__logger.info('Request failed. Error code: {}. Message: {}'.format(response.status_code, response.text))
                return None
            # API call done, parse data
            response_json = response.json()
            data['tweets'] += response_json['data']
            # These fields may not always exist
            try:
                data['others_tweets'] += response_json['tweets']
            except KeyError:
                pass
            try:
                data['includes'] += response_json['includes']
            except KeyError:
                pass
            print(f'Tweets obtained: {len(data["tweets"])}')
            # Check if we should stop
            if 'next_token' not in response_json['meta'].keys():
                break
            # Sleep for a little while
            time.sleep(0.5)
            # Add pagination token to url
            if 'pagination_token' not in url:
                url += '&pagination_token=' + response_json['meta']['next_token']
            else:
                url = url[:url.rfind('&')]
                url += '&pagination_token=' + response_json['meta']['next_token']
            # Check if number of tweets to get should be changed
            print()
            if max_tweets - len(data['tweets']) < num_to_get:
                url = url.split('max_results={}'.format(num_to_get))
                url = url[0] + 'max_results={}'.format(max_tweets-len(data['tweets'])) + url[1]

        print('Tweets loaded')
        return data
