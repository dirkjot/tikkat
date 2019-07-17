"""
Compute and display our ticket SLO measures

SLO #1:  The percentage of ticket completed on time

SLO $2:  The average completion time for High/Medium/Low urgency tickets

"""

import slack
import os
from airtable import Airtable
from pprint import pprint
from requests.exceptions import HTTPError
from datetime import datetime, timedelta
import pandas as pd
from flask import Blueprint, request, abort, make_response, render_template
from jinja2 import TemplateNotFound

f"This should be run in Python 3.6 or higher"

baseid = os.environ.get('AIRTABLE_BASE')
AIRTABLE_TABLENAME = os.environ.get('AIRTABLE_TICKET_TABLE_NAME', 'Tickets')
AIRTABLE_TABLEID = os.environ.get('BASE_TICKETS', 'tblA4zbHiw2Lqyvzo')
tickets_table = Airtable(baseid, AIRTABLE_TABLENAME)
verification_token=os.environ.get('VERIFICATION_TOKEN')


slo = Blueprint('slo', __name__, template_folder='templates')
@slo.route('/slo')
def slo_main():
    "Main and only page for SLO"
    ontime, groupmeans, groupsizes = runstats(getdonedusted())
    response = make_response(render_template('slo_page.html',
        ontime=ontime, groupmeans=groupmeans, groupsizes=groupsizes))
    response.headers.set('Pragma','No-Cache')
    return response


def getdonedusted():
    "Retrieve donedusted table from airtable, in DataFrame format"
    rawres = tickets_table.get_all(maxRecords=999, view="DoneDusted",
        fields=['DaysTaken','Urgency','SoftDeadline','Deadline', 'Completion'])
    # Example record, note Deadline not returned as nil
    # {'id': 'recJdo3yte2NmnHAW',
    #  'fields': {'Urgency': 'Medium',
    #   'SoftDeadline': '2019-06-07T01:00:00.000Z',
    #   'DaysTaken': 0},
    #  'createdTime': '2019-06-04T06:42:20.000Z'}

    da = pd.DataFrame([res['fields'] for res in rawres])
    return da

def runstats(da):
    "Given donedusted data, compute stats"
    # replace empty values for Deadline with SoftDeadline
    da.Deadline.fillna(da.SoftDeadline, inplace=True)
    # compute SLO 1, assuming completion happened at start of day,
    # so completion *at* deadline date is passing the SLO
    da['ontime'] = pd.to_datetime(da.Completion, utc=True) < pd.to_datetime(da.Deadline, utc=True)
    ontime = da.ontime.mean()

    # note that groupmeans need a double index (groupmeans['ontime']['High'])
    # but groupsizes does not, groupsizes['Low']
    groupmeans = da.groupby('Urgency').mean()
    groupsizes = da.groupby('Urgency').size()

    # visual formatting of percentages and averages
    ontime = round(ontime*100, 0)
    groupmeans['ontime'] = round(groupmeans['ontime']*100, 0)
    groupmeans['DaysTaken'] = round(groupmeans.DaysTaken, 1)

    return ontime, groupmeans, groupsizes
