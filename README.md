# helpscout-to-bigquery
Extracting data from the helpscout API and posting it to Google Cloud BigQuery.

# intro
Help Scout is a useful customer support platform, that allows you to track your interactions with your clients. Help Scout has an API allowing you to access all of your organisation's data. Off-the-shelf solutions for Help Scout data extraction & loading exist yet can be expensive.

At Octopus Labs, Kaustav Mitra and I developed an open source Help Scout data extraction package in Python that connects to the most useful Help Scout end-points and posts the data to a Google BigQuery SQL database.

# how it works
_helpscoutAPI_: This module is the interface with the Help Scout API. Within this, we have the HelpSout class with two general-purpose API-calling methods. 'get_helpscout_data' is a generic call, whilst 'get_pages_breakdown' is used when there are multiple pages.

_fields_: This module contains the mapping for the highest-level fields for each API endpoint, specifying whether it is a pure field or a record of fields. To make the module as lightweight as possible, we tried to avoid specifying the schema as much as possible, and make use of BigQuery's autodetect schema function. However, we found it problematic to not specify any of the schema whatsoever, as a given data dump was often not representative of edge cases. A record can accept null values for a given field, but a single value field cannot be turned into a record. Thus, we found a good compromise to be specifying the highest level of columns, and simply categorising them as either pure fields or records.

_helpscoutMethods_: This module contains some general-purpose methods (the static methods), as well as a method to process each API endpoint (the standard methods). 'generate_json' creates a json of the data to be uploaded from each endpoint. 'without_keys' creates a dictionary from a list excluding specific keys. Each given endpoint (conversations, customers, folders, mailboxes, ratings, threads, users) has its own method by the same name which returns the extracted data as a list of dictionaries, 'd'.

_bigqueryAPI_: This module is the interface with BigQuery and makes use of the google.cloud bigquery python module. We have adapted this to load rows into a Google BigQuery table from a json file.

_helpscoutDL_: 'DL' stands for 'Data Loader' and this module specifies how Help Scout data is loaded into Google BigQuery. Specify the name of your dataset in BGQ_DATASET. The 'endpoints' dictionary bears paying attention to. In each endpoint within the dictionary, 'on' determines whether the given endpoint will be queried in the run. By default, all are set to True. You can toggle these between True and False, depending on your needs. The 're_upload' key, on the other hand, should be kept as is, using this version of our package. Some Help Scout API endpoints cannot be directly queried by date. Where this is the case, we have decided to opt for the simple method of deleting the entire table and re-uploading the full data-set every time. This avoids messy updating of fields. It ensures we always have the most up-to-date data, and is not particularly expensive computationally because the non-date-dependent fields (customers, mailboxes, folders and users) are fairly small data-sets, compared with conversations and threads. For endpoints which can be queried using dates, data is appended on a week-by-week basis so data is never deleted. Another point worth mentioning is that we use a 'convert_camel_case' static method, which converts the column names of the data from camelCase to snake_case. This is purely a hack to employ a stylistic preference.

For each endpoint in the endpoints dictionary, we have two methods; 'get_data_for_upload' and 'write', which, as the names suggest, get the data for each endpoint and writes to the relevant table in BigQuery. We do this by getting the data, converting it to a json file, reading the json file and posting it using the BigQuery module from the google.cloud Python package.

One little hack that we've employed in this process is to sort the list of dictionaries of data from each point by the length of each line, descending (as we're working with newline delimited json). This is by no means a perfect method, but gives us a higher chance of fully outlining the data structure early on. In our experience, if you have a particularly large json file with lots of rows (say in the +1k rows order of magnitude), the way in which Google BigQuery parses the data can cause problems if the schema suddenly changes at, say, row 800. In other words, if the first 800 rows denote a field as being a pure field (e.g. a string), and then suddenly changes to a record (i.e. a list of fields), this can cause problems. However, if the most extensive edge cases are presented upfront, these problems are avoided. We already specify the highest level of fields in the 'fields.py' file, so this hack is only relevant to nested (sub) fields.

_main_: Following the general Python module structure, 'main' acts as the cockpit, controlling the module run. At Octopus, we do a weekly upload of data on Wednesdays for the previous week, ending Sunday night. This gives the customer support team a bit more time to do any manual tagging of the Help Scout conversations of the week before. In production, 'MODE_WEEKLY' should always be set to True, and 'MODE_BACKFILL' must be set to False. However, for the initial upload with back-fill, the opposite mode set up should be employed. In case the data for any given week is not fully representative of all the edge cases, you may want to add some extra code to stretch the weekly time-frame to catch all your edge cases. The below code snippet is a simple way of taking 12 week increments instead:

```
x = 0
increment = 12  # weeks
combined = list()  # initialise the list
end_dates = list()  # initialise the list

while (x+increment) <= (len(dates)+increment):
    combined.append(dates[x:x+increment][0])
    end_dates.append(dates[x:x+increment][-1])
    x += increment

combined.append(end_dates[-1])
```

Then, you simply replace 'dates' with 'combined' in the 'if MODE_BACKFILL' for-loop. There is no way of knowing if this is necessary for your specific dataset, and some trial and error iterations are advised. Once your data has been back-filled, you can keep MODE_BACKFILL off, and keep MODE_WEEKLY on in production.

Thanks for reading and we hope this helps. Good luck helping your customers & happy uploading!
