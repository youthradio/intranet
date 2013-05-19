from flask import Flask, g, request, render_template, jsonify
from flask_googleauth import GoogleFederated
from pytz import timezone

import urllib2, urllib, json
import sys

from util_metrics import *
from ajax_adp_metrics import *

# Setup Flask
app = Flask(__name__, instance_relative_config=True)
#app.config.from_object(__name__)
app.config.from_pyfile('intranet_cfg.py', silent=False)

# Setup Google Federated Auth
auth = GoogleFederated("youthradio.org", app)

# Needed functions
def jsonDefaultHandler(obj):
    """ Returns a properly formatted JSON Object.
    """
    # TODO: Add a handler for bson.objectid.ObjectId
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    elif isinstance(obj, datetime.datetime):
        return datetime.datetime
    else:
        return str(obj)
        #raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj))


"""
Set the AllDayPlay AJAX URL Rules
"""
app.add_url_rule('/_getCurrentSessionsTotal', 'ajax_currentSessionTotals', auth.required(ajax_currentSessionTotals), methods=["GET"])
app.add_url_rule('/_getOverallTotalListeningSessions', 'ajax_overallTotalListeningSessions', auth.required(ajax_overallTotalListeningSessions), methods=['GET'])
app.add_url_rule('/_getOverallUniqueListeners', 'ajax_overallUniqueListeners', auth.required(ajax_overallUniqueListeners), methods=['GET'])
app.add_url_rule('/_getListeningSessionsForThisHour', 'ajax_listeningSessionsForThisHour', auth.required(ajax_listeningSessionsForThisHour), methods=['GET'])
app.add_url_rule('/_getListeningSessionsForToday', 'ajax_listeningSessionsForToday', auth.required(ajax_listeningSessionsForToday), methods=['GET'])
app.add_url_rule('/_getCurrentPlayingSong', 'ajax_currentPlayingSong', auth.required(ajax_currentPlayingSong), methods=['GET'])
app.add_url_rule('/_getAvgSessionListeningTime', 'ajax_avgSessionListeningTime', auth.required(ajax_avgSessionListeningTime), methods=['GET'])
app.add_url_rule('/_getTotalListenerHours', 'ajax_totalListenerHours', auth.required(ajax_totalListenerHours), methods=['GET'])
app.add_url_rule('/_getAvgListeningSessionsPerUser', 'ajax_avgListeningSessionsPerUser', auth.required(ajax_avgListeningSessionsPerUser), methods=['GET'])
app.add_url_rule('/_getLastXminsOfSessions', 'ajax_lastXminsOfSessions', auth.required(ajax_lastXminsOfSessions), methods=['GET'])
app.add_url_rule('/_getLastXhoursOfListeners', 'ajax_lastXhoursOfListeners', auth.required(ajax_lastXhoursOfListeners), methods=['GET'])
app.add_url_rule('/_getLastXdaysOfListeners', 'ajax_lastXdaysOfListeners', auth.required(ajax_lastXdaysOfListeners), methods=['GET'])

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

    return render_template("adp_overall_metrics.html",
                           user=g.user, 
                           title="AllDayPlay Metrics",
                           songs=metricsServerRequest("/ADP/SONGS/PLAYED/?limit=10"),
                           server_url=app.config["METRICS_SERVER_URL"],
                           lifetime_stats=lifetime)


if __name__ == "__main__":
    app.debug = app.config["DEBUG"]

    if app.debug:
        app.run(host=app.config["HOST"], port=app.config["PORT"])
    else:
        app.run()