from flask import render_template, g, url_for, flash, redirect
from jinja2 import Template

import datetime
import forms, logging
import json

from yrEmail import mail
from yrGetTitle import getPageTitle

class NewsroomViews(object):
    """docstring for NewsroomViews"""
    def __init__(self, request, yr_api, metrics_api):
        super(NewsroomViews, self).__init__()
        self.request = request
        self.yr_api = yr_api
        self.metrics_api = metrics_api

        self.logger = logging.getLogger('yr_central')
        self.logger.info('[NEWSROOM_VIEW] Instantiated with request and APIs.')

        self.gmail_user = ''
        self.gmail_pass = ''
        self.debug = True

    def setDebug(self, debug):
        self.debug = debug

        return self.debug

    def setGmailUsernameAndPassword(self, user, password):
        self.gmail_user = user
        self.gmail_pass = password

        return True

    def dailyListForm(self):
        return render_template('daily_list_form.html', user=g.user, title="Rebecca's Daily List")

    def dailyListPreview(self, isPreview=True):
        request = self.request

        if isPreview:
            replacedFormValues = dict(request.form)
            for key, value in request.form.iteritems():
                replacedFormValues[key] = value.replace('\n', '<br \>')
        else:
            replacedFormValues = request.form

        return render_template('daily_list_response.html', 
                               user=g.user,
                               title="Preview The Daily List",
                               form=replacedFormValues, 
                               current_date=getFormattedDate(), 
                               preview=isPreview)

    def dailyListSubmission(self):
        if self.debug:
            mail(["asha@youthradio.org", "kurt@youthradio.org"], "[DEVELOPMENT] The Daily List - " + getFormattedDate(), self.dailyListPreview(isPreview=False), self.gmail_user, self.gmail_pass)
        else:
            #mail(["asha@youthradio.org", "kurt@youthradio.org"], "The Daily List", self.dailyListPreview(isPreview=False), self.gmail_user, self.gmail_pass)
            mail(["newsroom@youthradio.org", "development@youthradio.org"], "The Daily List - " + getFormattedDate(), self.dailyListPreview(isPreview=False), self.gmail_user, self.gmail_pass)
        return self.dailyListPreview(isPreview=False)

    def ajaxDailyListGetTitle(self):
        request = self.request

        url = request.args.get('url')
        try:
            title = getPageTitle(url)
        except Exception, e:
            title = "DLError: " + unicode(e)

        response = {
            "url":      url,
            "title":    title
        }
        return json.dumps(response)

    def ajaxDailyListAutoSave(self):
        request = self.request
        api = self.yr_api

        key = request.form["key"]
        value = request.form["value"]

        data = {
            "key": key,
            "value": value
        }

        self.logger.info("[NEWSROOM_VIEW] Ajax DL Autosave saving: %s - %s" % (key, value))
        response = api.serverRequest('/utilities/saveKeyValue', request_method='PUT', data=data)

        return json.dumps(response)

def getFormattedDate():
        now = datetime.datetime.now()

        current_year = now.year
        current_month = now.month
        current_day = now.day

        return str(now.month) + "/" + str(now.day) + "/" + str(now.year)