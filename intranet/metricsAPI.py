from flask import jsonify

import urllib2, urllib, json

class MetricsAPI(object):
    """docstring for MetricsAPI"""
    def __init__(self, url, request):
        super(MetricsAPI, self).__init__()
        self.server_url = url
        self.request = request

    def serverRequest(self, method):
        """ Connect to the metrics server and return a result.

        This function returns JSON from the metrics server
        using the configuration variables given in the configuration
        file.
        """
        returned_json = urllib2.urlopen(self.server_url + method).read()
        ret = json.loads(returned_json)
        return ret['Result']



