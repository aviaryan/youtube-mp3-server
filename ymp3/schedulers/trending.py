from ymp3 import logger
from . import Scheduler
from ..helpers.data import trending_playlist
from ..helpers.trending import get_trending_videos
from ..helpers.networking import open_page
from ..helpers.database import save_trending_songs, clear_trending


class TrendingScheduler(Scheduler):

    def __init__(self, name='Trending Scheduler', period=21600, playlist=trending_playlist,
                 connection_delay=0):
        Scheduler.__init__(self, name, period)
        self.playlist = playlist
        self.connection_delay = connection_delay

    def run(self):

        for pl in self.playlist:
            logger.info('Crawling playlist "%s"' % pl[0])

            playlist_name = pl[0]
            playlist_url = pl[1]

            html = open_page(
                url=playlist_url,
                sleep_upper_limit=self.connection_delay,
            )

            song_data = get_trending_videos(html)
            
            clear_trending(playlist_name)
            save_trending_songs(playlist_name, song_data)
