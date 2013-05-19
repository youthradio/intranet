from flask import Flask, g, request, render_template, jsonify
from pytz import timezone

import datetime, time, pytz
import urllib2, urllib, json

from util_metrics import *

def ajax_currentSessionTotals():
    """ Ajax function to return the current number of sessions.

    This function connects to the metrics server and returns the
    most recent number of listening sessions.
    """
    # Initialize variables.
    dt = request.args.get('dt') if request.args.get('dt') else datetime.datetime.utcnow()
    tzinfo = request.args.get('tz') if request.args.get('tz') else 'PST'
    strformat = request.args.get('strformat') if request.args.get('strformat') else '%I:%M<br>%p'

    # Perform the API request.
    ret = metricsServerRequest('/ADP/SESSIONS/CURRENT/')

    ret['Date'] = getDateTimeAsString(dt = datetime.datetime.utcnow(),
                                      inTimezone = tzinfo,
                                      withStringFormat = '%I:%M<br>%p')

    return jsonify(ret)

def ajax_overallTotalListeningSessions():
    """ Ajax function to return the total number of sessions.

    This function connects to the metrics server and returns the
    total number of listening sessions.
    """
    totalSessions = metricsServerRequest('/ADP/SESSIONS/TOTAL')
    totalBounced = metricsServerRequest('/ADP/SESSIONS/BOUNCED')

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

def ajax_overallUniqueListeners():
    """ Ajax function to return the total number of uniques.

    This function connects to the metrics server and returns the
    total number of unique users.
    """
    ret = metricsServerRequest('/ADP/LISTENER/TOTAL')

    return jsonify(ret)

def ajax_listeningSessionsForThisHour():
    """ Ajax function to return the total listening sessions
    in the last hour.

    This functions connects to the metrics server and returns
    the total number of listening sessions that connected during
    this hour.
    """
    ret = metricsServerRequest('/ADP/SESSIONS/LAST1HOURS/')

    # Convert the date to the hour string.
    ret["Hour"] = getDateTimeAsString(dt = ret["date_list"][0], withStringFormat = '%I%p')

    return jsonify(ret)

def ajax_listeningSessionsForToday():
    """ Ajax function to return the total listening sessions
    for today.

    This functions connects to the metrics server and returns
    the total number of listening sessions that connected today.
    """
    ret = metricsServerRequest('/ADP/SESSIONS/LAST1DAYS/')

    # Convert the date to the hour string.
    ret["Day"] = getDateTimeAsString(dt = ret["date_list"][0], withStringFormat = '%A')

    return jsonify(ret)

def ajax_currentPlayingSong():
    """ Ajax function to return the currently playing song.

    This functions connects to the metrics server and returns
    the currently playing song.
    """
    one_song = metricsServerRequest("/ADP/SONGS/PLAYED/?limit=1")

    ret = {"song": one_song[0]}

    return jsonify(ret)

def ajax_avgSessionListeningTime():
    """ Ajax function to return the avergage session listening
    time in minutes.

    This function connects to the metrics server and returns
    the average session listening time for all streams.
    """
    ret = metricsServerRequest("/ADP/SESSIONS/AVGLISTENINGTIME/")

    return jsonify(ret)

def ajax_totalListenerHours():
    """ Ajax function to return the total listener hours
    in hours.

    This function connects to the metrics server and returns
    the total listener hours for all streams.
    """
    ret = metricsServerRequest("/ADP/LISTENER/HOURS/")

    return jsonify(ret)

def ajax_avgListeningSessionsPerUser():
    """ Ajax function to return the average listening
    sessions per user.

    This function connects to the metrics server and returns
    the average listening sessions per user.
    """
    ret = {}
    ret["Total Listeners"] = float(metricsServerRequest("/ADP/LISTENER/TOTAL/")["Total"])
    ret["Total Sessions"] = float(metricsServerRequest("/ADP/SESSIONS/TOTAL/")["Total"])
    ret["Total Bounced"] = float(metricsServerRequest("/ADP/SESSIONS/BOUNCED/")["Total"])
    ret["Result"] = float("%.2f" % round((ret["Total Sessions"] - ret["Total Bounced"]) / ret["Total Listeners"], 2))

    return jsonify(ret)

def ajax_lastXminsOfSessions():
    """ Ajax function to get the total number of sessions
    per minute over the last X minutes.

    Given a number passed in via the MINS get variable,
    this method will return the number of sessions.
    """
    mins = request.args.get('mins')
    ltm = metricsServerRequest("/ADP/SESSIONS/LAST" + str(mins) + "MINS/")
    ltm["date_list"] = handleDateList(ltm["date_list"], '%I:%M %p')

    return jsonify(ltm)

def ajax_lastXhoursOfListeners():
    """ Ajax function to get the total number of listeners
    per hours over the last X hours.

    Given a number passed in via the HOURS get variable,
    this method will return the number of listeners.
    """
    hours = request.args.get('hours')
    ltm = metricsServerRequest("/ADP/SESSIONS/LAST" + str(hours) + "HOURS/")
    ltm["date_list"] = handleDateList(ltm["date_list"], '%I%p')

    return jsonify(ltm)

def ajax_lastXdaysOfListeners():
    """ Ajax function to get the total number of listeners
    per hours over the last X days.

    Given a number passed in via the DAYS get variable,
    this method will return the number of listeners.
    """
    days = request.args.get('days')
    ltm = metricsServerRequest("/ADP/SESSIONS/LAST" + str(days) + "DAYS/")
    ltm["date_list"] = handleDateList(ltm["date_list"], '%A')

    return jsonify(ltm)


