from flask import Flask, g, request, render_template
from flask_googleauth import GoogleFederated
from mongokit import Connection, Document, IS, OR, MultipleResultsFound, ObjectId, Collection
from validate_email import validate_email

import datetime
import re
import urllib2, urllib, json

# Constants
YMI_APP_RACE = ['Hispanic/Latino', 
                'African American', 
                'Asian American', 
                'Caucasian', 
                'Middle Eastern',
                'Pacific Islander',
                'Native American/Alaskan Native',
                'Decline to State']


# Setup Flask
app = Flask(__name__, instance_relative_config=True)
#app.config.from_object(__name__)
app.config.from_pyfile('intranet.cfg', silent=False)

# Setup Google Federated Auth
auth = GoogleFederated("youthradio.org", app)


# Connect to the database
db = Connection(app.config["MONGODB_HOST"], app.config["MONGODB_PORT"])


# Needed functions
def jsonDefaultHandler(obj):
    # TODO: Add a handler for bson.objectid.ObjectId
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    elif isinstance(obj, datetime.datetime):
        return datetime.datetime
    else:
        return str(obj)
        #raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj))


# Metrics server functions
def metricsServerRequest(url):
    returned_json = urllib2.urlopen(app.config["METRICS_SERVER_URL"] + url).read()
    ret = json.loads(returned_json)
    return ret['Result']


# Validator functions
def email_validator(email):
    return validate_email(email)


# Mongo Schema
@db.register
class RootDocument(Document):
    """Foundation class for MongoKit usage."""
    use_dot_notation = True
    use_autorefs = True
    skip_validation = False

    __database__ = "YMI"

    structure = {
        "enabled": bool,
        "date_created": datetime.datetime,
        "date_modified": datetime.datetime
    }
    default_values = {
        "enabled": True,
        "date_created": datetime.datetime.utcnow()
    }

    def save(self):
        self['date_modified'] = datetime.datetime.utcnow()
        return super(RootDocument, self).save()


@db.register
class Person(RootDocument):
    __collection__ = "People"
    structure = {
        "email": basestring,
        "first_name": unicode,
        "middle_initial": unicode,
        "last_name": unicode,
        "gender": IS(u'M', u'F', u'MTF', u'FTM'),
        "phone": {
            "home": basestring,
            "cell": basestring
        },
        "address": {
            "street_address_1": unicode,
            "street_address_2": unicode,
            "city": unicode,
            "state": unicode,
            "zip": unicode
        }
    }
    validators = {
        "email": email_validator
    }
    required_fields = ["email"]

    def __repr__(self):
        return "<Person %r>" % (self._id)

@db.register
class Participant(Person):
    structure = {
        "dob": datetime.datetime,
        "language": list,
        "english_fluency": IS(u'Fluent', u'Somewhat Fluent', u'Not Fluent'),
        "race": OR(list, basestring),
        "household_income": IS(u'<15k', u'15k-30k', u'30k-60k', u'60k-80k', u'>80k'),
        "dependency_status": IS(u'Both Parents', u'Legal Guardian', u'Friend', u'Single Parent', u'Foster Parent', u'Grandparents', u'Relatives', u'Boyfriend/Girlfriend'),
        "people_in_household": int,
        "guardian_education_1": IS(u'Middle School', u'High School', u'GED', u'AA/Certification', u'BA/BS', u'MA/MS', u'PhD', u'Unknown'),
        "guardian_education_2": IS(u'Middle School', u'High School', u'GED', u'AA/Certification', u'BA/BS', u'MA/MS', u'PhD', u'Unknown'),
        "internet_access": basestring,
        "referal_source": basestring
    }
    validators = {
        "language": lambda x: x > 0
    }

    def __repr__(self):
        return "<Particpant %r>" % (self._id)




@app.route("/")
@auth.required
def secret():
    # Once user is authenticated, his name and email are accessible as
    # g.user.name and g.user.email.
    #return "You have rights to be here, %s (%s): %r" % (g.user.name, g.user.email, g.user)
    ltm = metricsServerRequest("/ADP/SESSIONS/LAST30MINS/")
    dl = []

    for d in ltm["date_list"]:
        #dl.append(d.replace(u'\u2019', '').encode("ascii", "ignore"))
        dl.append(str(d).replace('T', ' ')[:-7] + " GMT")

    ltm["date_list"] = dl

    lifetime = {
        "Total Listening Sessions (Including Bounced)": metricsServerRequest("/ADP/SESSIONS/TOTAL/")["Total"],
        "Total Unique Listeners": metricsServerRequest("/ADP/LISTENER/TOTAL/")["Total"],
        "Total Bounced (Listened for under 1 minute)": metricsServerRequest("/ADP/SESSIONS/BOUNCED/")["Total"],
        "Total Current Sessions": metricsServerRequest("/ADP/SESSIONS/CURRENT/")["Total"],
        "Total Songs Played": metricsServerRequest("/ADP/SONGS/TOTAL/"),
        "Total Listener Hours": metricsServerRequest("/ADP/LISTENER/HOURS/")["Total"],
        "Average Session Listening Time": metricsServerRequest("/ADP/SESSIONS/AVGLISTENINGTIME/")["Overall"]
    }

    return render_template("index.html", 
                           user = g.user,
                           title="Youth Radio Intranet",
                           songs=metricsServerRequest("/ADP/SONGS/PLAYED/?limit=10"),
                           last_thirty_mins=ltm,
                           server_url=app.config["METRICS_SERVER_URL"],
                           lifetime_stats=lifetime)

app.run(host='127.0.0.1', port=5001, debug=app.config["DEBUG"])
