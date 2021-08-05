import sys
import logging
import argparse
# TwOSINT files
from src.argument_parser import get_parser
from src.authentication import Authentication
from src.api_handler import APIHandler
from src.save import Save
"""
This is the entry point to TwOSINT
"""

if __name__ == '__main__':
    # Initialize logging
    logging.basicConfig(format='%(asctime)s %(name)s: %(message)s', level=logging.INFO,
                        datefmt='%H:%M:%S', filename='logs/log.txt', filemode='w')
    parser = get_parser()
    args = parser.parse_args()
    # Get bearer token
    auth = Authentication()
    # Check that a bearer token is available
    auth.get_token(args.token)

    if not auth.token_found():
        print('A Bearer Token is required!')
    else:
        api_handler = APIHandler()
        # Check that possible user provided start and end times are correct
        if args.start_time and not api_handler.check_time_format(args.start_time):
            print('Incorrect start_time format!')
            sys.exit(1)
        if args.end_time and not api_handler.check_time_format(args.end_time):
            print('Incorrect end_time format!')
            sys.exit(1)

        # Load profile data
        profile = api_handler.get_profile(args.target, auth)
        if not profile:
            # Exit if fetching the profile failed
            sys.exit(1)
        # Get profile ID
        profile_id = profile['id']
        # Load tweets
        tweets = api_handler.get_tweets(profile_id, auth, max_tweets=args.n, retweets=args.retweets,
                                        replies=args.replies, start_time=args.start_time, end_time=args.end_time)
        if not tweets:
            sys.exit(1)
        save = Save()
        if args.format == 'csv':
            save.to_csv(profile, tweets, args.output)
        #if data:
        #    open('report.json', 'w').write(json.dumps(data, indent=4))
        #data = APIHandler().get_tweets('1121526942', auth, 100)
        #if data:
        #    open('tweets.json', 'w').write(json.dumps(data, indent=4))
