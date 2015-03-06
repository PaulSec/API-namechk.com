"""
This is the (unofficial) Python API for namechk.com Website.
Using this code, you can manage to retrieve info on a specific person with his name.

"""
import requests
import re
import urllib
from hashlib import sha1
from hmac import new as hmac
import threading
import Queue


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
        url = 'http://namechk.com/Content/sites.min.js'
        resp = requests.get(url)
        # extract sites info from the js file
        pattern = 'n:"([^"]+)",r:\d+,i:(\d+),s:"([^"]+)",b:"([^"]+)"'
        sites = re.findall(pattern, resp.text.replace('\n', ''))
        queue = Queue.Queue()

        # starting threads
        for i in range(5):
            t = ThreadSearch(queue, self)
            t.setDaemon(True)
            t.start()

        # inserting values in queue
        for username in usernames:
            result[username] = {}
            for site in sites:
                queue.put([username, site])

        # waiting on queue
        queue.join()
        return result


class ThreadSearch(threading.Thread):
    def __init__(self, queue, obj):
        threading.Thread.__init__(self)
        self.queue = queue
        self.obj = obj
    
    def run(self):
        while True:
            item = self.queue.get()
            username, site = item[0], item[1]
            # hardcoded key for hmac
            key = '1Sx8srDg1u57Ei2wqX65ymPGXu0f7uAig13u'
            # reset url for site requests
            url = 'http://namechk.com/check'
            # required header for site requests
            headers = {'X-Requested-With': 'XMLHttpRequest'}

            i = site[1]
            name = site[0]
            # build the hmac payload
            message = "POST&%s?i=%s&u=%s" % (url, i, username)
            b64_hmac_sha1 = '%s' % hmac(key, message, sha1).digest().encode('base64')[:-1]
            payload = {'i': i, 'u': username, 'o_0': b64_hmac_sha1}
            # build and send the request
            try:
                resp = requests.post(url, headers=headers, data=payload)
                x = resp.text
                if int(x) > 0:
                    self.obj.display_message('%s: %s' % (name, STATUSES[x]))
                    result[username][name] = STATUSES[x]
                else:
                    self.obj.display_message('%s: %s' % (name, 'Unknown error.'))
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except Exception as e:
                self.obj.display_message('%s: %s' % (name, e.__str__()))
                pass
            self.queue.task_done()

STATUSES = {
    '1': 'Available',
    '2': 'User Exists!',
    '3': 'Unknown',
    '4': 'Indefinite'
}

result = {}