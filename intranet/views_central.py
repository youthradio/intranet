from flask import render_template, g, url_for, flash, redirect
from jinja2 import Template

import datetime
import forms, logging
import json

class CentralViews(object):
    """docstring for CentralViews"""
    def __init__(self, request, yr_api, metrics_api):
        super(CentralViews, self).__init__()
        self.request = request
        self.yr_api = yr_api
        self.metrics_api = metrics_api

        self.logger = logging.getLogger('yr_central')
        self.logger.info('[CENTRAL_VIEW] Instantiated with request and APIs.')

    def homePage(self):
        return render_template('yr_central.html', user=g.user, title="Welcome!")

