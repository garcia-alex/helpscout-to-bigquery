from google.cloud import bigquery


class BigQuery:
    def __init__(self, dataset_name=None, table_name=None):
        """
        The BigQuery API connection
        :param dataset_name: the name of your dataset as a string
        :param table_name: the name of your table as a string
        """

        self.__client = bigquery.Client()

        self.dataset_name = dataset_name
        self.table_name = table_name

        if dataset_name is not None:
            self.__dataset_ref = self.__client.dataset(dataset_name)  # Dataset
            self.__table_obj = self.__dataset_ref.table(table_name)  # Table

    def delete_table(self):
        """
        Delete a table where the data cannot be queried by date, and so is simplest to re-upload every time.
        :return:
        """
        self.__client.delete_table(self.__table_obj)
        print("Deleted table")

    def local_json_bigquery(self, json_file):
        """
        Post to BigQuery from a local json file
        :param json_file: The json file with HelpScout data to post
        """

        job_config = bigquery.LoadJobConfig()
        job_config.source_format = bigquery.SourceFormat.NEWLINE_DELIMITED_JSON
        job_config.autodetect = True

        # Chanege the location to whatever is relevant to you
        with open(json_file, 'r+b') as source_file:
            job = self.__client.load_table_from_file(
                source_file,
                self.__table_obj,
                location='EU',
                job_config=job_config,
            )

        job.result()  # Waits until the table load is complete
        print('Job Finished\n')

        print('Loaded {} rows into {}:{}'.format(job.output_rows, self.dataset_name, self.table_name))
