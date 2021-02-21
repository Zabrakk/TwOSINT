import os
import logging


class Authentication:
    """
    Handles obtaining the Twitter API bearer token and providing the authentication header for API calls
    """

    def __init__(self):
        self.__logger = logging.getLogger('Authentication')
        self.__logger.info('Initialized')
        self.bearer = None

    def get_token(self, args_token: str, filename: str = 'bearer_token.txt'):
        """
        Tries to find the bearer token from one of the possible ways to provide it
        :param args_token: Possible token from command line argument
        :param filename: Bearer token text file name/relative location
        :return: True if bearer token was found; False otherwise
        """
        if args_token:
            # From command line
            self.bearer = args_token
            self.__logger.info('Bearer token provided from command line')
        elif 'BEARER_TOKEN' in os.environ:
            # From environment variable
            self.bearer = os.environ['BEARER_TOKEN']
            self.__logger.info('Bearer token obtained from BEARER_TOKEN environment variable')
        if not self.bearer:
            self.bearer = self.from_file(filename)
        if not self.bearer:
            self.bearer = self.from_input()
        if not self.bearer:
            self.__logger.info('No bearer token was obtained')
            return False
        print('Bearer token selected')
        return True

    def from_file(self, filename: str):
        """
        Attempts to read the bearer token from bearer_token.txt
        :param filename: Bearer token text file name/relative location
        :return: Bearer token or None if not found
        """
        token = None
        try:
            auth_file = open(filename, 'r')
            token = auth_file.read().split('=')[1]
            auth_file.close()
            if len(token) < 1:
                self.__logger.info('bearer_token.txt not found in file')
                return None
            self.__logger.info('Bearer token read from bearer_token.txt')
        except FileNotFoundError:
            # Authentication file not found
            self.__logger.info('bearer_token.txt not found, creating it')
            self.create_auth_file(filename)
            return None
        except IndexError:
            # Incorrect file formatting
            self.__logger.info('Bearer token not found in bearer_token.txt')
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
            self.__logger.info('User did not input a bearer token')
            return None
        self.__logger.info('Bearer token obtained from user input')
        return token

    def create_auth_file(self, filename: str):
        """
        Creates bearer_token.txt if its missing
        :param filename: Bearer token text file name/relative location
        :return: Nothing
        """
        try:
            open(filename, 'w').write('bearer_token=')
        except Exception as e:
            self.__logger.info('Failed to create bearer_token. Error was {}'.format(e))
            return
        self.__logger.info('bearer_token.txt created')

    def get_header(self):
        """
        Provides the Authentication header for API calls
        :return: Header or None if no bearer token was provided
        """
        if not self.bearer:
            self.__logger.info('Can\'t return authentication header. Bearer token not available')
            return None
        self.__logger.info('Returning authentication header')
        return {'Authorization': 'Bearer {}'.format(self.bearer)}
