from flask import render_template, g, url_for, flash

import logging

import forms

class FinanceViews(object):
    """docstring for FinanceViews"""
    def __init__(self, request, yr_api, metrics_api):
        super(FinanceViews, self).__init__()
        self.request = request
        self.yr_api = yr_api
        self.metrics_api = metrics_api

        self.logger = logging.getLogger('yr_central')
        self.logger.info('[FINANCE_VIEW] Instantiated with API and Metrics.')

    def addPOCategory(self):
        """ The form for adding a new Finance Category to the database. """
        api = self.yr_api

        # Get the Add POCategory form from WTForms
        form = forms.AddPOCategory()

        # Get the categories from the API
        form.category.choices = [("", "Choose Category")] + api.getPurchaseOrderCategories(0, WTForms=True)

        # Get the subcategories from the API
        form.subcategory1.choices = [("", "Choose Subcategory")] + api.getPurchaseOrderCategories(1, WTForms=True)

        # If the information has been validated, then go ahead to the
        # success page.
        if form.validate_on_submit():

            # Set the appropriate category names and such.
            if len(form.new_category.data.strip()) > 0:
                category = form.new_category.data
            else:
                category = form.category.data

            if len(form.new_subcategory1.data.strip()) > 0:
                subcategory1 = form.new_subcategory1.data
            else:
                subcategory1 = form.subcategory1.data

            subcategory2 = form.new_subcategory2.data.strip() if len(form.new_subcategory2.data.strip()) > 0 else ""

            # Create the object that's going to be submitted.
            POCategory = {
                "category": category,
                "subcategory1": subcategory1,
                "subcategory2": subcategory2
            }

            # Post to the API.
            api_response = api.serverRequest("/admin/cat/add", POCategory)

            # Flash a message saying this has been added.
            if api_response['Status'] == 'OK':
                flash(u"%s >> %s >> %s Added" % (category, subcategory1, subcategory2))
            else:
                flash(u'There was an error: %s' % api_response['Status'])

            # If there's a new category, then refresh the choices.
            if category:
                form.category.choices = [("", "Choose Category")] + api.getPurchaseOrderCategories(0, WTForms=True)
            if subcategory1:
                form.subcategory1.choices = [("", "Choose Subcategory")] + api.getPurchaseOrderCategories(1, WTForms=True)


            # Clear out the data.
            form.category.data = None
            form.subcategory1.data = None
            form.new_category.data = None
            form.new_subcategory1.data = None
            form.new_subcategory2.data = None

        # Flash the error messages if they exist.
        if form.errors:
            for field, error_list in form.errors.iteritems():
                for error in error_list:
                    flash(unicode(error))

        return render_template("finance_category_add.html",
                               user=g.user,
                               title="Add A Purchase Order Category", 
                               form=form)

    def addDepartment(self, _id=None):
        """ This form is used to add departments to the organization. """
        api = self.yr_api
        logger = self.logger

        # Get the form from WTForms
        form = forms.EditDepartment() if _id else forms.AddDepartment()

        if form.validate_on_submit():
            dept = {'name': form.name.data} if not _id else {'name': form.name.data, 'dept_id': _id}

            # Post to the API.
            
            api_response = api.serverRequest("/admin/dept/add", request_method='POST', data=dept)

            if api_response['Status'] == 'OK':
                flash(u"%s Added" % (form.name.data))
                form.name.data = None
            else:
                flash(u'There was an error: %s' % api_response['Status'])

        # Flash the error messages if they exist.
        if form.errors:
            for field, error_list in form.errors.iteritems():
                for error in error_list:
                    flash(unicode(error))

        # If there's an ID passed in, then this is an edit operation.
        if _id:

            logger.info('[FINANCE_VIEW] Editing a department for _id [%s]' % (_id))

            api_dept = api.getDepartment(_id)

            logger.info('[FINANCE_VIEW] Department for _id [%s] returned from API: %s' % (_id, str(api_dept)))

            # Set the form data
            form.name.data = api_dept['dept_name']
            form.dept_id.data = _id

        return render_template("finance_department_add.html",
                               user=g.user,
                               title="Add A Department", 
                               form=form)

    def listDepartments(self):
        """ The list of departments. """
        metrics = self.metrics_api
        api = self.yr_api

        return render_template("department_list.html",
                               user=g.user, 
                               title="Departments",
                               departments=api.getDepartments())

