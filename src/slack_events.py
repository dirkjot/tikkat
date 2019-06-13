"""
Respond to slack events.  This is the 2019 way to listen to conversations and respond when we are called. 

See 
- Events API docs: https://api.slack.com/events-api
- Python API : https://github.com/slackapi/python-slack-events-api
- Challenge request: https://api.slack.com/events/url_verification

"""

from flask import Flask
from slackeventsapi import SlackEventAdapter
import os



# This `app` represents your existing Flask app
app = Flask(__name__)

# An example of one of your Flask app's routes
@app.route("/hello")
def hello():
  return "<html><h1>Slack events up</h1></html>"


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


if __name__ == "__main__":
  app.run(port=5000)