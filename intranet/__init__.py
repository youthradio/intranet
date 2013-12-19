from flask import Flask, g, request, render_template, jsonify, flash, redirect, url_for
from flask_googleauth import GoogleFederated
from jinja2 import Template

import urllib2, urllib, json, sys
import logging
import smtplib

import forms

from yrAPI import *
from metricsAPI import *
from views_metrics_adp import ADPMetricsViews
from views_finance import FinanceViews
from views_user import UserViews
from views_newsroom import NewsroomViews
from views_central import CentralViews

# Setup Flask
app = Flask(__name__, instance_relative_config=True)
#app.config.from_object(__name__)
app.config.from_pyfile('instance/intranet_cfg.py', silent=False)
app.config.from_envvar('INTRANET_CONFIG_FILE', silent=False)

# Set up Jinja Templating stuff
app.jinja_env.globals['css'] = (lambda filepath: url_for('static', filename='css/'+filepath))
app.jinja_env.globals['js'] = (lambda filepath: url_for('static', filename='js/'+filepath))
app.jinja_env.globals['img'] = (lambda filepath: url_for('static', filename='img/'+filepath))

# Set up logging
logger = logging.getLogger('yr_central')
logger.setLevel(eval(app.config['LOG_LEVEL']) if app.config['LOG_LEVEL'] else logging.DEBUG)

# create file handler which logs even debug messages
fh = logging.FileHandler(app.config['LOG_FILE'] if app.config['LOG_FILE'] else app.config['/tmp/yr_central.log'])
fh.setLevel(logging.INFO)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(fh)

# Setup Google Federated Auth
auth = GoogleFederated('youthradio.org', app)

# Set up the API objects
api = yrAPI(url=app.config['YR_API_SERVER_URL'])
metrics = MetricsAPI(url=app.config['METRICS_SERVER_URL'], request=request)
logger.info('[API] All APIs registered.')

# Set up the URL views
centralView = CentralViews(request=request, yr_api=api, metrics_api=metrics)
adpMetricsView = ADPMetricsViews(request=request, yr_api=api, metrics_api=metrics)
financeView = FinanceViews(request=request, yr_api=api, metrics_api=metrics)
userView = UserViews(request=request, yr_api=api, metrics_api=metrics)
newsroomView = NewsroomViews(request=request, yr_api=api, metrics_api=metrics)

# Set up the options for the URL views
newsroomView.setDebug(app.config['DEBUG'])
newsroomView.setGmailUsernameAndPassword(app.config['GMAIL_USER'], app.config['GMAIL_PASSWORD'])

logger.info('[FLASK] All Flask view objects instantiated.')

"""
Overall web page views
"""
app.add_url_rule('/', 'central_index', auth.required(centralView.homePage), methods=["GET"])

logger.info('[FLASK] All overall web page URL rules added.')


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

logger.info('[FLASK] All ADP metrics URL rules added.')

"""
Finance views
"""
app.add_url_rule('/finance/category/add/', 'finance_category_add', auth.required(financeView.addPOCategory), methods=['GET', 'POST'])
app.add_url_rule('/finance/dept/add/', 'finance_department_add', auth.required(financeView.addDepartment), methods=['GET', 'POST'])
app.add_url_rule('/finance/dept/edit/<_id>', 'finance_department_edit', auth.required(lambda _id: financeView.addDepartment(_id)), methods=['GET', 'POST'])
app.add_url_rule('/finance/dept/list/', 'finance_department_list', auth.required(financeView.listDepartments), methods=['GET'])

logger.info('[FLASK] All Finance URL rules added.')

"""
User Views
"""
app.add_url_rule('/person/add/', 'user_person_add', auth.required(userView.addPerson), methods=['GET', 'POST'])
app.add_url_rule('/person/edit/<_id>', 'user_person_edit', auth.required(lambda _id: userView.editPerson(_id)), methods=['GET', 'POST'])
app.add_url_rule('/staff/list/', 'user_staff_list', auth.required(userView.staffMembersList), methods=['GET'])

"""
Newsroom Views
"""
app.add_url_rule('/newsroom/dl/', 'newsroom_dailylist_home', auth.required(newsroomView.dailyListForm), methods=['GET'])
app.add_url_rule('/newsroom/dl/preview/', 'newsroom_dailylist_preview', auth.required(newsroomView.dailyListPreview), methods=['POST'])
app.add_url_rule('/newsroom/dl/submit/', 'newsroom_dailylist_submit', auth.required(newsroomView.dailyListSubmission), methods=['POST'])

"""
Newsroom AJAX
"""
app.add_url_rule('/_getPageTitleForDailyList', 'ajax_getPageTitleForDailyList', auth.required(newsroomView.ajaxDailyListGetTitle), methods=['GET'])
app.add_url_rule('/_autoSaveForDailyList', 'ajax_autoSaveForDailyList', newsroomView.ajaxDailyListAutoSave, methods=['PUT'])

logger.info('[FLASK] All User URL rules added.')

if __name__ == "__main__":
    app.debug = app.config["DEBUG"]
    logger.info('Youth Radio Central server started. HOST: %s:%i' % (app.config["HOST"], app.config["PORT"]) )

    if app.debug:
        app.run(host=app.config["HOST"], port=app.config["PORT"])
    else:
        app.run()