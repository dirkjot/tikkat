# Tikkat

_A potential ticket system for PWS Platform_

This is very much a work in progress, maybe even a HVP (hardly viable prototype).

## Working parts

- Tickets come in our slack channels
- A webform is used to enter tickets (currently in airtable, future in Google Forms?)
- Airtable is used to track the tickets
- A bots only slack channel (#darkbots) is used to log all airtable actions (to overcome limitations in airtable)
- This software monitors #darkbots and updates airtable records when a ticket is started or completed
- Simple 'block' graphs in airtable show time to respond and time to resolve.

Future extensions:
- Given that we are already listening to every slack update, we can serve the user the form when we spot the word 'help'
- The airtable form is limited, a google form would be better (for example, we can ask extra questions if we need to share a password)
- The block graphs in airtable are nice, a simple webpage dashboard would be prettier and easier to put on a monitor (information radiator)


## Running and testing

Code is one Python3, under `src`.  Currently, everything is run from the `src` directory; it is my aim to change that.

To load dependencies:
```
pip3 install -r requirements.txt
```

To execute:
```
# run
python3 tikkat.py
```

To run the tests:
```
# make sure this uses Python3 pytest OR python3 -m pytest
pytest
```
