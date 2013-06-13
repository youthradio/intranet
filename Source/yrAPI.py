import urllib2, urllib, json, requests

class yrAPI(object):
    """Youth Radio API wrapper methods."""
    def __init__(self, url):
        self.server_url = url
        super(yrAPI, self).__init__()


    def serverRequest(self, api_method, request_method='GET', data=None):
        """ Connect to the Youth Radio API server and return a result.

        This function returns JSON from the API server
        using the configuration variables given in the configuration
        file.
        """
        if request_method.upper() == 'GET':
            response = requests.get(self.server_url + api_method, params=data, allow_redirects=True)
        elif request_method.upper() == 'POST':
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            response = requests.post(self.server_url + api_method, data=data, allow_redirects=True, headers=headers)

        return response.json()


    def getPurchaseOrderCategories(self, level, WTForms=False):
        """ Get the categories for purchase orders.

        level: an integer from 0 to 2 having to do with
        whether to return the base category, subcategory1, or
        subcategory2.

        asTuples: a boolean to return the results as 
        tuples to be used with WTForms or just a plain list.
        """
        # Get the categories from the API
        api_query_result = self.serverRequest('/finance/cat/list/%i' % level)
        api_categories = categories = []

        if api_query_result and api_query_result['Status'] == "OK":
            api_categories = api_query_result['Response']
            api_categories.sort()

        if WTForms:
            for category in api_categories:
                categories.append((category, category))
        else:
            categories = api_categories

        return categories

    def getPeople(self, type="all", WTFormat=False):
        """ Get people from the database.

        type: This can be three different values -
        staff, participant, all

        WTFormat: a boolean to return the results as
        tuples to be used with WTForms or just a plain list.
        """
        # Get the people from the API
        api_query_result = self.serverRequest('/people/%s/list' % type)
        api_people = people = []

        if api_query_result and api_query_result['Status'] == 'OK':
            api_people = api_query_result['People']

        if WTFormat:
            for person in api_people:
                people.append((person['_id'], '%s %s' % (person['first_name'], person['last_name'])))
        else:
            people = api_people

        return people

    def getPerson(self, _id):
        api_query_result = self.serverRequest('/person/%s' % _id)

        if api_query_result and api_query_result['Status'] == 'OK':
            api_person = api_query_result['Person']

        return api_person