from pytz import timezone

import datetime, time, pytz
import urllib2, urllib, json
import sys

sys.path.append('instance')
from intranet_cfg import *


def handleDateList(dates, strformat):
    """ Function to return a date list in the passed strformat.

    This function is a helper function that will return a list
    of dates according to the supplied strformat.
    """
    dl = []

    for d in dates:
        #convertedDate = datetime.datetime(*(time.strptime(d[:-7].replace('T', ' '), '%Y-%m-%d %H:%M:%S')[0:6]))
        convertedDate = datetime.datetime(*(time.strptime(d.replace('T', ' '), '%Y-%m-%d %H:%M:%S')[0:6]))
        dl.append(getDateTimeAsString(
                    dt = convertedDate,
                    inTimezone = 'PST',
                    withStringFormat = strformat))

    return dl


def metricsServerRequest(method):
    """ Connect to the metrics server and return a result.

    This function returns JSON from the metrics server
    using the configuration variables given in the configuration
    file.
    """
    returned_json = urllib2.urlopen(METRICS_SERVER_URL + method).read()
    ret = json.loads(returned_json)
    return ret['Result']


def getDateTimeAsString(dt = datetime.datetime.utcnow(),
                        inTimezone = 'PST',
                        withStringFormat = '%D %T'):
    """ Return the current number of sessions on AllDayPlay

    This AJAX function will return just the current number
    of listening sessions on AllDayPlay.FM. This number is
    saved to the server every minute, so it doesn't make
    sense to retrieve this information more regularly than
    that.

    You must pass a datetime in the dt parameter if you
    want to convert a specific datetime. Otherwise it will
    default to the current datetime in utc time.

    You must pass the standard Python strftime formatting
    as a parameter in order to get the right string format.

    In order to deal with timezones, every date and time
    on the server is stored in UTC. This function assumes
    Pacific Standard Time, but the timezone can be changed.

    strftime formatting
    ===================
    %a - abbreviated weekday name
    %A - full weekday name
    %b - abbreviated month name
    %B - full month name
    %c - preferred date and time representation
    %C - century number (the year divided by 100, range 00 to 99)
    %d - day of the month (01 to 31)
    %D - same as %m/%d/%y
    %e - day of the month (1 to 31)
    %g - like %G, but without the century
    %G - 4-digit year corresponding to the ISO week number (see %V).
    %h - same as %b
    %H - hour, using a 24-hour clock (00 to 23)
    %I - hour, using a 12-hour clock (01 to 12)
    %j - day of the year (001 to 366)
    %m - month (01 to 12)
    %M - minute
    %n - newline character
    %p - either am or pm according to the given time value
    %r - time in a.m. and p.m. notation
    %R - time in 24 hour notation
    %S - second
    %t - tab character
    %T - current time, equal to %H:%M:%S
    %u - weekday as a number (1 to 7), Monday=1. Warning: In Sun Solaris Sunday=1
    %U - week number of the current year, starting with the first Sunday as the first day of the first week
    %V - The ISO 8601 week number of the current year (01 to 53), where week 1 is the first week that has at least 4 days in the current year, and with Monday as the first day of the week
    %W - week number of the current year, starting with the first Monday as the first day of the first week
    %w - day of the week as a decimal, Sunday=0
    %x - preferred date representation without the time
    %X - preferred time representation without the date
    %y - year without a century (range 00 to 99)
    %Y - year including the century
    %Z or %z - time zone or name or abbreviation
    %% - a literal % character
    """

    if type(dt) in [str, unicode]:
        #dt = datetime.datetime(*(time.strptime(dt[:-7].replace('T', ' '), '%Y-%m-%d %H:%M:%S')[0:6]))
        dt = datetime.datetime(*(time.strptime(dt.replace('T', ' '), '%Y-%m-%d %H:%M:%S')[0:6]))

    if inTimezone == 'PST':
        tz = timezone('US/Pacific')
    elif inTimezone == 'EST':
        tz = timezone('US/Eastern')

    # Create the time in the UTC timezone
    utc_time = (pytz.utc).localize(dt)

    # Convert to local time.
    local_time = utc_time.astimezone(tz)

    return local_time.strftime(withStringFormat)


