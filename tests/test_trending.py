import unittest
import json
from tests import YMP3TestCase
from ymp3.schedulers import trending


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
        resp = self.app.get('/api/v1/trending')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertNotEqual(data['metadata']['count'], 0)


if __name__ == '__main__':
    unittest.main()
