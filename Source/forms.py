from flask.ext.wtf import Form, TextField, DateField, SelectField, BooleanField, SubmitField, HiddenField, validators

US_STATES = [
    ("", "State"), ("AK", "Alaska"), ("AL", "Alabama"), ("AS", "American Samoa"),
    ("AZ", "Arizona"), ("AR", "Arkansas"), ("CA", "California"), ("CO", "Colorado"),
    ("CT", "Connecticut"), ("DE", "Delaware"), ("DC", "District of Columbia"), ("FL", "Florida"),
    ("GA", "Georgia"), ("GU", "Guam"), ("HI", "Hawaii"), ("ID", "Idaho"), ("IA", "Iowa"),
    ("IL", "Illinois"), ("IN", "Indiana"), ("KS", "Kansas"), ("KY", "Kentucky"),
    ("LA", "Louisiana"), ("ME", "Maine"), ("MA", "Massachusetts"), ("MD", "Maryland"),
    ("MH", "Marshall Islands"), ("MI", "Michigan"), ("MN", "Minnesota"),
    ("MS", "Mississippi"), ("MO", "Missouri"), ("MT", "Montana"), ("NC", "North Carolina"),
    ("ND", "North Dakota"), ("NE", "Nebraska"), ("NV", "Nevada"), ("NH", "New Hampshire"),
    ("NJ", "New Jersey"), ("NM", "New Mexico"), ("NY", "New York"), ("OH", "Ohio"),
    ("OK", "Oklahoma"), ("OR", "Oregon"), ("PW", "Palau"), ("PA", "Pennsylvania"),
    ("PR", "Puerto Rico"), ("RI", "Rhode Island"), ("SC", "South Carolina"),
    ("SD", "South Dakota"), ("TN", "Tennessee"), ("TX", "Texas"), ("UT", "Utah"),
    ("VI", "Virgin Islands"), ("VA", "Virginia"), ("VT", "Vermont"),
    ("WA", "Washington"), ("WV", "West Virginia"), ("WY", "Wyoming")
]

PERSON_TYPE = [
    ("staff", "Staff")
]

GENDER = [
    ("", "Gender"),
    ("M", "Male"),
    ("F", "Female"),
    ("MTF", "Male-to-Female"),
    ("FTM", "Female-to-Male")
]

class CentralForm(Form):
    """docstring for CentralForm"""
    def __init__(self):
        super(CentralForm, self).__init__()

    def populateFormFields(self, obj, prefix=''):
        """ In order to automatically populate the fields with
        values from the database, then use this function. """
        for field_name, field_value in obj.iteritems():
            if prefix + field_name in self:
                self[prefix + field_name].data = field_value


class AddPOCategory(CentralForm):
    """ This is a WTForms implementation for 
    adding a person to the Youth Radio database.
    """

    api_categories = None
    api_subcategories = None

    category = SelectField('category', validators=[
        validators.Optional()
    ])

    subcategory1 = SelectField('subcategory1', validators=[
        validators.Optional()
    ])

    # Set up the text fields
    new_category = TextField('new_category', validators=[
        validators.Optional()
    ])
    new_subcategory1 = TextField('new_subcategory1', validators=[
        validators.Optional()
    ])
    new_subcategory2 = TextField('new_subcategory2', validators=[
        validators.Optional()
    ])

    # Submit field
    add_category = SubmitField('Add Category/Subcategory')

class Person(CentralForm):
    # Type of person being added to the database
    person_type = SelectField('person_type', choices=PERSON_TYPE, validators=[
        validators.Required(message=(u'You must choose a person type.'))
    ])

    # Primary and vital statistics
    first_name = TextField('first_name', validators=[
        validators.Required(message=(u'First name is required.')),
        validators.Length(min=2, message=(u'First name needs to be longer than 2 characters.')),
    ])
    middle_initial = TextField('middle_initial', validators=[
        validators.Length(max=1, message=(u'Only one letter required for the middle intial.')),
        validators.Optional()
    ])
    last_name = TextField('last_name', validators=[
        validators.Required(message=(u'Last name is required.'))
    ])
    dob = TextField('dob', validators=[
        validators.Optional()
    ])
    email = TextField('email', validators=[
        validators.Required(message=(u'Email address is required. It must be a @youthradio.org address.'))
    ])
    gender = SelectField('gender', choices=GENDER, validators=[
        validators.Required(message=(u'You must choose a gender.'))
    ])

    # Contact information
    phone_home = TextField('phone_home', validators=[
        validators.Optional()
    ])
    phone_cell = TextField('phone_cell', validators=[
        validators.Optional()
    ])

    street_address_1 = TextField('street_address_1', validators=[
        validators.Optional()
    ])
    street_address_2 = TextField('street_address_2', validators=[
        validators.Optional()
    ])
    city = TextField('city', validators=[
        validators.Optional()
    ])
    state = SelectField('state', choices=US_STATES, validators=[
        validators.Optional()
    ])
    zipcode = TextField('zipcode', validators=[
        validators.Optional()
    ])

    # Emergency contact info
    emergency_contact_relationship = TextField('emergency_contact_relationship', validators=[
        validators.Optional()
    ])
    emergency_contact_name = TextField('emergency_contact_name', validators=[
        validators.Optional()
    ])
    emergency_contact_address = TextField('emergency_contact_address', validators=[
        validators.Optional()
    ])
    emergency_contact_phone_home = TextField('emergency_contact_phone_home', validators=[
        validators.Optional()
    ])
    emergency_contact_phone_cell = TextField('emergency_contact_phone_cell', validators=[
        validators.Optional()
    ])


class StaffMember(Person):
    # Staff-specific information
    extension = TextField('extension', validators=[
        validators.Optional()
    ])
    department = TextField('department', validators=[
        validators.Optional()
    ])
    supervisor = SelectField('supervisor', validators=[
        validators.Optional()
    ])
    title = TextField('title', validators=[
        validators.Optional()
    ])


class AddStaffMember(StaffMember):
    """ This is a WTForms implementation for
    adding a person to the Youth Radio database.
    """

    # Submit field
    submit = SubmitField('Add Person')


class EditStaffMember(StaffMember):
    """ This is a WTForms implementation for
    editing a staff member in the Youth Radio database.
    """

    # Hidden ID field
    person_id = HiddenField()

    # Submit field
    submit = SubmitField('Edit Person')

