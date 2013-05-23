import urllib2, urllib, json
import sys

sys.path.append('instance')
from intranet_cfg import *


def yrAPIServerRequest(method, data=None):
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
        request = urllib2.Request(YR_API_SERVER_URL + method, encoded_data)
    else:
        # This is a get request.
        request = urllib2.Request(YR_API_SERVER_URL + method)

    # Send the request.
    response = urllib2.urlopen(request)
    ret = json.loads(returned_json).read()

    return ret

