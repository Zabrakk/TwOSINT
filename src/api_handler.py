import json
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

    def get_profile(self, username: str, auth: Authentication):
        """
        Calls /2/users/by/username/{username} to obtain basic info about the given user.
        API call documentation:
            https://developer.twitter.com/en/docs/twitter-api/users/lookup/api-reference/get-users-by-username-username
        :param username: Targets Twitter @ username
        :param auth: Authentication object with token
        :return: JSON with profile info; None if failed
        """
        print('Fetching profile data for {}'.format(username))
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
            self.__logger.info('Request failed. Error code: {}. Message: {}'.format(response.status_code, response.text))
            return None
        # API call done
        self.__logger.info('Request completed, profile info obtained')
        return response.json()

