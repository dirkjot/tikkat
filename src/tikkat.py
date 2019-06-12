import os

from flask import Flask, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

# internal
import airtable_dates


verification_token=os.environ.get('VERIFICATION_TOKEN')


app = Flask(__name__)


@app.route('/rj75ud/slash', methods=['POST'])
def slash():
    "Simple slash command"
    if request.form['token'] == verification_token:
        payload = {'text': 'Meow - Tikkat does not say much yet.'}
        return jsonify(payload)


def setup_scheduler():
    "The AP Scheduler is used to run our airtable parse regularly"

    executors = {
        'default': ThreadPoolExecutor(1) } 
    job_defaults = {
        'coalesce': True,
        'max_instances': 3  }
    scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults)
    scheduler.add_job(airtable_dates.parse_airtable_updates_for_timestamps, 'interval', minutes=15)
    scheduler.start()



if __name__ == "__main__":
    setup_scheduler()
    app.run()
    
