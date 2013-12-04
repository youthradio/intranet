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

    def dailyListForm(self):
        return render_template('daily_list_form.html', user=g.user, title="Rebecca's Daily List")

    def dailyListPreview(self, isPreview=True):
        now = datetime.datetime.now()
        request = self.request

        current_year = now.year
        current_month = now.month
        current_day = now.day

        todaydate = str(now.month) + "/" + str(now.day) + "/" + str(now.year)

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
                               current_date=todaydate, 
                               preview=isPreview)

    def dailyListSubmission(self):
        #mail(["newsroom@youthradio.org", "development@youthradio.org"], "The Daily List", self.dailyListPreview(isPreview=False))
        mail(["asha@youthradio.org", "kurt@youthradio.org"], "The Daily List", self.dailyListPreview(isPreview=False))
        return self.dailyListPreview(isPreview=False)

    def ajaxDailyListGetTitle(self):
        request = self.request

        url = request.args.get('url')
        title = getPageTitle(url)

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
