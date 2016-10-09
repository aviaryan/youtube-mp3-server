import unittest
import json
from tests import YMP3TestCase


class TestSearch(YMP3TestCase):
    """
    Test Search feature
    """
    def test_successful_search(self):
        """test a successful search of a music video"""
        result = self._search('Numb')
        self.assertIn('Numb', result)
        self.assertIn('Linkin Park', result)
        data = json.loads(result)
        self.assertEqual(len(data['results']), data['metadata']['count'])
        self.assertTrue(len(data['results']) >= 15, result)

    def test_long_video_not_returned(self):
        """test search of a term which usually will have long videos as results"""
        resp = self.app.get('/api/v1/search?q=kishore kumar')
        self.assertIn('Kishore', resp.data)
        data = json.loads(resp.data)
        self.assertTrue(len(data['results']) < 10)


if __name__ == '__main__':
    unittest.main()
