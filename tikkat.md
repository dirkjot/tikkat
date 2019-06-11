# Tikkat - Experimental PWS Platform Slack Bot



# Development notes




## Auth

- Get Airbase API key from my account page
- Get base id from airtable.com/api (must be logged in), right click to get the url which
has the base id (starts with APP).
- All this stored in .envrc (in .gitignore)
- and backed up to lastpass as '/tikkat-envrc' (secure note)


## Slack App token
Slack app token for tikkat is in the .envrc  This page is the management page for it.  We should aim
to have this owned by a bot, service acccount???

WRONG this was a bot https://pivotal.slack.com/services/632419160354?updated=1


https://api.slack.com/apps/AKELREXRS?created=1




## Airtable API 
is super simple, and very limited.  basically just crud
https://airtable.com/appG79slE6qPaJ3eV/api/docs#javascript/table:tickets


Notable
- cannot introduce @mention, only remove existing ones.
- cannot listen for changes, only query
- links to 'action' table must be updated by reading, adding one and
  writing back, otherwise you'll replace all old ones with your one
  new one.
- cannot change the options of the dropdown




## Airtable does not do change notifications yet.  
YOu can either query the table, sort by time mod, and then take a few
latest adn run this on a poll loop.
OR you can use the slack integration and poll the slack channel
(darkbots in our case).  This has the advantage that we have to poll
slack anyway, and we avoid eating into the 5rps rate limit that
Airtable imposes.

This guy's got it figured out:
https://medium.com/@yoad/retrieve-latest-changes-from-airtable-api-b473f5d4cdf9


Alternatives (not taken):
- https://community.airtable.com/t/knowing-when-there-is-a-change-to-the-record/1518/8
- https://community.airtable.com/t/notification-when-field-value-changes/15944/3


## Parsing the updates in darkbots

each message has attachments, the updates are part of the attachments.
https://api.slack.com/docs/message-attachments

The attachments have fields that reflect the airtable fields (columns) that were updated.  We can
simply check for changing of the State field


## Using it on Cloud Foundry

in .envrc.json are the variable setttings that cf needs, they reflect the exports in .envrc.  Open the settings tab of the 
app in app manager and bulk/json edit to paste all of them in at once.  I'm sure there is a command line for that too.

```
cd src 
cf push -f manifest.yml 
cf logs tikkat
```



## Links/ topics

