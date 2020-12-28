import json
import os
from datetime import datetime, timedelta

import pytz
import requests
from icalevents.icalevents import events

PYTZ_TIMEZONE = pytz.timezone('US/Eastern')
CONFIGURED_MORNING_TIME = int(os.environ.get('CONFIGURED_MORNING_TIME'))
CONFIGURED_NIGHT_TIME = int(os.environ.get('CONFIGURED_NIGHT_TIME'))
ECOBEE_TOKEN_URL = os.environ.get('ECOBEE_TOKEN_URL')
ECOBEE_THERMOSTAT_URL = os.environ.get('ECOBEE_THERMOSTAT_URL')
ECOBEE_APP_CODE = os.environ.get('ECOBEE_APP_CODE')
ECOBEE_APP_CLIENT_ID = os.environ.get('ECOBEE_APP_CLIENT_ID')


def main():
    todays_events = list(filter(lambda x: x.start.date() == datetime.today().date() and not x.all_day, get_events()))

    # my ecobee turns on by default at 8am every morning. Lets check if we need to adjust that
    early_events = get_early_events(todays_events)
    if len(early_events) > 0:
        print('Event detected before', CONFIGURED_MORNING_TIME, 'hours. Adjusting thermostat this morning...')
        earliest_event = early_events[0]
        thermostat_wake_up_time = earliest_event.start - timedelta(hours=1)
        print('Telling thermostat to wake up at: ' + str(thermostat_wake_up_time))
        adjust_thermostat(thermostat_wake_up_time, create_today_with_time(CONFIGURED_MORNING_TIME))
    else:
        print("No events before", CONFIGURED_MORNING_TIME, "am we're detected")

    late_events = get_late_events(todays_events)
    if len(late_events) > 0:
        print('Event detected after', CONFIGURED_NIGHT_TIME, 'hours. Adjusting thermostat for tonight...')
        latest_event = late_events[0]
        thermostat_shutdown_time = latest_event.end + timedelta(hours=1)
        print('Telling thermostat to shutdown at: ' + str(thermostat_shutdown_time))
        adjust_thermostat(create_today_with_time(CONFIGURED_NIGHT_TIME), thermostat_shutdown_time)
    else:
        print("No events after", CONFIGURED_NIGHT_TIME, "am we're detected")

    print('Script completed')


def adjust_thermostat(start_time, end_time, mode="home"):
    request = json.loads('{"selection":{"selectionType":"registered","selectionMatch":""},"functions":[{'
                         '"type":"setHold","params":{"holdType":"dateTime","holdClimateRef":"populate",'
                         '"startDate":"populate","startTime":"populate","endDate":"populate",'
                         '"endTime":"populate"}}]}')

    request['functions'][0]['params']['holdClimateRef'] = mode
    request['functions'][0]['params']['startDate'] = start_time.date()
    request['functions'][0]['params']['startTime'] = start_time.time()
    request['functions'][0]['params']['endDate'] = end_time.date()
    request['functions'][0]['params']['endTime'] = end_time.time()

    bearer_token = get_access_token()

    response = requests.post(ECOBEE_THERMOSTAT_URL, data=json.dumps(request, default=str),
                             headers={'Authorization': 'Bearer ' + bearer_token})

    if response.ok:
        print('Thermostat updated.')
    else:
        print('Failure sending request to thermostat')


def get_access_token():
    response = requests.get(ECOBEE_TOKEN_URL,
                            {'grant_type': 'refresh_token', 'code': ECOBEE_APP_CODE, 'client_id': ECOBEE_APP_CLIENT_ID})

    return response.json()['access_token']


def get_late_events(todays_events):
    late_events = list(filter(lambda x: x.end >= datetime.today()
                              .replace(hour=int(CONFIGURED_NIGHT_TIME), minute=0, second=0, microsecond=0)
                              .astimezone(PYTZ_TIMEZONE), todays_events))

    late_events.sort(key=lambda x: x.end, reverse=True)

    return late_events


def get_early_events(todays_events):
    early_events = list(filter(lambda x: x.start <= datetime.today()
                               .replace(hour=int(CONFIGURED_MORNING_TIME), minute=0, second=0, microsecond=0)
                               .astimezone(PYTZ_TIMEZONE), todays_events))

    early_events.sort(key=lambda x: x.start, reverse=False)

    return early_events


def get_events():
    cal_events = events(os.environ.get('ICAL_URL'), fix_apple=True)

    # Adjust timezone to eastern time
    for item in cal_events:
        item.start = item.start.astimezone(PYTZ_TIMEZONE)
        item.end = item.end.astimezone(PYTZ_TIMEZONE)

    cal_events.sort(key=lambda x: x.start, reverse=False)

    return cal_events


def create_today_with_time(hour):
    return datetime.today().replace(hour=hour, minute=0, second=0, microsecond=0)


if __name__ == '__main__':
    main()
