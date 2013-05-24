from flask import jsonify
from pytz import timezone

import datetime, time, pytz

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

class ADPMetricsViews(object):
    """docstring for ADPMetricsViews"""
    def __init__(self, request, yr_api, metrics_api):
        super(ADPMetricsViews, self).__init__()
        self.request = request
        self.yr_api = yr_api
        self.metrics_api = metrics_api

    def ajaxCurrentSessionTotals(self):
        """ Ajax function to return the current number of sessions.

        This function connects to the metrics server and returns the
        most recent number of listening sessions.
        """
        request = self.request
        metrics = self.metrics_api
        
        # Initialize variables.
        dt = request.args.get('dt') if request.args.get('dt') else datetime.datetime.utcnow()
        tzinfo = request.args.get('tz') if request.args.get('tz') else 'PST'
        strformat = request.args.get('strformat') if request.args.get('strformat') else '%I:%M<br>%p'

        # Perform the API request.
        ret = metrics.serverRequest('/ADP/SESSIONS/CURRENT/')

        ret['Date'] = getDateTimeAsString(dt = datetime.datetime.utcnow(),
                                          inTimezone = tzinfo,
                                          withStringFormat = '%I:%M<br>%p')

        return jsonify(ret)

    def ajaxOverallTotalListeningSessions(self):
        """ Ajax function to return the total number of sessions.

        This function connects to the metrics server and returns the
        total number of listening sessions.
        """
        metrics = self.metrics_api

        totalSessions = metrics.serverRequest('/ADP/SESSIONS/TOTAL')
        totalBounced = metrics.serverRequest('/ADP/SESSIONS/BOUNCED')

        ret = {
            '128K Shoutcast Server': {
                'Total': totalSessions['128K Shoutcast Server'],
                'Bounced': totalBounced['128K Shoutcast Server']
            },
            '56K Shoutcast Server': {
                'Total': totalSessions['56K Shoutcast Server'],
                'Bounced': totalBounced['56K Shoutcast Server']
            },
            'All': {
                'Total': totalSessions['Total'],
                'Bounced': totalBounced['Total']
            }
        }

        return jsonify(ret)

    def ajaxOverallUniqueListeners(self):
        """ Ajax function to return the total number of uniques.

        This function connects to the metrics server and returns the
        total number of unique users.
        """
        metrics = self.metrics_api

        ret = metrics.serverRequest('/ADP/LISTENER/TOTAL')

        return jsonify(ret)

    def ajaxListeningSessionsForThisHour(self):
        """ Ajax function to return the total listening sessions
        in the last hour.

        This functions connects to the metrics server and returns
        the total number of listening sessions that connected during
        this hour.
        """
        metrics = self.metrics_api

        ret = metrics.serverRequest('/ADP/SESSIONS/LAST1HOURS/')

        # Convert the date to the hour string.
        ret["Hour"] = getDateTimeAsString(dt = ret["date_list"][0], withStringFormat = '%I%p')

        return jsonify(ret)

    def ajaxListeningSessionsForToday(self):
        """ Ajax function to return the total listening sessions
        for today.

        This functions connects to the metrics server and returns
        the total number of listening sessions that connected today.
        """
        metrics = self.metrics_api

        ret = metrics.serverRequest('/ADP/SESSIONS/LAST1DAYS/')

        # Convert the date to the hour string.
        ret["Day"] = getDateTimeAsString(dt = ret["date_list"][0], withStringFormat = '%A')

        return jsonify(ret)

    def ajaxCurrentPlayingSong(self):
        """ Ajax function to return the currently playing song.

        This functions connects to the metrics server and returns
        the currently playing song.
        """
        metrics = self.metrics_api

        one_song = metrics.serverRequest("/ADP/SONGS/PLAYED/?limit=1")

        ret = {"song": one_song[0]}

        return jsonify(ret)

    def ajaxAvgSessionListeningTime(self):
        """ Ajax function to return the avergage session listening
        time in minutes.

        This function connects to the metrics server and returns
        the average session listening time for all streams.
        """
        metrics = self.metrics_api

        ret = metrics.serverRequest("/ADP/SESSIONS/AVGLISTENINGTIME/")

        return jsonify(ret)

    def ajaxTotalListenerHours(self):
        """ Ajax function to return the total listener hours
        in hours.

        This function connects to the metrics server and returns
        the total listener hours for all streams.
        """
        metrics = self.metrics_api

        ret = metrics.serverRequest("/ADP/LISTENER/HOURS/")

        return jsonify(ret)

    def ajaxAvgListeningSessionsPerUser(self):
        """ Ajax function to return the average listening
        sessions per user.

        This function connects to the metrics server and returns
        the average listening sessions per user.
        """
        ret = {}
        metrics = self.metrics_api

        ret["Total Listeners"] = float(metrics.serverRequest("/ADP/LISTENER/TOTAL/")["Total"])
        ret["Total Sessions"] = float(metrics.serverRequest("/ADP/SESSIONS/TOTAL/")["Total"])
        ret["Total Bounced"] = float(metrics.serverRequest("/ADP/SESSIONS/BOUNCED/")["Total"])
        ret["Result"] = float("%.2f" % round((ret["Total Sessions"] - ret["Total Bounced"]) / ret["Total Listeners"], 2))

        return jsonify(ret)

    def ajaxLastXminsOfSessions(self):
        """ Ajax function to get the total number of sessions
        per minute over the last X minutes.

        Given a number passed in via the MINS get variable,
        this method will return the number of sessions.
        """
        metrics = self.metrics_api
        request = self.request
        
        mins = request.args.get('mins')
        ltm = metrics.serverRequest("/ADP/SESSIONS/LAST" + str(mins) + "MINS/")
        ltm["date_list"] = handleDateList(ltm["date_list"], '%I:%M %p')

        return jsonify(ltm)

    def ajaxLastXhoursOfListeners(self):
        """ Ajax function to get the total number of listeners
        per hours over the last X hours.

        Given a number passed in via the HOURS get variable,
        this method will return the number of listeners.
        """
        request = self.request
        metrics = self.metrics_api
        
        hours = request.args.get('hours')
        ltm = metrics.serverRequest("/ADP/SESSIONS/LAST" + str(hours) + "HOURS/")
        ltm["date_list"] = handleDateList(ltm["date_list"], '%I%p')

        return jsonify(ltm)

    def ajaxLastXdaysOfListeners(self):
        """ Ajax function to get the total number of listeners
        per hours over the last X days.

        Given a number passed in via the DAYS get variable,
        this method will return the number of listeners.
        """
        request = self.request
        metrics = self.metrics_api
        
        days = request.args.get('days')
        ltm = metrics.serverRequest("/ADP/SESSIONS/LAST" + str(days) + "DAYS/")
        ltm["date_list"] = handleDateList(ltm["date_list"], '%A')

        return jsonify(ltm)

        