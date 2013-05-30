from flask import Flask, g, request, render_template, jsonify, flash, redirect, url_for
from flask_googleauth import GoogleFederated
from jinja2 import Template

import urllib2, urllib, json, sys

import forms

from yrAPI import *
from metricsAPI import *
from views_metrics_adp import ADPMetricsViews

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

"""
Set the AllDayPlay AJAX URL Rules
"""
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

@app.route("/")
@app.route("/metrics/adp")
@app.route("/metrics/adp/")
@auth.required
def metrics_adp():
    """ The metrics for All Day Play.

    This function returns the metrics screen for All Day Play.
    """
    # Once user is authenticated, his name and email are accessible as
    # g.user.name and g.user.email.
    #return "You have rights to be here, %s (%s): %r" % (g.user.name, g.user.email, g.user)


    lifetime = {
        "Total Songs Played": metrics.serverRequest("/adp/songs/total")
    }

    return render_template("adp_overall_metrics.html",
                           user=g.user, 
                           title="AllDayPlay Metrics",
                           songs=metrics.serverRequest("/adp/songs/played?limit=10"),
                           server_url=app.config["METRICS_SERVER_URL"],
                           lifetime_stats=lifetime)


@app.route("/person/add", methods=['GET', 'POST'])
@auth.required
def person_add():
    """ The form for adding a new person to the database. """

    # Get the Add Person form from WTForms
    form = forms.AddPerson()

    # If the information has been validated, then go ahead to the
    # success page.
    if form.validate_on_submit():
        flash(u"%s %s Added" % (form.first_name, form.last_name))
        return redirect(url_for("success"))

    # Flash the error messages if they exist.
    if form.errors:
        for field, error_list in form.errors.iteritems():
            for error in error_list:
                flash(unicode(error))

    return render_template("person_add.html",
                           user=g.user,
                           title="Add A New Person", 
                           form=form)

@app.route("/test", methods=['GET'])
@auth.required
def test():
    categories = [("None", "Choose Subcategory")] + api.getPurchaseOrderCategories(0, asTuples=True)
    template_success = Template(str(categories))
    return template_success.render()


@app.route("/finance/category/add", methods=['GET', 'POST'])
@auth.required
def finance_category_add():
    """ The form for adding a new Finance Category to the database. """

    # Get the Add Department form from WTForms
    form = forms.AddPOCategory()

    # Get the categories from the API
    form.category.choices = [("None", "Choose Category")] + api.getPurchaseOrderCategories(0, asTuples=True)

    # Get the subcategories from the API
    form.subcategory1.choices = [("None", "Choose Subcategory")] + api.getPurchaseOrderCategories(1, asTuples=True)

    # If the information has been validated, then go ahead to the
    # success page.
    if form.validate_on_submit():

        # Set the appropriate category names and such.
        if len(form.new_category.data.strip()) > 0:
            category = form.new_category.data
        elif form.category.data == "None":
            category = ""
        else:
            category = form.category.data

        if len(form.new_subcategory1.data.strip()) > 0:
            subcategory1 = form.new_subcategory.data
        elif form.subcategory1.data == "None":
            subcategory1 = ""
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
            form.category.choices = [("None", "Choose Category")] + api.getPurchaseOrderCategories(0, asTuples=True)
        if subcategory1:
            form.subcategory1.choices = [("None", "Choose Subcategory")] + api.getPurchaseOrderCategories(1, asTuples=True)


        # Clear out the data.
        form.category.data = None
        form.subcategory1.data = None
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




@app.route("/person/success")
@auth.required
def success():
    template_success = Template("""
    <html>
        <head><title>Success</title></head>
        <body>Success!</body>
    </html>
    """)
    return template_success.render()


if __name__ == "__main__":
    app.debug = app.config["DEBUG"]

    if app.debug:
        app.run(host=app.config["HOST"], port=app.config["PORT"])
    else:
        app.run()