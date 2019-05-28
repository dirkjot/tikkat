from airtable import Airtable
import os
from pprint import pprint

# apikey = os.environ.get('AIRTABLE_API_KEY')
baseid = os.environ.get('AIRTABLE_BASE')
tablename = 'Tickets'
base = Airtable(baseid, tablename)
#print(base.get_all())
for page in base.get_iter(maxRecords=1):
    for record in page:
        pprint(record)


