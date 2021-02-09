import logging
import argparse
# TwOSINT files
from src.authentication import Authentication


if __name__ == '__main__':
    # Initialize logging
    logging.basicConfig(format='%(asctime)s %(name)s: %(message)s', level=logging.INFO,
                        datefmt='%H:%M:%S', filename='logs/log.txt', filemode='w')
    # Initialize ArgumentParser
    parser = argparse.ArgumentParser()
    # Add command line arguments
    parser.add_argument('-t', '--token', type=str, help='Bearer token')
    # Get user provided arguments
    args = parser.parse_args()
    # Get bearer token
    auth = Authentication()
    # Check that a bearer token is available
    auth.get_token(args.token)
    if not auth.get_header():
        print('A Bearer Token is required!')
