import unittest
import json
# import os
from ymp3 import app
from ymp3.helpers.database import init_databases

init_databases()


class YMP3TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        # DATABASE_PATH = 'test.db'
        self.app = app.test_client()

    def _search(self, term, just_results=False):
        """
        searches and returns the result
        :just_results - If true, return results dict
        """
        resp = self.app.get('/api/v1/search?q=%s' % term)
        self.assertEqual(resp.status_code, 200)
        if just_results:
            return json.loads(resp.data)['results']
        else:
            return resp.data

    def _get_dl_link(self, url, just_url=False):
        """
        from get download url, get the download url
        """
        resp = self.app.get(url)
        self.assertEqual(resp.status_code, 200)
        if just_url:
            return json.loads(resp.data)['url']
        else:
            return resp.data

    def tearDown(self):
        pass
        # if os.path.isfile('test.db'):
        #     os.unlink('test.db')
