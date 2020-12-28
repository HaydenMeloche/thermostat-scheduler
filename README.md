# thermostat-scheduler
A simple python script that adjusts my Ecobee's schedule based on events in my calendar.

## How this works
Every morning at 5am my Raspberry PI runs `main.py`. On run, the script will fetch my calendar entries from my shared family calendar and filters them for events that occur today.

By default, my Ecobee is setup to turn on "home" mode every morning at 8am and then back to sleep mode at 11pm.
If a calendar event starts prior to 8am or runs later than 11pm, then the script will send a "hold" command to the ecobee specifying the time it needs to cover.
For example, if a calendar event started at 7:30am, the script will tell the ecobee to kick into home mode at 6:30am rather than 8am.

If no events meet the criteria, then the Ecobee will stick to its default schedule.

## Setup
Prior to running the script you will need to set up some environment variables.

All Ecobee variables require a Ecobee developer account and "app" created on the Ecobee site.
See [authenticating your Ecobee app.](https://www.ecobee.com/home/developer/api/examples/ex1.shtml)
```bash
CONFIGURED_MORNING_TIME # the time the Ecobee turns "home" mode on
CONFIGURED_NIGHT_TIME # the time the Ecobee turns "sleep" mode on
ECOBEE_TOKEN_URL # Ecobee API token URL
ECOBEE_THERMOSTAT_URL # Ecobee API thermostat URL
ECOBEE_APP_CODE # Your Ecobee app code
ECOBEE_APP_CLIENT_ID = # Your Ecobee app client id
```
Once all enviorment variables have been configured, you can launch the python script.
```bash
$ python main.py
```
