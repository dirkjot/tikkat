# from airtable import Airtable
# import os
# from pprint import pprint

# # apikey = os.environ.get('AIRTABLE_API_KEY')
# baseid = os.environ.get('AIRTABLE_BASE')
# tablename = 'Tickets'
# base = Airtable(baseid, tablename)
# #print(base.get_all())
# for page in base.get_iter(maxRecords=1):
#     for record in page:
#         pprint(record)




# note that the namespacing has changed as of slackclient 2.0
import slack 
import os

client = slack.WebClient(token=os.environ.get('SLACK_API_TOKEN'))
response = client.chat_postMessage(
        channel=u'#darkbots',
        text="Hello python slack client!")
assert response["ok"]


@slack.RTMClient.run_on(event='message')
def say_hello(**payload):
        data = payload['data']
        web_client = payload['web_client']
        rtm_client = payload['rtm_client']
        text = data.get('text', '')
        #print('.', end='')
        print(text[:15])
        if '!darkbot' in text:
            channel_id = data['channel']
            thread_ts = data['ts']
            user = data['user']
            print('\nResponding')

            web_client.chat_postMessage(
                channel=channel_id,
                text=f"Hi <@{user}>!",
                thread_ts=thread_ts
            )

slack_token = os.environ["SLACK_API_TOKEN"]
rtm_client = slack.RTMClient(token=slack_token)
rtm_client.start()
