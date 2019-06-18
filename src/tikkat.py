import os

from flask import Flask, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

# internal
import airtable_dates
from slack_events import app
from slack_slash import slash



#######################


f"This should be run in Python 3.6 or higher"




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
    app.register_blueprint(slash)
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


