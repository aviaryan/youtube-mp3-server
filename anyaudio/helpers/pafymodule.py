import pafy
from anyaudio import logger


def get_download(url):
    """
    gets download link of a audio from url
    url - can be full youtube url or just video id
    """
    vid = pafy.new(url)
    audio_streams = vid.audiostreams
    return find_stream(
        audio_streams,
        [['m4a', 128], ['m4a', 192], ['ogg', 128], ['ogg', 192], ['m4a', 300], ['*', 0]]
    )


def get_stream(url):
    """
    gets stream link of a audio from url
    """
    vid = pafy.new(url)
    audio_streams = vid.audiostreams
    return find_stream(
        audio_streams,
        [
            ['webm', 64], ['webm', 80], ['m4a', 64], ['webm', 128], ['webm', 192], ['m4a', 128],
            ['webm', 300], ['m4a', 300], ['*', 0]
            # ^^ 300 used as bitrate sometimes varies slightly over 256, 300 has no side effects
        ]
    )


def find_stream(streams, prefs):
    """
    finds stream by priority
    streams = streams in descending order of bitrate
    prefs = [[format, bitrate]]
        bitrate - assumed to be less than equal to
    """
    final = ''
    for item in prefs:
        # fallback case
        if item[0] == '*':
            final = streams[0]
            break
        # general preferences
        for stream in streams:
            if stream.extension == item[0] and int(stream.bitrate.replace('k', '')) <= item[1]:
                final = stream
                break
        if final:
            break
    logger.info(final)
    return final.url
