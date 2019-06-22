"""
Compute and display our ticket SLO measures

SLO #1:  The percentage of ticket completed on time

SLO $2:  The average completion time for High/Medium/Low urgency tickets

"""


import slack
import os
from airtable import Airtable
from pprint import pprint
from datetime import datetime
from requests.exceptions import HTTPError
from datetime import datetime, timedelta

f"This should be run in Python 3.6 or higher"


