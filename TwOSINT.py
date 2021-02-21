import json
import logging
import argparse
# TwOSINT files
from src.authentication import Authentication
from src.api_handler import APIHandler


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
    else:
        data = APIHandler().get_profile('twitter', auth)
        if data:
            open('report.json', 'w').write(json.dumps(data, indent=4))
        data = APIHandler().get_tweets('783214', auth, 100)
        if data:
            open('tweets.json', 'w').write(json.dumps(data, indent=4))
