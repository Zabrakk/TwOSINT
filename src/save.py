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
        Saves the fetched Twitter profile and its tweets to TWO different csv file.
        Note: This will overwrite files!
        :param profile: Profile fetched with api_handler.get_profile()
        :param tweets: Tweets fetched with api_handler.get_tweets()
        :param filename: File to save to
        :return: None
        """
        filename = self._add_file_extension(filename, 'csv')
        profile_file = filename[:-4]+'_profile'+filename[-4:]
        tweet_file = filename[:-4]+'_tweets'+filename[-4:]
        if tweets == {'emptry': True}: # TODO: FIX THIS THING
            print('Saving profile=>{}'.format(profile_file))
        else:
            print('Saving profile=>{} and tweets=>{}'.format(profile_file, tweet_file))
        # Save profile info
        with open(profile_file, 'w', newline='', encoding='utf-8') as f:
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
        # Save tweets
        if tweets != {'emptry': True}: # TODO: FIX THIS THING
            with open(tweet_file, 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                columns = ['Tweeted at', 'Text', 'Retweets', 'Replies', 'Coordinates']
                w.writerow(columns)
                for tweet in tweets:
                    w.writerow([tweet['created_at'], tweet['text'].replace('\n', ' ').replace(',', '').replace(';', ':'),
                                tweet['public_metrics']['retweet_count'], tweet['public_metrics']['reply_count'],
                                tweet['geo']['coordinates']['coordinates'] if 'geo' in tweet.keys() and 'coordinates' in tweet['geo'].keys() else None])

        print('Done saving!')



