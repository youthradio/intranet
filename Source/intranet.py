from flask import Flask, g, request, render_template, jsonify, flash, redirect, url_for
from flask_googleauth import GoogleFederated
from jinja2 import Template

import urllib2, urllib, json, sys

import forms

from yrAPI import *
from metricsAPI import *
from views_metrics_adp import ADPMetricsViews
from views_finance import FinanceViews
from views_user import UserViews

# Setup Flask
app = Flask(__name__, instance_relative_config=True)
#app.config.from_object(__name__)
app.config.from_pyfile('intranet_cfg.py', silent=False)

# Setup Google Federated Auth
auth = GoogleFederated('youthradio.org', app)

# Set up the API objects
api = yrAPI(url=app.config['YR_API_SERVER_URL'])
metrics = MetricsAPI(url=app.config['METRICS_SERVER_URL'], request=request)

# Set up the URL views
adpMetricsView = ADPMetricsViews(request=request, yr_api=api, metrics_api=metrics)
financeView = FinanceViews(request=request, yr_api=api, metrics_api=metrics)
userView = UserViews(request=request, yr_api=api, metrics_api=metrics)

"""
Overall web page views
"""
app.add_url_rule('/', 'central_index', auth.required(adpMetricsView.metricsIndexPage), methods=["GET"])

"""
AllDayPlay Metrics Views
"""
# Main web pages for ADP Metrics
app.add_url_rule('/metrics/adp/', 'metrics_adp_index', auth.required(adpMetricsView.metricsIndexPage), methods=["GET"])

# ADP ajax methods
app.add_url_rule('/metrics/adp/_getCurrentSessionsTotal', 'ajax_currentSessionTotals', auth.required(adpMetricsView.ajaxCurrentSessionTotals), methods=["GET"])
app.add_url_rule('/metrics/adp/_getOverallTotalListeningSessions', 'ajax_overallTotalListeningSessions', auth.required(adpMetricsView.ajaxOverallTotalListeningSessions), methods=['GET'])
app.add_url_rule('/metrics/adp/_getOverallUniqueListeners', 'ajax_overallUniqueListeners', auth.required(adpMetricsView.ajaxOverallUniqueListeners), methods=['GET'])
app.add_url_rule('/metrics/adp/_getListeningSessionsForThisHour', 'ajax_listeningSessionsForThisHour', auth.required(adpMetricsView.ajaxListeningSessionsForThisHour), methods=['GET'])
app.add_url_rule('/metrics/adp/_getListeningSessionsForToday', 'ajax_listeningSessionsForToday', auth.required(adpMetricsView.ajaxListeningSessionsForToday), methods=['GET'])
app.add_url_rule('/metrics/adp/_getCurrentPlayingSong', 'ajax_currentPlayingSong', auth.required(adpMetricsView.ajaxCurrentPlayingSong), methods=['GET'])
app.add_url_rule('/metrics/adp/_getAvgSessionListeningTime', 'ajax_avgSessionListeningTime', auth.required(adpMetricsView.ajaxAvgSessionListeningTime), methods=['GET'])
app.add_url_rule('/metrics/adp/_getTotalListenerHours', 'ajax_totalListenerHours', auth.required(adpMetricsView.ajaxTotalListenerHours), methods=['GET'])
app.add_url_rule('/metrics/adp/_getAvgListeningSessionsPerUser', 'ajax_avgListeningSessionsPerUser', auth.required(adpMetricsView.ajaxAvgListeningSessionsPerUser), methods=['GET'])
app.add_url_rule('/metrics/adp/_getLastXminsOfSessions', 'ajax_lastXminsOfSessions', auth.required(adpMetricsView.ajaxLastXminsOfSessions), methods=['GET'])
app.add_url_rule('/metrics/adp/_getLastXhoursOfListeners', 'ajax_lastXhoursOfListeners', auth.required(adpMetricsView.ajaxLastXhoursOfListeners), methods=['GET'])
app.add_url_rule('/metrics/adp/_getLastXdaysOfListeners', 'ajax_lastXdaysOfListeners', auth.required(adpMetricsView.ajaxLastXdaysOfListeners), methods=['GET'])

"""
Finance views
"""
app.add_url_rule('/finance/category/add/', 'finance_category_add', auth.required(financeView.addPOCategory), methods=['GET', 'POST'])

"""
User Views
"""
app.add_url_rule('/person/add/', 'user_person_add', auth.required(userView.addPerson), methods=['GET', 'POST'])
app.add_url_rule('/staff/list/', 'user_staff_list', auth.required(userView.staffMembersList), methods=['GET'])

if __name__ == "__main__":
    app.debug = app.config["DEBUG"]

    if app.debug:
        app.run(host=app.config["HOST"], port=app.config["PORT"])
    else:
        app.run()