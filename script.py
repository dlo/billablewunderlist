#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import logging
import sys
import collections
import json
import datetime
import requests
from dateutil import parser

import os

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

HARVEST_EMAIL = os.environ['HARVEST_EMAIL']
HARVEST_PASSWORD = os.environ['HARVEST_PASSWORD']
HARVEST_HOURS_REQUIRED = int(os.environ['HARVEST_HOURS_REQUIRED'])
HARVEST_COMPANY_NAME = os.environ['HARVEST_COMPANY_NAME']

WL_MON_TASK = os.environ['WL_MON_TASK']
WL_TUE_TASK = os.environ['WL_TUE_TASK']
WL_WED_TASK = os.environ['WL_WED_TASK']
WL_THU_TASK = os.environ['WL_THU_TASK']
WL_FRI_TASK = os.environ['WL_FRI_TASK']
WL_CALENDAR_LIST_ID = int(os.environ['WL_CALENDAR_LIST_ID'])
WL_INCOMPLETE_LIST_ID = int(os.environ['WL_INCOMPLETE_LIST_ID'])

WL_ACCESS_TOKEN = os.environ['WL_ACCESS_TOKEN']
WL_CLIENT_ID = os.environ['WL_CLIENT_ID']

now = datetime.datetime.now()
year = now.timetuple().tm_year
day_of_year = now.timetuple().tm_yday
url = "https://{}.harvestapp.com/daily/{}/{}".format(HARVEST_COMPANY_NAME, day_of_year, year)
auth = (HARVEST_EMAIL, HARVEST_PASSWORD)
headers = {'Accept': "application/json"}
response = requests.get(url, auth=auth, headers=headers)

tasks_to_hours = collections.defaultdict(lambda: 0)
hours = 0
billable_tasks = set()

projects = response.json()['projects']
for project in projects:
    if project['billable']:
        for task in project['tasks']:
            if task['billable']:
                billable_tasks.add(task['id'])

entries = response.json()['day_entries']
for entry in entries:
    task_id = entry['task_id']
    if task_id in billable_tasks:
        hours += entry['hours']

weekdays_to_tasks = [WL_MON_TASK, WL_TUE_TASK, WL_WED_TASK, WL_THU_TASK, WL_FRI_TASK]

total_hours = sum(map(lambda k: k['hours'], entries))

# Get current day's task in Wunderlist. Mark as completed. If yesterday's task was incomplete, move it to the trash.
url = "https://a.wunderlist.com/api/v1/tasks"
params = {'list_id': WL_CALENDAR_LIST_ID}
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
todays_task_id = weekdays_to_tasks[today.weekday()]

headers = {
    'X-Access-Token': WL_ACCESS_TOKEN,
    'X-Client-ID': WL_CLIENT_ID,
    'Content-Type': "application/json"
}

response = requests.get(url, params=params, headers=headers)
tasks = response.json()

logger.info("Looping through tasks...")
for task in tasks:
    update_url = "https://a.wunderlist.com/api/v1/tasks/{}".format(task['id'])
    if 'due_date' in task:
        due_date = parser.parse(task['due_date']).date()
        created_by_request_id = task['created_by_request_id']
        revision = task['revision']
        if total_hours >= HARVEST_HOURS_REQUIRED and \
                due_date == today and \
                (todays_task_id == str(task['id']) or todays_task_id in created_by_request_id):

            data = {
                'revision': revision,
                'completed': True
            }
            response = requests.patch(update_url, data=json.dumps(data), headers=headers)
            if response.status_code == 200:
                logger.info("Marked task {} as completed for {}.".format(task['id'], due_date))
            else:
                logger.error("There was an error marking task {} as completed for {}.".format(task['id'], due_date))

        elif due_date == yesterday:
            # Have to move and then complete the task in two steps
            data = {
                'revision': revision,
                'list_id': WL_INCOMPLETE_LIST_ID
            }
            requests.patch(update_url, data=json.dumps(data), headers=headers).text

            data = {
                'revision': revision + 1,
                'completed': True
            }
            response = requests.patch(update_url, data=json.dumps(data), headers=headers)
            if response.status_code == 200:
                logger.info("Marked task {} as incompleted for {}.".format(task['id'], yesterday))
            else:
                logger.error("There was an error marking task {} as incomplete for {}.".format(task['id'], yesterday))
