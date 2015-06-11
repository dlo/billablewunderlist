# vim: set fileencoding=utf-8 :

from datetime import datetime
import requests
from dateutil import parser

import os

HARVEST_EMAIL = os.environ['HARVEST_EMAIL']
HARVEST_PASSWORD = os.environ['HARVEST_PASSWORD']
HARVEST_HOURS_REQUIRED = int(os.environ['HARVEST_HOURS_REQUIRED'])
HARVEST_COMPANY_NAME = os.environ['HARVEST_COMPANY_NAME']

WL_MON_TASK = os.environ['WL_MON_TASK']
WL_TUE_TASK = os.environ['WL_TUE_TASK']
WL_WED_TASK = os.environ['WL_WED_TASK']
WL_THU_TASK = os.environ['WL_THU_TASK']
WL_FRI_TASK = os.environ['WL_FRI_TASK']

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
if total_hours >= threshold:
    # Get current day's task in Wunderlist. Mark as completed.
    url = "https://a.wunderlist.com/api/v1/tasks"
    params = {'list_id': 163624279}
    response = requests.get(url, params=params, headers=headers)
    tasks = response.json()
    today = datetime.date.today()
    todays_task_id = weekdays_to_tasks[today.weekday()]

    for task in tasks:
        due_date = parser.parse(task['due_date']).date()
        ccreated_by_request_id = task['created_by_request_id']
        if due_date == today and (todays_task_id == str(task['id']) or todays_task_id in created_by_request_id):
            headers = {
                'X-Access-Token': WL_ACCESS_TOKEN,
                'X-Client-ID': WL_CLIENT_ID,
                'Content-Type': "application/json"
            }
            url = "https://a.wunderlist.com/api/v1/tasks/{}".format(task['id'])
            new_revision = task['revision'] + 1
            data = {
                'revision': new_revision,
                'completed': True
            }
            response = requests.patch(url, data=data, headers=headers)
