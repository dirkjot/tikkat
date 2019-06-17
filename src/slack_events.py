"""
Respond to slack events.  This is the 2019 way to listen to conversations and respond when we are called.

See
- Events API docs: https://api.slack.com/events-api
- Python API : https://github.com/slackapi/python-slack-events-api
- Challenge request: https://api.slack.com/events/url_verification

"""

from flask import Flask, abort, request, jsonify
from slackeventsapi import SlackEventAdapter
import slack
import airtable_dates

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

# Bind the Events API route to your existing Flask app by passing the server
# instance as the last param, or with `server=app`.
# Wart: you have to bind this to /slack/events, or stuff won't work
# Maybe: I did not try if you can bind the slack adapter to a blueprint
slack_events_adapter = SlackEventAdapter(os.environ.get('SLACK_SIGNING_SECRET'), "/slack/events", app)

slackclient = slack.WebClient(token=os.environ.get('SLACK_TOKEN'))


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

# @app.errorhandler(Exception)
# def exceptions(e):
#     tb = traceback.format_exc()
#     timestamp = strftime('[%Y-%b-%d %H:%M]')
#     logger.error('%s %s %s %s %s 5xx INTERNAL SERVER ERROR\n%s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, tb)
#     abort(500)



# Create an event listener for "reaction_added" events and print the emoji name
# @slack_events_adapter.on("reaction_added")
# def reaction_added(event_data):
#   emoji = event_data["event"]["reaction"]
#   print(emoji)

@slack_events_adapter.on("app_mention")
def mention(event_data):
    """


    """
    ensure_correct_token(event_data)
    dispatch = {
        new_ticket: ['new ticket', 'start ticket'],
        close_ticket: ['close ticket'] }

    text = event_data['event']['text'].lower()

    for handler, fragments in dispatch.items():
        for fragment in fragments:
            if fragment in text:
                handler(event_data)
                return
    give_help(event_data)


def makeThreadUrl(event_data):
    "Given event data, return a valid URL into the thread"
    # TODO add global for slack URL
    channel = event_data['event']['channel']
    pthread = 'p' + event_data['event']['thread_ts'].replace('.', '')
    threadurl = f"https://pivotal.slack.com/archives/{channel}/{pthread}"
    return threadurl


def new_ticket(event_data):
    print("Return new ticket")
    options={}
    if event_data['event'].get('thread_ts') is None:
        # message was made in main channel
        formlink = "https://forms.gle/EbNSJbL66XDqwJCi9"
        text = (
            f"Could you please fill out a short request form {formlink}. "
            f"It takes only a minute and it helps us a lot.\n"
            f"Thanks! _PWS Platform_")
    else:
        # message in thread, use prefilled link:
        threadurl = makeThreadUrl(event_data)
        formlink = f"https://docs.google.com/forms/d/e/1FAIpQLSfEpoWK3G1c7vOjkRK6HCOpmxn-QFVv6n2I3UFVY5OMBtTaAg/viewform?usp=pp_url&entry.43286154={threadurl}"
        text = (
            f"Could you please fill out a short request form? "
            f"It takes only a minute and it helps us a lot. \n"
            f"Thanks! _PWS Platform_ \n{formlink}")
        options['thread_ts'] = event_data['event']['thread_ts']
    slackclient.chat_postMessage(
        channel=event_data['event']['channel'],
        text=text,
        **options)


def close_ticket_in_thread(event_data):
    "Close airtable ticket that was opened in a thread"
    # TODO refactor this with our eventing system:
    threadurl = makeThreadUrl(event_data)
    recordContentsList = airtable_dates.findAirtableRecordFromSlackThread(threadurl)
    if len(recordContentsList) == 1:
        recordContents = recordContentsList[0]
        recordId = recordContents['id']
        oldvalue = recordContents['fields'].get('State')
        change = airtable_dates.AirtableChangeRequest(recordId, 'State', oldvalue, 'Completed')
        change.run()
        msg = ("We have now closed this ticket, but feel free to reopen it "
            "by calling the interrupt pair (`@interrupt`) or by opening a "
            "new ticket.\nThanks! _PWS Platform_")
    else:
        print(f"Expected 1 record to match, found {len(recordContentsList)} for url {threadurl}")
        msg = f"I could not find a unique ticket matching this thread. Help is on the way.  @interrupt "
    options = {}
    options['thread_ts'] = event_data['event']['thread_ts']
    slackclient.chat_postMessage(
        channel=event_data['event']['channel'],
        text=msg,
        **options)


def close_ticket(event_data):
    print("Return close ticket")
    if event_data['event'].get('thread_ts'):
        close_ticket_in_thread(event_data)
    else:
        # close was called in main channel
        slackclient.chat_postEphemeral(
            channel=event_data['event']['channel'],
            text=("I'm sorry but I can only close tickets from the thread that they were registered to.  "
                "Feel free to call the the interrupt pair (`@interrupt`) to help with this."
                "\nThanks! _PWS Platform_"),
            user=event_data['event']['user'])

def give_help(event_data):
    print("Help given")
    options = {}
    if event_data['event'].get('thread_ts'):
        options['thread_ts'] = event_data['event']['thread_ts']
    slackclient.chat_postEphemeral(
        channel=event_data['event']['channel'],
        text=("Tikkat PWS Platform bot knows these commands:\n"
            " - `new ticket`:  will send you a link to start a ticket\n"
            " - `close ticket`: will close the ticket linked to this thread (experimental)\n"),
        user=event_data['event']['user'],
        **options)


def ensure_correct_token(event_data):
    "Check the token and 404 if incorrect"
    if (event_data['token'] != verification_token):
        pprint(event_data['token'])
        pprint("Token was ^^,  should have been "+ verification_token)
        abort(404)


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