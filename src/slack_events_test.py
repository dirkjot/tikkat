# run with option to supress warning:
#  pytest -W ignore::DeprecationWarning slack_events_test.py

import slack_events as subject
from unittest.mock import MagicMock


def test_hello():
    ""
    with subject.app.test_client() as c:
        actual = c.get('/hello')
        assert b'Slack events up' in actual.data


def XXtest_mention():
    ""
    event = {
        'channel': 'CKHQ6FAMS',
        'client_msg_id': 'acc0596d-b12f-4601-8c70-7f4e02e1c7d9',
        'event_ts': '1560438906.001300',
        'parent_user_id': 'U0AB10953',
        'text': '<@UKHHR1BK2> thread',
        'thread_ts': '1560438884.001000',
        'ts': '1560438906.001300',
        'type': 'app_mention',
        'user': 'U0AB10953'}
    event_data = {
        'event': event,
        'token': subject.verification_token}

    with subject.app.test_client() as c:
        actual = c.post('/slack/events', json=event_data)
        assert b'Slack events up' in actual.data


def test_close_ticket_in_thread():
    "this is a pretty horrible test but hard to change that in this architecture"
    event_data = {'event': {'channel': 'CKHQ6FAMS',
                            'text': '<@UKHHR1BK2> thread',
                            'thread_ts': '1560438884.001000',
                            'ts': '1560438906.001300',
                            'user': 'U0AB10953'},
                  'token': '123'}

    fake_findAirtableRecordFromSlackThread = MagicMock()
    subject.airtable_dates.findAirtableRecordFromSlackThread = fake_findAirtableRecordFromSlackThread
    fake_findAirtableRecordFromSlackThread.return_value = \
        [{'id': 'recLJBBNTJhrC05a4',
          'fields': {'TicketName': 'Kevin Kelani',
                     'Urgency': 'Medium',
                     'State': 'Not Us',
                     'Slack Thread Link': 'https://pivotal.slack.com/archives/CKHQ6FAMS/p1560438884001000',
                     'TicketId': 7,
                     'Created Time': '2019-05-20T23:07:06.000Z'},
          'createdTime': '2019-05-20T23:07:06.000Z'}]
    changereq = MagicMock()
    subject.airtable_dates.AirtableChangeRequest = changereq
    changereq.return_value = changereq
    subject.slackclient.chat_postMessage = MagicMock()

    subject.close_ticket_in_thread(event_data)

    fake_findAirtableRecordFromSlackThread.assert_called_once_with('https://pivotal.slack.com/archives/CKHQ6FAMS/p1560438884001000')
    changereq.assert_called_once_with('recLJBBNTJhrC05a4','State','Not Us', 'Completed')
    changereq.run.assert_called_once_with()
    subject.slackclient.chat_postMessage.assert_called_once()

    ## test with zero matching records
    fake_findAirtableRecordFromSlackThread.return_value = []
    fake_findAirtableRecordFromSlackThread.reset_mock()
    changereq.run.reset_mock()
    subject.slackclient.chat_postMessage.reset_mock()

    subject.close_ticket_in_thread(event_data)

    fake_findAirtableRecordFromSlackThread.assert_called_once_with('https://pivotal.slack.com/archives/CKHQ6FAMS/p1560438884001000')
    changereq.assert_called_once_with('recLJBBNTJhrC05a4','State','Not Us', 'Completed')
    assert changereq.run.call_count == 0
    subject.slackclient.chat_postMessage.assert_called_once()



