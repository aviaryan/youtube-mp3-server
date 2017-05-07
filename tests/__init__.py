import unittest
import json
# import os
from anyaudio import app
from anyaudio.helpers.database import init_databases

init_databases()


class YMP3TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        # DATABASE_PATH = 'test.db'
        self.app = app.test_client()

    def _search(self, term, just_results=False, version='v1'):
        """
        searches and returns the result
        :just_results - If true, return results dict
        """
        resp = self.app.get('/api/' + version + '/search?q=%s' % term)
        self.assertEqual(resp.status_code, 200)
        if just_results:
            return json.loads(resp.data)['results']
        else:
            return resp.data

    def _search_v2(self, term, just_results=False):
        return self._search(term, just_results=just_results, version='v2')

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
