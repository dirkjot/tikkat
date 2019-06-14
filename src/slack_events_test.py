# run with option to supress warning:
#  pytest -W ignore::DeprecationWarning slack_events_test.py 

import slack_events as subject


def test_hello():
    ""
    with subject.app.test_client() as c:
        actual = c.get('/hello')
        assert b'Slack events up' in actual.data 


def XXtest_mention():
    ""
    event =  {
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



    #result = subject.mention(event_data)
    #assert result.startswith('Tikkat PWS Platform bot')