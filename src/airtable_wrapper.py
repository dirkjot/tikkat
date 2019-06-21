import slack
import os
from airtable import Airtable
from pprint import pprint
from datetime import datetime
from requests.exceptions import HTTPError
from datetime import datetime, timedelta

f"This should be run in Python 3.6 or higher"

baseid = os.environ.get('AIRTABLE_BASE')
AIRTABLE_TABLENAME = 'Tickets'
AIRTABLE_TABLEID = 'tblA4zbHiw2Lqyvzo'
tickets_table = Airtable(baseid, AIRTABLE_TABLENAME)


#####################
# Generic Airtable updates

class AirtableChangeException(Exception):
    pass

def findAirtableRecordFromSlackThread(slackthread):
    """From an slack thread URL, find the matching airtable records, returning an array of airtable records

    Return limited to 9 records.
    Returns a list of dicts, each dict has standard AirTable structure, ie 'id', 'createdTime' and a 'fields' dict with each
    column name and value for which the value is non-zero.
    """
    # curl "https://api.airtable.com/v0/appG79slE6qPaJ3eV/Tickets?maxRecords=9&filterByFormula=%7BSlack%20Thread%20Link%7D%3D%27https%3A%2F%2Fwww.pivotaltracker.com%2Fstory%2Fshow%2F166143448%27%0A"   -H "Authorization: Bearer ..."
    return tickets_table.search('Slack Thread Link', slackthread, max_records=9)


class AirtableChangeRequest(object):
    "Request to change a column from oldvalue to newvalue for a recordId"

    def __init__(self, recordId, column, oldvalue, newvalue):
        self.column = column
        self.oldvalue = oldvalue
        self.newvalue = newvalue
        self.recordId = recordId

    def __str__(self):
        return f"[AirtableChangeRequest col {self.column} from {self.oldvalue} to {self.newvalue} for {self.recordId}]"

    def run(self):
        "Make the update"
        try:
            record = tickets_table.get(self.recordId)
        except HTTPError:
            raise AirtableChangeException(f"Record with state changes ignored, as record not found: {self.recordId}")
        assert record['id'] == self.recordId
        if record['fields'].get(self.column) != self.oldvalue:
            raise AirtableChangeException(f"Record with state changes ignored, as old value for record does not match: {self.recordId}"
                    f"col {self.column} should be {self.oldvalue} was {record['fields'].get(self.column)}")
        tickets_table.update(self.recordId, {self.column: self.newvalue})
