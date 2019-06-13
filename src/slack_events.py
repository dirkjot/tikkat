"""
Respond to slack events.  This is the 2019 way to listen to conversations and respond when we are called. 

See 
- Events API docs: https://api.slack.com/events-api
- Python API : https://github.com/slackapi/python-slack-events-api
- Challenge request: https://api.slack.com/events/url_verification

"""

from flask import Flask, abort, request, jsonify
from slackeventsapi import SlackEventAdapter
import os
from pprint import pprint
import logging
import traceback
from time import strftime

verification_token = os.environ.get('VERIFICATION_TOKEN')

# This `app` represents your existing Flask app
app = Flask(__name__)
logger = logging.getLogger('slack_event')
logger.setLevel(logging.INFO)

# An example of one of your Flask app's routes
@app.route("/hello")
def hello():
  return "<html><h1>Slack events up</h1></html>"

# https://gist.github.com/oo1john/f6fc154a7fbcd9b85985efb796afe5b9
@app.after_request
def after_request(response):
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    logger.error('FlaskLog %s %s %s %s %s %s', timestamp, request.method, 
        request.scheme, request.full_path, request.data, response.status)
    return response

@app.errorhandler(Exception)
def exceptions(e):
    tb = traceback.format_exc()
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    logger.error('%s %s %s %s %s 5xx INTERNAL SERVER ERROR\n%s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, tb)
    abort(500)


# Bind the Events API route to your existing Flask app by passing the server
# instance as the last param, or with `server=app`.
# Wart: you have to bind this to /slack/events, or stuff won't work
# Maybe: I did not try if you can bind the slack adapter to a blueprint
slack_events_adapter = SlackEventAdapter(os.environ.get('SLACK_SIGNING_SECRET'), "/slack/events", app)


# Create an event listener for "reaction_added" events and print the emoji name
@slack_events_adapter.on("reaction_added")
def reaction_added(event_data):
  emoji = event_data["event"]["reaction"]
  print(emoji)

@slack_events_adapter.on("app_mention")
def mention(event_data):
    """

    Example event_data.event:
       {'channel': 'CKHQ6FAMS',
        'client_msg_id': 'acc0596d-b12f-4601-8c70-7f4e02e1c7d9',
        'event_ts': '1560438906.001300',
        'parent_user_id': 'U0AB10953',
        'text': '<@UKHHR1BK2> thread',
        'thread_ts': '1560438884.001000',
        'ts': '1560438906.001300',
        'type': 'app_mention',
        'user': 'U0AB10953'}

    """
    if (event_data['token'] != verification_token):
        pprint(event_data['token'])
        pprint("sign"+ verification_token)
        abort(404)
    print("app_mention")
    pprint(event_data['event'])

@slack_events_adapter.on("message.channels")
#@slack_events_adapter.on("message.groups")
#@slack_events_adapter.on("message.im")
def message_channels(event_data):
    """


    """
    print("msg chan")
    if (event_data['token'] != verification_token):
        pprint(event_data['token'])
        pprint("sign"+ verification_token)
        abort(404)
    print("message.channels")
    pprint(event_data['event'])



if __name__ == "__main__":
  app.run(port=5000)