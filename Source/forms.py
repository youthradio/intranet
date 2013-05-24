from flask.ext.wtf import Form, TextField, DateField, SelectField, BooleanField, SubmitField, validators

US_STATES = [
    ("None", "State"), ("AK", "Alaska"), ("AL", "Alabama"), ("AS", "American Samoa"),
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

class AddPOCategory(Form):
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


class AddPerson(Form):
    """ This is a WTForms implementation for
    adding a person to the Youth Radio database.
    """

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
    dob = DateField('dob', format='%m/%d/%y', validators=[
        validators.Optional()
    ])

    # Contact information
    phone_home = TextField('phone_home', validators=[
        validators.Optional()
    ])
    phone_cell = TextField('phone_cell', validators=[
        validators.Optional()
    ])
    address_street_1 = TextField('address_street_1', validators=[
        validators.Optional()
    ])
    address_street_2 = TextField('address_street_2', validators=[
        validators.Optional()
    ])
    address_city = TextField('address_city', validators=[
        validators.Optional()
    ])
    address_state = SelectField('address_state', choices=US_STATES, validators=[
        validators.Optional()
    ])
    address_zip = TextField('address_zip', validators=[
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

    # Staff-specific information
    extension = TextField('extension', validators=[
        validators.Optional()
    ])
    department = TextField('department', validators=[
        validators.Optional()
    ])
    supervisor = TextField('supervisor', validators=[
        validators.Optional()
    ])
    title = TextField('title', validators=[
        validators.Optional()
    ])

    # Submit field
    add_person = SubmitField('Add Person')