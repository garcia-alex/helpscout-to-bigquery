import json
import os
import re

from util.bigqueryAPI import BigQuery
from util.helpscoutMethods import HelpScoutMethods

BGQ_DATASET = 'helpscout_prod'  # enter the name of your Google BigQuery Dataset

# re_upload is True for non-date-dependent fields.
# Where this is the case, the table is deleted and the full data is re-uploaded.
endpoints = {
    'conversations': {'on': True, 're_upload': False},
    'threads': {'on': True, 're_upload': False},
    'ratings': {'on': True, 're_upload': False},
    'customers': {'on': True, 're_upload': True},  # not date-dependent
    'mailboxes': {'on': True, 're_upload': True},  # not date-dependent
    'folders': {'on': True, 're_upload': True},  # not date-dependent
    'users': {'on': True, 're_upload': True}  # not date-dependent
}

# Global compile
all_cap_re = re.compile('([a-z0-9])([A-Z])')
first_cap_re = re.compile('(.)([A-Z][a-z]+)\":$')


class HelpScoutDataLoader:
    def __init__(self, start, end, endpoint):
        """
        The data loader class
        :param start: The start date in question
        :param end: The end date in question
        :param endpoint: the HelpScout API endpoint
        """

        self.start = start
        self.end = end
        self.endpoint = endpoint
        self.helpscoutmethod_obj = HelpScoutMethods(self.start, self.end)  # Initialise the helpscout methods
        self.bgq_obj = BigQuery(BGQ_DATASET, endpoint)  # BigQuery()  # initialize the BigQuery objs

    @staticmethod
    def convert_camel_case(name):
        """
        Convert camelCase to snake_case (purely a stylistic preference)
        :param name: string to be converted
        :return: converted string
        """
        s1 = first_cap_re.sub(r'\1_\2', name)
        return all_cap_re.sub(r'\1_\2', s1).lower().replace("-", "_")

    def get_data_for_upload(self):
        """
        Get the data from a given endpoint and write it to a json file.
        """

        if endpoints[self.endpoint]['on']:
            print("endpoint:", self.endpoint)

            d = eval('self.helpscoutmethod_obj.'+self.endpoint+'()')

            try:
                os.remove(self.endpoint+".json")
            except OSError:
                pass

            for item in d:
                converted = self.convert_camel_case(str(json.dumps(item)))

                with open(self.endpoint+'.json', 'a') as outfile:
                    json.dump(json.loads(converted), outfile)
                    outfile.write('\n')

    def write(self):
        """
        Write the data from a json file to BigQuery
        """

        if endpoints[self.endpoint]['on']:
            if endpoints[self.endpoint]['re_upload']:
                # NB: please ensure the table exists in the dataset (even if blank), or this will fail
                self.bgq_obj.delete_table()  # if re-upload is on, delete the table.

            with open(self.endpoint+'.json') as f:
                content = f.readlines()

            # Overwrite with sorted list "hack"
            # takes longest lines first therefore most likely to contain all sub-fields
            sorted_list = sorted(content, key=len, reverse=True)

            try:
                os.remove(self.endpoint+".json")
            except OSError:
                pass

            for i in range(len(sorted_list)):
                with open(self.endpoint+'.json', 'a') as outfile:
                    json.dump(json.loads(sorted_list[i]), outfile)
                    outfile.write('\n')

            self.bgq_obj.local_json_bigquery(self.endpoint+".json")
