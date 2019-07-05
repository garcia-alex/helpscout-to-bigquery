import datetime as dt
from datetime import datetime

from util.helpscoutAPI import HelpScout
from const.fields import RECORD, \
                         FIELD, \
                         THREADS_MAPPING, \
                         CONVERSATIONS_MAPPING, \
                         RATINGS_MAPPING, \
                         CUSTOMERS_MAPPING, \
                         MAILBOXES_MAPPING, \
                         FOLDERS_MAPPING, \
                         USERS_MAPPING

import pandas as pd

# Global urls and url handles
URL_MAIN = 'https://api.helpscout.net/v2/'

STATUS_ALL = '?status=all'


class HelpScoutMethods:
    def __init__(self, start='', end=''):
        """
        The HelpScout API endpoints class of methods
        :param start: the start date from which the HelpScout API will be queried.
        :param end: the end date from which the HelpScout API will be queried.
        """

        self.helpscout_obj = HelpScout()

        self.start = start
        self.end = end

        if self.start != '' and self.end != '':
            self.query = '&query=(createdAt: [{}T00:00:00Z TO {}T00:00:00Z])'.format(
                self.start.strftime('%Y-%m-%d'),
                self.end.strftime('%Y-%m-%d')
            )

            self.start_daterange = pd.date_range(start=self.start.strftime("%Y-%m-%d"),
                                                 end=(self.end - dt.timedelta(1)).strftime("%Y-%m-%d"),
                                                 freq='D')

        self.url_mailboxes = URL_MAIN + 'mailboxes'

    @staticmethod
    def generate_json(l, mapping):
        """
        Generate a json structure of data
        :param l: input list which has been retrieved from HelpScout API
        :param mapping: input dictionary determining the fields and whether they are records or pure fields
        :return: the resulting dictionary
        """
        results = dict()
        for j in range(len(l)):
            for item in list(mapping.keys()):
                if mapping[item] == RECORD:
                    if item in l[j].keys():
                        if l[j][item] == []:
                            pass  # BigQuery does not accept empty records
                        else:
                            if type(l[j][item]) != list:
                                results[item] = [l[j][item]]
                            else:
                                results[item] = l[j][item]
                    else:
                        pass  # results[item] = []
                elif mapping[item] == FIELD:
                    if item in l[j].keys():
                        results[item] = l[j][item]
                    else:
                        results[item] = ""

        return results

    @staticmethod
    def without_keys(d, keys):
        """
        Create a dictionary from a list excluding specific keys
        :param d: dictionary
        :param keys: keys to exclude from dictionary
        :return: trimmed dictionary
        """
        return {x: d[x] for x in d if x not in keys}

    def conversations(self):
        """
        The method for getting and posting data from the 'conversations' HelpScout endpoint
        :return: list of dictionaries with the conversations data
        """

        url_conversations = URL_MAIN + 'conversations' + STATUS_ALL + self.query

        data = self.helpscout_obj.get_helpscout_data(url=url_conversations)

        # List of all pages for query in date range:
        pages = list()
        for i in range(data['page']['totalPages']):
            pages.append('&page=' + str(i + 1))

        # Create a list of dictionaries of conversations:
        d = list()
        for i in range(data['page']['totalPages']):
            conv = self.helpscout_obj.get_helpscout_data(url=url_conversations + pages[i])['_embedded']['conversations']
            results = self.generate_json(conv, CONVERSATIONS_MAPPING)
            d.append(results)

        return d

    def customers(self):
        """
        The method for getting and posting data from the 'customers' HelpScout endpoint
        :return: list of dictionaries with the customers data
        """

        url_customers = URL_MAIN + 'customers'
        data = self.helpscout_obj.get_helpscout_data(url=url_customers)

        d = list()

        for i in range(data['page']['totalPages']):
            customer_list = self.helpscout_obj.get_pages_breakdown(url=url_customers, page=i + 1)

            if '_embedded' in customer_list.keys():
                customer_list = customer_list['_embedded']['customers']

                exclude = {"_embedded", "_links"}
                for item in customer_list:
                    dict_1 = self.without_keys(item, exclude)
                    dict_2 = item['_embedded']
                    dict_1.update(dict_2)

                    results = self.generate_json([dict_1], CUSTOMERS_MAPPING)

                    d.append(results)

        return d

    def folders(self):
        """
        The method for getting and posting data from the 'folders' HelpScout endpoint
        :return: list of dictionaries with the folders data
        """

        data = self.helpscout_obj.get_helpscout_data(url=self.url_mailboxes)

        d1 = list()

        for i in range(data['page']['totalPages']):
            d1.append(self.helpscout_obj.get_pages_breakdown(
                url=self.url_mailboxes,
                page=i + 1
            )['_embedded']['mailboxes'])

        mailboxes = d1[0]

        ids_list = list()
        for mailbox in mailboxes:
            ids_list.append(mailbox['id'])

        d = list()

        for _id in ids_list:
            data = self.helpscout_obj.get_helpscout_data(url=self.url_mailboxes + "/" + str(_id) + "/" + 'folders')
            for item in data['_embedded']['folders']:
                item['mailboxId'] = _id
                results = self.generate_json([item], FOLDERS_MAPPING)
                d.append(results)

        return d

    def mailboxes(self):
        """
        The method for getting and posting data from the 'mailboxes' HelpScout endpoint
        :return: list of dictionaries with the mailboxes data
        """

        data = self.helpscout_obj.get_helpscout_data(url=self.url_mailboxes)

        d = list()
        for i in range(data['page']['totalPages']):
            mailbox_list = self.helpscout_obj.get_pages_breakdown(
                url=self.url_mailboxes,
                page=i + 1
            )['_embedded']['mailboxes']

            exclude = {"_embedded", "_links"}
            for item in mailbox_list:
                __dict = self.without_keys(item, exclude)
                results = self.generate_json([__dict], MAILBOXES_MAPPING)
                d.append(results)

        return d

    def ratings(self):
        """
        The method for getting and posting data from the 'ratings' HelpScout endpoint
        :return: list of dictionaries with the ratings data
        """

        delta = self.end - self.start
        d = list()  # initialise the list
        date = self.start  # initialise the date

        # For days in the delta between start and end time:
        for i in range(delta.days):
            url_ratings = URL_MAIN + 'reports/happiness/ratings'

            # Get pages
            pages = self.helpscout_obj.get_helpscout_data(
                url=url_ratings,
                start=date.strftime("%Y-%m-%d"),
                end=(date + dt.timedelta(1)).strftime("%Y-%m-%d")
            )['pages']

            # Get results
            for j in range(pages):
                rating = self.helpscout_obj.get_pages_breakdown(
                    url=url_ratings,
                    page=j + 1,
                    start=date.strftime("%Y-%m-%d"),
                    end=(date + dt.timedelta(1)).strftime("%Y-%m-%d"),
                )['results']

                results = self.generate_json(rating, RATINGS_MAPPING)
                d.append(results)

            date += dt.timedelta(1)

        return d

    def threads(self):
        """
        The method for getting and posting data from the 'threads' HelpScout endpoint
        :return: list of dictionaries with the threads data
        """

        # Loop date range for full upload:
        _date_range = pd.date_range(start=self.start,
                                    end=self.end - dt.timedelta(1),  # self.start + dt.timedelta(6),
                                    freq='D')

        d = list()

        # For a range of days:
        for day_idx, day_val in enumerate(_date_range):

            # This query looks at the conversation create date (not necessarily the thread create date)
            query_day = '&query=(createdAt: [{}T00:00:00Z TO {}T00:00:00Z])'.format(
                _date_range[day_idx].date().strftime('%Y-%m-%d'),
                (_date_range[day_idx] + dt.timedelta(1)).date().strftime('%Y-%m-%d')
            )

            # Connect to API and extract conversations
            conversations = self.helpscout_obj.get_helpscout_data(
                url=URL_MAIN + 'conversations' + STATUS_ALL + query_day
            )

            if '_embedded' in list(conversations.keys()):  # Ensure that '_embedded' is actually in the keys
                # Extract the conversation id
                conversation_ids = list()
                for i, val in enumerate(conversations['_embedded']['conversations']):
                    conversation_ids.append(conversations['_embedded']['conversations'][i]['id'])

                for _idx, conv_id in enumerate(conversation_ids):
                    conv_threads = self.helpscout_obj.get_helpscout_data(
                        url=URL_MAIN + 'conversations' + '/{}/threads'.format(conv_id)
                    )['_embedded']['threads']

                    results = self.generate_json(conv_threads, THREADS_MAPPING)
                    d.append(results)

        return d

    def users(self):
        """
        The method for getting and posting data from the 'users' HelpScout endpoint
        :return: list of dictionaries with the users data
        """

        data = self.helpscout_obj.get_helpscout_data(url=URL_MAIN + 'users')

        d = list()
        for i in range(data['page']['totalPages']):
            user_list = self.helpscout_obj.get_pages_breakdown(
                url=URL_MAIN + 'users',
                page=i + 1
            )['_embedded']['users']

            exclude = {"_links"}
            for item in user_list:
                __dict = self.without_keys(item, exclude)
                results = self.generate_json([__dict], USERS_MAPPING)
                d.append(results)

        return d
