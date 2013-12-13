from flask import render_template, g, url_for, flash, redirect
from jinja2 import Template

import datetime
import forms, logging

class UserViews(object):
    """docstring for UserViews"""
    def __init__(self, request, yr_api, metrics_api):
        super(UserViews, self).__init__()
        self.request = request
        self.yr_api = yr_api
        self.metrics_api = metrics_api

        self.logger = logging.getLogger('yr_central')
        self.logger.info('[USER_VIEW] Instantiated with request and APIs.')

    def addPerson(self):
        """ The form for adding a new person to the database. """
        api = self.yr_api

        # Get the Add Person form from WTForms
        form = forms.AddStaffMember()

        # Get the supervisors from the API
        form.supervisor.choices = [("", "Supervisor")] + api.getPeople(type='staff', WTFormat=True)

        # Get the departments from the API
        form.department.choices = [("", "Department")] + api.getDepartments(WTFormat=True)

        # If the information has been validated, then go ahead to the,
        # success page.
        if form.validate_on_submit():
            add_person = api.serverRequest('/person/add', request_method='POST', data=form.data)

            if add_person['Status'] == "OK":
                flash(u"%s %s Added" % (form.first_name.data, form.last_name.data))
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

    def editPerson(self, _id):
        """ The form for editing a person in the database. """
        api = self.yr_api
        logger = self.logger

        # Get the Edit Person form from WTForms
        form = forms.EditStaffMember()

        # Get the supervisors from the API
        form.supervisor.choices = [("", "Supervisor")] + api.getPeople(type='staff', WTFormat=True)

        # Get the departments from the API
        form.department.choices = [("", "Department")] + api.getDepartments(WTFormat=True)

        # If the information has been validated, then go ahead to the
        # success page.
        if form.validate_on_submit():
            edit_person = api.serverRequest('/person/edit', request_method='POST', data=form.data)

            if edit_person['Status'] == "OK":
                flash(u"%s %s Edited" % (form.first_name.data, form.last_name.data))
                return redirect(url_for("user_staff_list"))
            else:
                flash(u'Houston, we have a problem: %s' % edit_person['Status'])

        # Flash the error messages if they exist.
        if form.errors:
            for field, error_list in form.errors.iteritems():
                for error in error_list:
                    flash(unicode(error))

        logger.info('[USER_VIEW] Editing person for _id [%s]' % (_id))

        api_person = api.getPerson(_id)

        logger.info('[USER_VIEW] Person for _id [%s] returned from API: %s' % (_id, str(api_person)))

        # Set the form data
        form.populateFormFields(obj=api_person)
        form.populateFormFields(obj=api_person['phone'], prefix='phone_')
        form.populateFormFields(obj=api_person['address'])
        form.populateFormFields(obj=api_person['emergency_contact'], prefix='emergency_contact_')
        form.populateFormFields(obj=api_person['emergency_contact']['phone'], prefix='emergency_contact_phone_')

        form.person_id.data = _id
        form.zipcode.data = api_person['address']['zip']

        return render_template("person_add.html",
                               user=g.user,
                               title="Edit Person",
                               form=form)


    def staffMembersList(self):
        """ The list of staff members. """
        metrics = self.metrics_api
        api = self.yr_api

        return render_template("people_list.html",
                               user=g.user, 
                               title="Staff Members",
                               people=api.getPeople(type='staff'))

