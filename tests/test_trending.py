import unittest
import json
from tests import YMP3TestCase
from anyaudio.schedulers import trending
from anyaudio.helpers.data import trending_playlist


class TestTrending(YMP3TestCase):
    """
    Test Trending
    """
    def test_trending_worker_run(self):
        """run trending worker and see if it goes well"""
        scheduler = trending.TrendingScheduler()
        scheduler.run_repeater = scheduler.run
        worker = scheduler.start()
        worker.join()
        # ^^ wait for above to finish
        for playlist in trending_playlist:
            resp = self.app.get('/api/v1/trending?type=%s' % playlist[0])
            self.assertEqual(resp.status_code, 200, playlist[0])
            self.assertIn('stream_url', resp.data)
            data = json.loads(resp.data)
            self.assertNotEqual(data['metadata']['count'], 0, playlist[0])


if __name__ == '__main__':
    unittest.main()
