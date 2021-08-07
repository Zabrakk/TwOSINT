import os
import logging


class Authentication:
    """
    Handles obtaining the Twitter API bearer token and providing the authentication header for API calls
    """

    def __init__(self, save_token: bool):
        """
        Logging for Authentication
        :param save_token: Should token be saved to bearer_token.txt?
        """
        self.__logger = logging.getLogger('Authentication')
        self.__logger.info('Initialized')
        self.token = None
        self.save_token = save_token

    def get_token(self, args_token: str, filename: str = 'bearer_token.txt') -> bool:
        """
        Tries to find the bearer token from one of the possible ways.
        :param args_token: Possible token from command line argument
        :param filename: Bearer token text file name/relative location
        :return: True if bearer token was found; False otherwise
        """
        if args_token:
            # From command line
            self.token = args_token
            self.__logger.info('Bearer token provided from command line')
        elif 'BEARER_TOKEN' in os.environ:
            # From environment variable
            self.token = os.environ['BEARER_TOKEN']
            self.__logger.info('Bearer token obtained from BEARER_TOKEN environment variable')
        if not self.token:
            # From .txt file
            self.token = self.from_file(filename)
            if self.token:
                self.save_token = False
        if not self.token:
            # From user input prompt
            self.token = self.from_input()
        if not self.token:
            self.__logger.info('No bearer token was obtained')
            return False
        # Save token in file for convenience
        self.store_token_to_file(filename, self.token)
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
            return None
        except IndexError:
            # Incorrect file formatting
            self.__logger.info('Bearer token not found in bearer_token.txt')
            return None
        return token

    def from_input(self) -> str or None:
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

    def store_token_to_file(self, filename: str, token: str) -> None:
        """
        Stores the bearer token to a text file. Also creates the token storage file.
        :param filename: Name of the bearer token storage file
        :param token: Bearer token
        :return: None
        """
        if not self.save_token:
            return
        try:
            f = open(filename, 'w')
            f.write('bearer_token={}'.format(token))
            f.close()
        except Exception as e:
            self.__logger.info('Failed to store bearer token. Error was {}'.format(e))
            return
        self.__logger.info('Bearer token saved to {}'.format(filename))

    def token_found(self) -> bool:
        """
        Tells whether or not the bearer token was found
        :return: True if token was obtained; False otherwise
        """
        return self.token is not None

    def get_header(self) -> dict or None:
        """
        Provides the Authentication header for API calls
        :return: Header or None if no bearer token was provided
        """
        if not self.token:
            self.__logger.info("Can't return authentication header. Bearer token not available")
            return None
        self.__logger.info('Returning authentication header')
        return {'Authorization': 'Bearer {}'.format(self.token)}
