billablewunderlist
==================

Sets a Wunderlist task as done when a certain amount of billable time has been clocked in Harvest.

Deployment
==========

    $ heroku create
    $ heroku config:set HARVEST_EMAIL=production
    $ heroku config:set HARVEST_PASSWORD=XXX
    $ heroku config:set HARVEST_HOURS_REQUIRED=XXX
    $ heroku config:set HARVEST_COMPANY_NAME=XXX
    $ heroku config:set WL_ACCESS_TOKEN=XXX
    $ heroku config:set WL_CLIENT_ID=XXX
    $ heroku config:set WL_MON_TASK=XXX
    $ heroku config:set WL_TUE_TASK=XXX
    $ heroku config:set WL_WED_TASK=XXX
    $ heroku config:set WL_THU_TASK=XXX
    $ heroku config:set WL_FRI_TASK=XXX
    $ heroku config:set WL_CALENDAR_LIST_ID=XXX
    $ heroku config:set WL_INCOMPLETE_LIST_ID=XXX
    $ git push heroku master
    $ heroku run python manage.py syncmedia

