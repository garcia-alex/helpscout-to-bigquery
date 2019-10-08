import datetime as dt
from datetime import datetime

from src.helpscoutDL import HelpScoutDataLoader, endpoints

import pandas as pd

N_WEEKS = 1

today = datetime.today()  # Today
last_week_start = today - dt.timedelta(days=today.weekday(), weeks=N_WEEKS)  # Monday of previous week
last_week_end = today - dt.timedelta(days=today.weekday(), weeks=N_WEEKS-1) # This Monday

last_week_start = last_week_start.replace(hour=0, minute=0, second=0, microsecond=0)
last_week_end = last_week_end.replace(hour=0, minute=0, second=0, microsecond=0)

# All time:
dates = pd.date_range(start='2018-03-16',  # Enter the date you started using HelpScout
                      end=last_week_end,
                      freq='W')

MODE_BACKFILL = False
MODE_WEEKLY = True


def upload(__start, __end):
    for endpoint in endpoints.keys():
        helpscoutdl_obj = HelpScoutDataLoader(__start, __end, endpoint)
        helpscoutdl_obj.get_data_for_upload()
        helpscoutdl_obj.write()


if __name__ == "__main__":

    if MODE_BACKFILL:
        for i in range(len(dates)-1):
            start = dates[i]
            end = dates[i + 1]
            upload(start, end)

    elif MODE_WEEKLY:
        start = last_week_start
        end = last_week_end
        upload(start, end)
