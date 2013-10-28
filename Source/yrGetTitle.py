import urllib2

from bs4 import BeautifulSoup
from cookielib import CookieJar

def getPageTitle(url):

    cj = CookieJar()
    
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:17.0) Gecko/20100101 Firefox/17.0')]
    response = opener.open(url)
    html = response.read()

    soup = BeautifulSoup(html)

    return soup.title.string
