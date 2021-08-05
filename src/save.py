import re
import csv
import json


class Save:
    """
    Performs the different save operations for fetched twitter data
    """

    def _add_file_extension(self, filename: str, extension: str) -> str:
        """
        Adds the file extension to the report file's name if it is missing
        :param filename: Name of file
        :param extension: File extension to use
        :return: Filename with file extension
        """
        if not filename.endswith('.{}'.format(extension)):
            return filename + '.' + extension
        return filename

    def to_csv(self, profile: dict, tweets: dict, filename: str) -> None:
        """
        Saves the fetched Twitter profile and its tweets to a csv file.
        Note: This will overwrite files!
        :param profile: Profile fetched with api_handler.get_profile()
        :param tweets: Tweets fetched with api_handler.get_tweets()
        :param filename: File to save to
        :return: None
        """
        filename = self._add_file_extension(filename, 'csv')
        # Open / create the report file
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            # Create the csv writer
            w = csv.writer(f)
            w.writerows(
                [
                    ['Handle:', profile['username']],
                    ['Name:', profile['name']],
                    ['ID:', str(profile['id'])],
                    ['Description:', profile['description']],
                    ['Profile img:', profile['profile_image_url']],
                    ['Verified:', profile['verified']],
                    ['Followers:', profile['public_metrics']['followers_count']],
                    ['Following:', profile['public_metrics']['following_count']]
                ]
            )
            # Add empty row
            w.writerow([''])
            # Tweet column names
            w.writerow([''])





