import json
import os
import re

from pandas.io.json import json_normalize
import stringcase

BGQ_DATASET = 'helpscout_prod'  # enter the name of your Google BigQuery Dataset
from util.bigqueryAPI import BigQuery
from util.helpscoutMethods import HelpScoutMethods

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
        self.table_schema = self.bgq_obj.get_table_schema()

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

            d = eval('self.helpscoutfunc_obj.'+self.endpoint+'()')

            # Here we delete any new fields that have been added to the HelpScout API,
            # but are not in our existing schema.
            schema = json_normalize(self.table_schema)

            if 'fields' in list(schema.columns):
                schema = schema[['type', 'name', 'mode', 'fields']]
                schema_trim = schema.drop(['fields'], axis=1)

                for i, val in enumerate(schema['name']):
                    if schema.iloc[i]['type'] == 'RECORD':
                        temp = json_normalize(schema['fields'][i])
                        temp['name'] = schema.iloc[i]['name'] + '.' + temp['name']
                        temp = temp[['type', 'name', 'mode']]
                        schema_trim = schema_trim.append(temp)

                schema_trim = schema_trim.sort_values(by='name')
                schema_trim_names = list(schema_trim['name'])

                d_list = list()
                d_lookup = dict()

                for col in json_normalize(d).columns:
                    temp = stringcase.snakecase(col)
                    d_list.append(temp)
                    d_lookup[temp] = col
                    if type(json_normalize(d)[col][0]) == list:
                        if len(json_normalize(d)[col][0]) > 0:
                            if type(json_normalize(d)[col][0][0]) == dict:
                                for key in list(json_normalize(d)[col][0][0].keys()):
                                    temp = stringcase.snakecase(col) + '.' + stringcase.snakecase(key)
                                    d_list.append(temp)
                                    d_lookup[temp] = col + '.' + key

                for i in range(len(d)):
                    try:
                        for key, value in d_lookup.items():
                            if key not in schema_trim_names:
                                del d[i][value.split('.')[0]][0][value.split('.')[1]]
                    except KeyError:
                        pass

            # removing the existing json file
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
                # NB: please ensure the table exists in the dataset, or this will fail
                self.bgq_obj.delete_table()  # if re-upload is on, delete the table.

            # Overwrite with sorted list
            # (little hack - takes longest lines first therefore most likely to contain all sub-fields):
            with open(self.endpoint+'.json') as f:
                content = f.readlines()

            sorted_list = sorted(content, key=len, reverse=True)

            try:
                os.remove(self.endpoint+".json")
            except OSError:
                pass

            for i in range(len(sorted_list)):
                with open(self.endpoint+'.json', 'a') as outfile:
                    json.dump(json.loads(sorted_list[i]), outfile)
                    outfile.write('\n')

            self.bgq_obj.local_json_bigquery(self.endpoint+".json", autodetect=False, schema=self.table_schema)
