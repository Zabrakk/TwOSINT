import os
import re
import csv
import json
from fpdf import FPDF

from src.constants import profile_field_names


class Save:
    """
    Performs the different save operations for fetched twitter data
    """
    def __init__(self):
        """
        Creates the reports/ directory if it's missing
        """
        if not os.path.exists('reports'):
            os.mkdir('reports')

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
        Saves the fetched Twitter profile and its tweets to TWO different CSV file.
        Note: This will overwrite files!
        :param profile: Profile fetched with api_handler.get_profile()
        :param tweets: Tweets fetched with api_handler.get_tweets()
        :param filename: File to save to
        :return: None
        """
        filename = self._add_file_extension(filename, 'csv')
        profile_file = filename[:-4]+'_profile'+filename[-4:]
        tweet_file = filename[:-4]+'_tweets'+filename[-4:]
        if tweets == {'empty': True}:
            print('Saving profile=>{}'.format(profile_file))
        else:
            print('Saving profile=>{} and tweets=>{}'.format(profile_file, tweet_file))
        # Save profile info
        with open('reports/'+profile_file, 'w', newline='', encoding='utf-8') as f:
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
                    ['Followers:', profile['followers']],
                    ['Following:', profile['following']]
                ]
            )
        # Save tweets
        if tweets != {'empty': True}:
            with open('reports/'+tweet_file, 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                columns = ['Tweeted at', 'Text', 'Retweets', 'Replies', 'Coordinates']
                w.writerow(columns)
                for tweet in tweets:
                    w.writerow([tweet['created_at'], tweet['text'].replace('\n', ' ').replace(',', '').replace(';', ':'),
                                tweet['public_metrics']['retweet_count'], tweet['public_metrics']['reply_count'],
                                tweet['geo']['coordinates']['coordinates'] if 'geo' in tweet.keys() and 'coordinates' in tweet['geo'].keys() else None])

        print('Done saving!')

    def to_json(self, profile: dict, tweets: dict, filename: str) -> None:
        """
        Saves the fetched Twitter profile and its tweets to a JSON file.
        Note: This will overwrite files!
        :param profile: Profile fetched with api_handler.get_profile()
        :param tweets: Tweets fetched with api_handler.get_tweets()
        :param filename: File to save to
        :return: None
        """
        filename = self._add_file_extension(filename, 'json')
        result = profile
        result['tweets'] = tweets
        print('Saving profile and tweets =>{}'.format(filename))
        with open('reports/'+filename, 'w', encoding='utf-8') as f:
            f.write(json.dumps(result, indent=4))
        print('Done saving!')

    def _remove_non_ascii(self, text: str) -> str:
        """
        Removes non ascii characters from text. Also removes line changes
        :param text: Text to parse
        :return: Input with non-ascii removed
        """
        if len(text) > 0:
            # This is not a very good solution, as some characters that should not be deleted have to be added here
            text = re.sub(r'[^\x00-\x7Fäöå]+', ' ', text)
        return text.replace('\n', ' ')

    def to_pdf(self, profile: dict, tweets: dict, filename: str) -> None:
        """
        Saves the fetched Twitter profile and its tweets to a PDF file.
        Note: This will overwrite files!
        :param profile: Profile fetched with api_handler.get_profile()
        :param tweets: Tweets fetched with api_handler.get_tweets()
        :param filename: File to save to
        :return: None
        """
        filename = self._add_file_extension(filename, 'pdf')
        print('Saving profile and tweets =>{}'.format(filename))
        pdf = FPDF()
        pdf.add_page()
        # Title
        pdf.set_font('Arial', 'B', 22)
        pdf.cell(0, 10, 'TwOSINT report for {}'.format(profile['username']), border='B')
        # Profile info
        pdf.set_font('Arial', '', 12)
        y = 25
        pdf.set_y(y)
        for key in profile_field_names.keys():
            if key in profile.keys() and key != 'profile_image_url' and key != 'username':
                # Have to remove non ascii characters :/
                text = self._remove_non_ascii(str(profile[key]))
                x = 15
                pdf.set_x(x)
                pdf.cell(len(profile_field_names[key])*2, 5, profile_field_names[key], border='B')
                x += 30
                pdf.set_x(x)
                pdf.multi_cell(0, 5, ' ' + text, align='L')
                if len(text) > 70:
                    y += 10
                else:
                    y += 7
                pdf.set_y(y)
            elif key == 'profile_image_url':
                #pdf.image('reports/{}.jpg'.format(profile['username']), type='jpg')
                pdf.image('reports/{}.jpg'.format(profile['username']), x=150, y=25, type='jpg')
        # Tweets
        pdf.set_font('Arial', 'B', 17)
        pdf.cell(30, 10, 'Tweets:', border='B')
        y += 15
        pdf.set_y(y)
        for tweet in tweets:
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 5, 'Author ID: {} | Tweeted at: {}'.format(tweet['author_id'], tweet['created_at']))
            y += 5
            pdf.set_y(y)
            if 'geo' in tweet.keys() and 'coordinates' in tweet['geo'].keys():
                pdf.cell(0, 5, 'Coordinates: {}'.format(tweet['geo']['coordinates']['coordinates']))
                y += 5
                pdf.set_y(y)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 5, self._remove_non_ascii(tweet['text']))
            pdf.cell(0, 1, '', border='B')
            y += 15
            if y > 240:
                pdf.add_page()
                y = 20
            pdf.set_y(y)

        # Save
        pdf.output('reports/'+filename, 'F')
        print('Done saving!')
