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
AIRTABLE_BOT_ID = 'BJUEU6P60'


# note that the namespacing has changed as of slackclient 2.0
slackclient = slack.WebClient(token=os.environ.get('SLACK_TOKEN'))


# when State (a hardcoded column name) is changed to value X, add a timestamp to column Y
# this maps X to Y
state_to_field = {
        'Completed': 'Completion',
        'Not Us': 'Completion',
        'Started': 'Started'}
all_states = state_to_field.keys()

#######################


class objectview(object):
    """Convert dict(or parameters of dict) to object view
    See also:
        - https://goodcode.io/articles/python-dict-object/
        - https://stackoverflow.com/questions/1305532/convert-python-dict-to-object
    >>> o = objectview({'a': 1, 'b': 2})
    >>> o.a, o.b
    (1, 2)
    >>> o = objectview(a=1, b=2)
    >>> o.a, o.b
    (1, 2)
    """

    def __init__(self, *args, **kwargs):
        d = dict(*args, **kwargs)
        self.__dict__ = d

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


#######################
# Completion and Started timestamp updates
# This has some overlap with the generic case above


class FieldUpdate(object):
    """
    Record to hold state changes so that we can update Completion/Started fields
    """
    title = newvalue = table = record = timestamp = None
    def __init__(self, title, newvalue, table, record, timestamp):
        self.title = title
        self.newvalue = newvalue
        self.table = table
        self.record = record
        self.timestamp = timestamp

    def __str__(self):
        return f"Found {self.title} changed to {self.newvalue} for record {self.record} in {self.table} at ts {self.timestamp}"


def get_airdetails_from_link(slack_title_link):
    "Given a slack title link, extract table name and record name"
    return slack_title_link.split('/')[3:]


def is_the_right_type_of_message(message):
    "check for bot messages from our bot, with attachments"
    return (message['type'] == 'message' and
        message.get('subtype') == 'bot_message' and
        message['bot_id'] == AIRTABLE_BOT_ID and
        message.get('attachments') is not None)


def generate_updates_for_states(slackclient, states=all_states, count=100, oldest=0):
    """
    Generator that reads the #darkbots private channel (a group in Slack API) for update from Airtable and
    parse them, generate a stream of FieldUpdate records

    - states: list of states to create records for
    - count: max number of messages to retrieve from Slack
    - oldest: timestamp to limit message retrieval, only messages after this
    """
    # MAYBE we need to page through this if we ever get more than count messages
    # Slack gotcha: this call is specific to private channels (groups)
    hist = slackclient.groups_history(
        channel='GJV0WJUPJ',  # darkbots group
        count=count, oldest=oldest)
    ok = hist.get('ok')
    assert ok is not None

    messages = hist.get('messages')
    print(f"Retrieved {len(messages)} messages from Slack")

    for message in messages:
        if (is_the_right_type_of_message(message)):
            for attachment in message['attachments']:
                for field in attachment['fields']:
                    if field['title'] == 'State' and field['value'] in states:
                        # state was updated
                        table, record = get_airdetails_from_link(attachment['title_link'])
                        if False  or table != AIRTABLE_TABLEID:
                            print(f"Ignoring updates to other table {table}")
                        else:
                            fup = FieldUpdate(
                                field['title'], field['value'], table, record, message['ts'])
                            yield(fup)



def airtable_update_completion(updategen, tickets_table):
    """
    For each FieldUpdate generated by updategen, fill the
    appropriate record in airtable 'tickets_table' with the timestamp
    in the FieldUpdate
    """

    for upd in updategen:
        try:
            record = tickets_table.get(upd.record)
        except HTTPError:
            print(f"Record with state changes ignored, as record not found: {upd.record}")
            continue

        assert record['id'] == upd.record
        airfield = state_to_field.get(upd.newvalue)
        if record['fields'].get(upd.title) != upd.newvalue:
            print(f"Warning update {upd.record} column {airfield}  even though {upd.title} is now {record['fields'].get(upd.title)}, not {upd.newvalue} ")

        if airfield:
            if record['fields'].get(airfield) is None:
                datestring = datetime.utcfromtimestamp(int(float(upd.timestamp))).strftime('%Y-%m-%d')
                record = tickets_table.update(upd.record, {airfield: datestring})
                print(f"SET Airtable {airfield} to {datestring} because {upd}" )
            else:
                print(f"Field {airfield} already has a value, ignoring {upd}" )
        else:
            print(f"Found State was changed to {upd.newvalue} but could not find a matching fieldname in 'state_to_field'")


def parse_airtable_updates_for_timestamps():
    oldest = (datetime.utcnow() - timedelta(days=2)) # one day back from now
    # TODO this somehow needs to be 2 days to work, not sure why
    print (f"Retrieving messages since {oldest} = {str(oldest.timestamp())}")
    airtable_update_completion(
        generate_updates_for_states(slackclient, count=500, oldest=str(oldest.timestamp())),
        tickets_table)





if __name__ == "__main__":
    parse_airtable_updates_for_timestamps()


