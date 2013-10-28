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
        return render_template('daily_list_form.html')

    def dailyListSubmission(self):
        now = datetime.now()

        current_year = now.year
        current_month = now.month
        current_day = now.day

        todaydate = str(now.month) + "/" + str(now.day) + "/" + str(now.year)

        mail("applab@youthradio.org", "The Daily List", render_template('daily_list_response.html', form=request.form , current_date = todaydate ))
        return render_template('daily_list_response.html', form=request.form, current_date = todaydate )

    def ajaxDailyListGetTitle(self):
        request = self.request

        url = request.args.get('url')
        title = getPageTitle(url)

        response = {
            "url":      url,
            "title":    title
        }
        return json.dumps(response)
