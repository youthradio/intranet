from flask import Flask, g, request, render_template, jsonify
from flask_googleauth import GoogleFederated
from mongokit import Connection, Document, IS, OR, MultipleResultsFound, ObjectId, Collection
from validate_email import validate_email
from pytz import timezone

import datetime, time, pytz
import re
import urllib2, urllib, json

# Constants
YMI_APP_RACE = ['Hispanic/Latino', 
                'African American', 
                'Asian American', 
                'Caucasian', 
                'Middle Eastern',
                'Pacific Islander',
                'Native American/Alaskan Native',
                'Decline to State']


# Setup Flask
app = Flask(__name__, instance_relative_config=True)
#app.config.from_object(__name__)
app.config.from_pyfile('intranet.cfg', silent=False)

# Setup Google Federated Auth
auth = GoogleFederated("youthradio.org", app)


# Connect to the database
db = Connection(app.config["MONGODB_HOST"], app.config["MONGODB_PORT"])


# Needed functions
def jsonDefaultHandler(obj):
    # TODO: Add a handler for bson.objectid.ObjectId
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    elif isinstance(obj, datetime.datetime):
        return datetime.datetime
    else:
        return str(obj)
        #raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj))

def metricsServerRequest(url):
    returned_json = urllib2.urlopen(app.config["METRICS_SERVER_URL"] + url).read()
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


# Validator functions
def email_validator(email):
    return validate_email(email)


# Mongo Schema
@db.register
class RootDocument(Document):
    """Foundation class for MongoKit usage."""
    use_dot_notation = True
    use_autorefs = True
    skip_validation = False

    __database__ = "YMI"

    structure = {
        "enabled": bool,
        "date_created": datetime.datetime,
        "date_modified": datetime.datetime
    }
    default_values = {
        "enabled": True,
        "date_created": datetime.datetime.utcnow()
    }

    def save(self):
        self['date_modified'] = datetime.datetime.utcnow()
        return super(RootDocument, self).save()


@db.register
class Person(RootDocument):
    __collection__ = "People"
    structure = {
        "email": basestring,
        "first_name": unicode,
        "middle_initial": unicode,
        "last_name": unicode,
        "gender": IS(u'M', u'F', u'MTF', u'FTM'),
        "phone": {
            "home": basestring,
            "cell": basestring
        },
        "address": {
            "street_address_1": unicode,
            "street_address_2": unicode,
            "city": unicode,
            "state": unicode,
            "zip": unicode
        }
    }
    validators = {
        "email": email_validator
    }
    required_fields = ["email"]

    def __repr__(self):
        return "<Person %r>" % (self._id)

@db.register
class Participant(Person):
    structure = {
        "dob": datetime.datetime,
        "language": list,
        "english_fluency": IS(u'Fluent', u'Somewhat Fluent', u'Not Fluent'),
        "race": OR(list, basestring),
        "household_income": IS(u'<15k', u'15k-30k', u'30k-60k', u'60k-80k', u'>80k'),
        "dependency_status": IS(u'Both Parents', u'Legal Guardian', u'Friend', u'Single Parent', u'Foster Parent', u'Grandparents', u'Relatives', u'Boyfriend/Girlfriend'),
        "people_in_household": int,
        "guardian_education_1": IS(u'Middle School', u'High School', u'GED', u'AA/Certification', u'BA/BS', u'MA/MS', u'PhD', u'Unknown'),
        "guardian_education_2": IS(u'Middle School', u'High School', u'GED', u'AA/Certification', u'BA/BS', u'MA/MS', u'PhD', u'Unknown'),
        "internet_access": basestring,
        "referal_source": basestring
    }
    validators = {
        "language": lambda x: x > 0
    }

    def __repr__(self):
        return "<Particpant %r>" % (self._id)


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


@app.route("/_getCurrentSessionsTotal", methods=["GET"])
@auth.required
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

@app.route('/_getOverallTotalListeningSessions', methods=['GET'])
@auth.required
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


@app.route('/_getOverallUniqueListeners', methods=['GET'])
@auth.required
def ajax_overallUniqueListeners():
    """ Ajax function to return the total number of uniques.

    This function connects to the metrics server and returns the
    total number of unique users.
    """
    ret = metricsServerRequest('/ADP/LISTENER/TOTAL')

    return jsonify(ret)


@app.route('/_getListeningSessionsForThisHour', methods=['GET'])
@auth.required
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


@app.route('/_getListeningSessionsForToday', methods=['GET'])
@auth.required
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


@app.route('/_getCurrentPlayingSong', methods=['GET'])
@auth.required
def ajax_currentPlayingSong():
    """ Ajax function to return the currently playing song.

    This functions connects to the metrics server and returns
    the currently playing song.
    """
    one_song = metricsServerRequest("/ADP/SONGS/PLAYED/?limit=1")

    ret = {"song": one_song[0]}

    return jsonify(ret)


@app.route('/_getAvgSessionListeningTime', methods=['GET'])
@auth.required
def ajax_avgSessionListeningTime():
    """ Ajax function to return the avergage session listening
    time in minutes.

    This function connects to the metrics server and returns
    the average session listening time for all streams.
    """
    ret = metricsServerRequest("/ADP/SESSIONS/AVGLISTENINGTIME/")

    return jsonify(ret)


@app.route('/_getTotalListenerHours', methods=['GET'])
@auth.required
def ajax_totalListenerHours():
    """ Ajax function to return the total listener hours
    in hours.

    This function connects to the metrics server and returns
    the total listener hours for all streams.
    """
    ret = metricsServerRequest("/ADP/LISTENER/HOURS/")

    return jsonify(ret)

@app.route('/_getAvgListeningSessionsPerUser', methods=['GET'])
@auth.required
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

@app.route('/_getLastXminsOfSessions', methods=['GET'])
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

@app.route('/_getLastXhoursOfListeners', methods=['GET'])
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

@app.route('/_getLastXdaysOfListeners', methods=['GET'])
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


@app.route("/")
@app.route("/metrics/adp")
@app.route("/metrics/adp/")
@auth.required
def metrics_ADP():
    """ The metrics for All Day Play.

    This function returns the metrics screen for All Day Play.
    """
    # Once user is authenticated, his name and email are accessible as
    # g.user.name and g.user.email.
    #return "You have rights to be here, %s (%s): %r" % (g.user.name, g.user.email, g.user)


    lifetime = {
        "Total Songs Played": metricsServerRequest("/ADP/SONGS/TOTAL/")
    }

    return render_template("index.html", 
                           user = g.user,
                           title="Youth Radio Central",
                           songs=metricsServerRequest("/ADP/SONGS/PLAYED/?limit=10"),
                           server_url=app.config["METRICS_SERVER_URL"],
                           lifetime_stats=lifetime)

if __name__ == "__main__":
    app.debug = app.config["DEBUG"]
    
    if app.debug:
        app.run(host=app.config["HOST"], port=app.config["PORT"])
    else:
        app.run()