import argparse


def get_parser() -> argparse.ArgumentParser:
    """
    Creates the argument parser and adds all command line arguments used by TwOSINT
    :return: ArgumentParser
    """
    # Initialize ArgumentParser
    parser = argparse.ArgumentParser()
    # Add command line arguments
    parser.add_argument('target', type=str, help='Twitter @handle of the target')
    parser.add_argument('-t', '--token', type=str, help='Twitter API bearer token')
    parser.add_argument('-f', '--format', type=str, default='csv', choices=['csv', 'json', 'pdf'], metavar="[csv, json, pdf]", help='Output format of the report. defaults to csv')
    parser.add_argument('-o', '--output', type=str, default='report', help='Output file name, file extension doesn\'t need to be provided. Defaults to report')
    parser.add_argument('-n', type=int, default=100, metavar="[5-999]", choices=range(5, 3200), help='Number (5-3200) of tweets to fetch. Defaults to 100')
    parser.add_argument('--no-retweets', default=True, help='Exclude retweets', dest='retweets', action='store_false')
    parser.add_argument('--no-replies', default=True,  help='Exclude replies', dest='replies', action='store_false')
    parser.add_argument('--start-time', type=str, help='Obtain tweets posted after this time. Format is "YYYY-mm-ddThh:mm:ssZ"')
    parser.add_argument('--end-time', type=str, help='Obtain tweets posted before this time. Format is "YYYY-mm-ddThh:mm:ssZ"')
    parser.set_defaults(retweets=True)
    parser.set_defaults(retweets=True)

    return parser
