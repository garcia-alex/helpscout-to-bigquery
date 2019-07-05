import requests
from util.config import Config
import time

URL_AUTH = 'https://api.helpscout.net/v2/oauth2/token'


class HelpScout:
    def __init__(self):
        """
        The connection with the HelpScout API.
        """

        # get the helpscout config parameters
        self.config = Config('helpscout')

        self.data = {
        'grant_type': self.config.get('grant_type'),
        'client_id': self.config.get('client_id'),
        'client_secret': self.config.get('client_secret')
        }

        self.token = requests.post(URL_AUTH, data=self.data)

        self.headers = {'Authorization': 'Bearer {}'.format(self.token.json()['access_token'])}

    def get_helpscout_data(self, url,  start='', end=''):
        """
        Get the data for a given HelpScout API url
        :param url: the url to query
        :param start: start date in question
        :param end: end date in question
        :return: the helpscout data in json format
        """

        params = {
            'start': '{}T00:00:00Z'.format(start),
            'end': '{}T00:00:00Z'.format(end)
        }

        helpscout_data = requests.get(url, headers=self.headers, params=params)
        time.sleep(1)
        return helpscout_data.json()

    def get_pages_breakdown(self, url, page, start='', end=''):
        """
        Get the data for a given HelpScout API url if there are multiple pages
        :param url: the url to query
        :param page: the page in the multiple pages of results
        :param start: start date in question
        :param end: end date in question
        :return: the helpscout data in json format
        """

        params = {
                'start': '{}T00:00:00Z'.format(start),
                'end': '{}T00:00:00Z'.format(end),
                'page': '{}'.format(page)
        }

        pages_breakdown = requests.get(url, headers=self.headers, params=params)
        time.sleep(1)
        return pages_breakdown.json()