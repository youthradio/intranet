from flask import render_template, g, url_for, flash

import forms

class FinanceViews(object):
    """docstring for FinanceViews"""
    def __init__(self, request, yr_api, metrics_api):
        super(FinanceViews, self).__init__()
        self.request = request
        self.yr_api = yr_api
        self.metrics_api = metrics_api

    def addPOCategory(self):
        """ The form for adding a new Finance Category to the database. """
        api = self.yr_api

        # Get the Add POCategory form from WTForms
        form = forms.AddPOCategory()

        # Get the categories from the API
        form.category.choices = [("", "Choose Category")] + api.getPurchaseOrderCategories(0, asTuples=True)

        # Get the subcategories from the API
        form.subcategory1.choices = [("", "Choose Subcategory")] + api.getPurchaseOrderCategories(1, asTuples=True)

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
            api.serverRequest("/finance/cat/add", POCategory)

            # Flash a message saying this has been added.
            flash(u"%s >> %s >> %s Added" % (category, subcategory1, subcategory2))

            # If there's a new category, then refresh the choices.
            if category:
                form.category.choices = [("", "Choose Category")] + api.getPurchaseOrderCategories(0, asTuples=True)
            if subcategory1:
                form.subcategory1.choices = [("", "Choose Subcategory")] + api.getPurchaseOrderCategories(1, asTuples=True)


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

