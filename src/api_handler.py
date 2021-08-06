import re
import time
import shutil
import logging
import requests
# TwOSINT files
from src.authentication import Authentication

# TODO: Handling for different failures


class APIHandler:
    """
    Performs the Twitter API calls
    """

    def __init__(self):
        self.__logger = logging.getLogger('API_Handler')
        self.base_url = 'https://api.twitter.com/2/'

    def get_profile(self, username: str, auth: Authentication) -> dict or None:
        """
        Calls /2/users/by/username/{username} to obtain basic info about the given user.
        API call documentation:
            https://developer.twitter.com/en/docs/twitter-api/users/lookup/api-reference/get-users-by-username-username
        :param username: Targets Twitter @ username (handle)
        :param auth: Authentication object with token
        :return: JSON with profile info or None if failed
        """
        print('Fetching profile data for {}...'.format(username))
        self.__logger.info('Fetching profile data for {}'.format(username))
        # Obtain the request URL
        url = self.create_get_profile_url(username)
        self.__logger.info('Calling {}'.format(url))
        # Send the GET request
        response = requests.get(url, headers=auth.get_header())
        # Handle possible error codes
        if response.status_code != 200:
            print('Failed to load profile! Check logs for more info')
            self.__logger.info('Request failed. Error code: {}. Message: {}'.format(response.status_code, response.text))
            return None
        # Extract the JSON response
        data = response.json()
        # Check JSON for errors
        if self.check_raised_error(data):
            return None
        # API call done
        data = response.json()['data']
        data['followers'] = data['public_metrics']['followers_count']
        data['following'] = data['public_metrics']['following_count']
        data.pop('public_metrics', None)

        # Download target's profile image
        self._save_profile_image(username, data['profile_image_url'])

        print('Done loading profile data')
        self.__logger.info('Request completed, profile info obtained')
        return data

    def get_tweets(self, user_id: str, auth: Authentication, max_tweets: int = 5, retweets: bool = True,
                   replies: bool = True, start_time: str = None, end_time: str = None):
        """
        Calls /2/users/{id}/tweets to obtain tweets from the specified user. Can get max 3200, and minimum 5 tweets.
        API call documentation:
            https://developer.twitter.com/en/docs/twitter-api/tweets/timelines/api-reference/get-users-id-tweets
        SETTING EXCLUDE REPLIES MAKE ONLY 800 NEWEST TWEETS AVAILABLE
        :param user_id: Target user's ID
        :param auth: Authentication object
        :param max_tweets: Maximum number of tweets to obtain. Minimum 5, maximum 3200
        :param retweets: Include retweets (True or False)
        :param replies: Include replies (True or False). Setting this to true limits number of tweets to 800
        :param start_time: Obtain tweets posted after this time. Format is "YYYY-mm-ddThh:mm:ssZ"
        :param end_time: Obtain tweets posted before this time. Format is "YYYY-mm-ddThh:mm:ssZ"
        :return: JSON object with tweets or None if call failed
        """
        max_tweets, num_to_get = self.decide_num_to_get(max_tweets, replies)
        print('Fetching tweets...')
        self.__logger.info('Fetching up to {} tweets for {}'.format(max_tweets, user_id))
        # Create request URL
        url = self.create_get_tweets_url(user_id, num_to_get, retweets, replies, start_time, end_time)
        if url is None:
            return None
        # Response data is stored here
        data = {
            'tweets': [],
            'others_tweets': [],
            'includes': []
        }
        response = None
        first_iteration = True
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
            # Check if tweets were found during the first iteration
            if first_iteration and response_json['meta']['result_count'] == 0:
                print('No tweets found for the target')
                return {'empty': True}
            first_iteration = False
            data = self.append_response_json(data, response_json)
            print(f'Tweets obtained: {len(data["tweets"])}')
            # Check if we should stop
            if 'next_token' not in response_json['meta'].keys():
                break
            # Sleep for a little while
            time.sleep(0.5)
            # Add pagination token to url
            url = self.update_pagination_token(url, response_json['meta']['next_token'])
            # Check if number of tweets to get should be changed
            if max_tweets - len(data['tweets']) < num_to_get:
                url, num_to_get = self.update_url_results_num(url, num_to_get, max_tweets-len(data['tweets']))

        print('Done loading tweets')
        return data['tweets']

    def append_response_json(self, data: list, response_json: list):
        """
        Concatenates the response from Twitter to existing data
        :param data: Local response data
        :param response_json: Response from Twitter
        :return: Local data combined with the Twitter response
        """
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
        return data

    def create_get_profile_url(self, username: str) -> str:
        """
        Creates the URL used for obtaining a Twitter user's profile
        :param username: Target user
        :return: The API call
        """
        url = self.base_url + 'users/by/username/' + username
        url += '?user.fields=id,name,description,created_at,location,url,profile_image_url,public_metrics,verified'
        return url

    def create_get_tweets_url(self, user_id: str, num_to_get: int, retweets: bool = True, replies: bool = True, start_time: str = None, end_time: str = None) -> str:
        """
        Generates the API call URL used to obtain tweets
        :param user_id: Target user's ID
        :param num_to_get: Number of tweets to obtain per call
        :param retweets: Include retweets (True or False)
        :param replies: Include replies (True or False
        :param start_time: Obtain tweets posted after this time. Format is "YYYY-mm-ddThh:mm:ssZ"
        :param end_time: Obtain tweets posted before this time. Format is "YYYY-mm-ddThh:mm:ssZ"
        :return: URL for get tweets API call
        """
        url = self.base_url + 'users/{}/tweets?max_results={}&'.format(user_id, num_to_get)
        # Add expansions
        url += 'expansions=author_id,in_reply_to_user_id,referenced_tweets.id,referenced_tweets.id.author_id,attachments.media_keys&'
        # Tweet fields
        url += 'tweet.fields=author_id,text,attachments,created_at,entities,geo,in_reply_to_user_id,lang,public_metrics,referenced_tweets&'
        # Media fields
        url += 'media.fields=url,preview_image_url,media_key&'
        if not retweets and not replies:
            url += 'exclude=retweets,replies&'
        elif not retweets:
            url += 'exclude=retweets&'
        elif not replies:
            url += 'exclude=replies&'
        if start_time:
            if self.check_time_format(start_time):
                url += 'start_time={}&'.format(start_time)
            else:
                print('Invalid start_time format! Use YYYY-mm-ddThh:mm:ssZ')
                return None
        if end_time:
            if self.check_time_format(end_time):
                url += 'end_time={}&'.format(end_time)
            else:
                print('Invalid end_time format! Use YYYY-mm-ddThh:mm:ssZ')
                return None
        # Remove trailing '&'
        return url[:-1]

    def update_url_results_num(self, url: str, old_num_to_get: int, new_num_to_get: int):
        """
        Updates the number of tweets obtained per API call
        :param url: API call URL
        :param old_num_to_get: Old number of tweets
        :param new_num_to_get: New number of tweets
        :return: URL with max_results set to new number of tweets
        """
        url = url.split('max_results={}'.format(old_num_to_get))
        if new_num_to_get < 5:
            new_num_to_get = 5
        url = url[0] + 'max_results={}'.format(new_num_to_get) + url[1]
        return url, new_num_to_get

    def update_pagination_token(self, url: str, pagination_token: str):
        """
        Updates the pagination token in the API call url
        :param url: API call URL
        :param pagination_token: New pagination token
        :return: URL with new token
        """
        if 'pagination_token' not in url:
            url += '&pagination_token={}'.format(pagination_token)
        else:
            # Remove old pagination token
            url = url[:url.rfind('&')]
            # Add new one
            url += '&pagination_token={}'.format(pagination_token)
        return url

    def decide_num_to_get(self, max_tweets: int, include_replies: bool = True):
        """
        Decides how many tweets get_tweets() should obtain in total and how many per one request
        :param max_tweets: Number of tweets user wants to get
        :param include_replies: Are replies included (True or False). max_tweets limited to 800 if set to False
        :return: max_tweets <= 3200 & num_to_get <= 100. Alternatively, returns None,None if max_tweets is not an integer
        """
        try:
            max_tweets = int(max_tweets)
        except ValueError:
            return None, None
        if not include_replies and max_tweets > 800:
            print('Replies excluded, can\'t request more than 800 tweets ==> Defaulting to 800')
            max_tweets = 800
        if max_tweets < 5:
            print('Can\'t request less than 5 tweets ==> Defaulting to 5')
            return 5, 5
        elif max_tweets <= 100:
            return max_tweets, max_tweets
        elif max_tweets > 3200:
            print('Can\'t request more than 3200 tweets ==> Defaulting to 3200')
            return 3200, 100
        return max_tweets, 100

    def check_raised_error(self, j: dict) -> bool:
        """
        Checks whether or not an error occurred based on the response json
        :param j: Response JSON
        :return: True if error occurred; False otherwise
        """
        if 'errors' in j.keys():
            for entry in j['errors']:
                print('The following error occurred: {}'.format(entry['detail']))
                self.__logger.info('Twitter responded with the following error:\n\tTitle: {}, Message: {}'.format(entry['title'], entry['detail']))
            return True
        return False

    def check_time_format(self, time_str: str):
        """
        Ensures that the "YYYY-mm-ddThh:mm:ssT" format is used for timestamps
        :param time_str: Datetime as string
        :return: True if correct; False otherwise
        """
        if re.search(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", time_str):
            return True
        return False

    def _save_profile_image(self, username: str, url: str) -> None:
        """
        Downloads target's Twitter profile image, so it can be added to the PDF
        :param username: Twitter handle of target
        :param url: URL of profile image
        :return: Nothing
        """
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open('reports/{}.jpg'.format(username), 'wb') as f:
                self.__logger.info("Downloaded target's profile image")
                shutil.copyfileobj(r.raw, f)
        else:
            self.__logger.info("Could not download target's profile image")