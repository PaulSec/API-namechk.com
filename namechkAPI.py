"""
This is the (unofficial) Python API for namechk.com Website.
Using this code, you can manage to retrieve info on a specific person with his name.

"""
import requests
from bs4 import BeautifulSoup

class NamechkAPI(object):

    """
        namechkAPI Main Handler
    """

    _instance = None
    _verbose = False

    def __init__(self, arg=None):
        pass

    def __new__(cls, *args, **kwargs):
        """
            __new__ builtin
        """
        if not cls._instance:
            cls._instance = super(NamechkAPI, cls).__new__(
                cls, *args, **kwargs)
            if (args and args[0] and args[0]['verbose']):
                cls._verbose = True
        return cls._instance

    def display_message(self, s):
        if (self._verbose):
            print '[verbose] %s' % s

    def search(self, usernames):
        url = 'https://namechk.com/'

        res = {}
        s = requests.Session()
        req = s.get(url)
        token = req.cookies['token']
        soup = BeautifulSoup(req.content, 'html.parser')

        providers = [provider['data-name'] for provider in soup.findAll('div', attrs={'class', 'record'})
                    if "unavailable" not in provider['class']]

        for username in usernames:
            res[username] = []
            for provider in providers:
                tmp_url = "{0}/availability/{1}?q={2}&x={3}".format(url, provider, username, token)
                data = s.get(tmp_url).json()
                if (not data['available']):
                    self.display_message("{0} exists on {1}".format(username, provider))
                    res[username].append(provider)
        return res