import os
import logging


class Authentication:
    """
    Handles obtaining the Twitter API bearer token and providing the authentication header for API calls
    """

    def __init__(self):
        self.logger = logging.getLogger('Authentication')
        self.logger.info('Initialized')
        self.bearer = None

    def get_token(self, args_token):
        """
        Tries to find the bearer token from one of the possible ways to provide it
        :param args_token: Possible token from command line argument
        :return: True if bearer token was found; False otherwise
        """
        if args_token:
            # From command line
            self.bearer = args_token
            self.logger.info('Bearer token provided from command line')
        elif 'BEARER_TOKEN' in os.environ:
            # From environment variable
            self.bearer = os.environ['BEARER_TOKEN']
            self.logger.info('Bearer token obtained from BEARER_TOKEN environment variable')
        if not self.bearer:
            self.bearer = self.from_file()
        if not self.bearer:
            self.bearer = self.from_input()
        if not self.bearer:
            self.logger.info('No bearer token was obtained')
            return False
        print('Bearer token selected')
        return True

    def from_file(self):
        """
        Attempts to read the bearer token from bearer_token.txt
        :return: Bearer token or None if not found
        """
        token = None
        try:
            auth_file = open('bearer_token.txt', 'r')
            token = auth_file.read().split('=')[1]
            auth_file.close()
            if len(token) < 1:
                self.logger.info('bearer_token.txt not found in file')
                return None
            self.logger.info('Bearer token read from bearer_token.txt')
        except FileNotFoundError:
            # Authentication file not found
            self.logger.info('bearer_token.txt not found, creating it')
            self.create_auth_file()
            return None
        except IndexError:
            # Incorrect file formatting
            self.logger.info('Bearer token not found in bearer_token.txt')
            return None
        return token

    def from_input(self):
        """
        Prompts user to input their bearer token
        :return: Token or none if not provided
        """
        token = None
        token = input('Enter your Bearer Token: ')
        if not token:
            self.logger.info('User did not input a bearer token')
            return None
        self.logger.info('Bearer token obtained from user input')
        return token

    def create_auth_file(self):
        """
        Creates bearer_token.txt if its missing
        :return: Nothing
        """
        try:
            open('bearer_token.txt', 'w').write('bearer_token=')
        except Exception as e:
            self.logger.info('Failed to create bearer_token. Error was {}'.format(e))
            return
        self.logger.info('bearer_token.txt created')

    def get_header(self):
        """
        Provides the Authentication header for API calls
        :return: Header or None if no bearer token was provided
        """
        if not self.bearer:
            self.logger.info('Can\'t return authentication header. Bearer token not available')
            return None
        self.logger.info('Returning authentication header')
        return {'Authorization': 'Bearer {}'.format(self.bearer)}
