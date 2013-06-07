from flask import render_template, g, url_for, flash, redirect
from jinja2 import Template

import forms

class UserViews(object):
    """docstring for UserViews"""
    def __init__(self, request, yr_api, metrics_api):
        super(UserViews, self).__init__()
        self.request = request
        self.yr_api = yr_api
        self.metrics_api = metrics_api

    def addPerson(self):
        """ The form for adding a new person to the database. """
        api = self.yr_api

        # Get the Add Person form from WTForms
        form = forms.AddPerson()

        # Get the supervisors from the API
        form.supervisor.choices = [("", "Supervisor")] + api.getPeople(type='staff', WTFormat=True)

        # If the information has been validated, then go ahead to the
        # success page.
        if form.validate_on_submit():
            add_person = api.serverRequest('/person/add', request_method='POST', data=form.data)

            if add_person['Status'] == "OK":
                flash(u"%s %s Added<br />" % (form.first_name.data, form.last_name.data))
                return redirect(url_for("user_staff_list"))
            else:
                flash(u'Houston, we have a problem: %s' % add_person['Status'])

        # Flash the error messages if they exist.
        if form.errors:
            for field, error_list in form.errors.iteritems():
                for error in error_list:
                    flash(unicode(error))

        return render_template("person_add.html",
                               user=g.user,
                               title="Add A New Person", 
                               form=form)

    def staffMembersList(self):
        """ The list of staff members. """
        metrics = self.metrics_api
        api = self.yr_api

        return render_template("people_list.html",
                               user=g.user, 
                               title="Staff Members",
                               people=api.getPeople(type='staff'))

