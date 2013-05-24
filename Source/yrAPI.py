import urllib2, urllib, json

class yrAPI(object):
    """Youth Radio API wrapper methods."""
    def __init__(self, url):
        self.server_url = url
        super(yrAPI, self).__init__()


    def serverRequest(self, method, data=None):
        """ Connect to the Youth Radio API server and return a result.

        This function returns JSON from the API server
        using the configuration variables given in the configuration
        file.
        """
        if data:
            # This is a post request.
            # Prepare the data.
            encoded_data = urllib.urlencode(data)

            # Prepare the request.
            request = urllib2.Request(self.server_url + method, encoded_data)
        else:
            # This is a get request.
            request = urllib2.Request(self.server_url + method)

        # Send the request.
        response = urllib2.urlopen(request).read()
        ret = json.loads(response)

        return ret

    def getPurchaseOrderCategories(self, level, asTuples=False):
        """ Get the categories for purchase orders.

        level: an integer from 0 to 2 having to do with
        whether to return the base category, subcategory1, or
        subcategory2.

        asTuples: a boolean regarding to return the results as 
        tuples to used with WTForms or just a plain list.
        """
        # Get the categories from the API
        api_query_result = self.serverRequest('/finance/cat/list/%s' % str(level))
        categories = []

        if api_query_result and api_query_result['Status'] == "OK":
            api_categories = api_query_result['Response']
            api_categories.sort()

        if asTuples:
            for category in api_categories:
                categories.append((category, category))
        else:
            categories = api_categories

        return categories