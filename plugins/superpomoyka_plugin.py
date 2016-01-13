__author__ = 'blockinhead'
'''
http://super-pomoyka.us.to/trash/ttv-list/ playlist downloader plugin
(based on torrent-telik plugin)
usage:
http://ip:port/superpomoyka
'''
import json
import logging
import urllib2
import urlparse
from modules.PluginInterface import AceProxyPlugin
from modules.PlaylistGenerator import PlaylistGenerator
import config.superpomoyka as config


class Superpomoyka(AceProxyPlugin):

    handlers = ('superpomoyka', )

    logger = logging.getLogger('plugin_superpomoyka')
    playlist = None

    def downloadPlaylist(self, url):
        try:
            req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"})
            Superpomoyka.playlist = urllib2.urlopen(req, timeout=10).read()
            Superpomoyka.logger.info('downloading playlist from %s' % url)
            Superpomoyka.playlist = Superpomoyka.playlist.split('\xef\xbb\xbf')[1]    # garbage at the beginning
            #some debug code
            #with open('c:/tmp/playlist.txt', 'w') as pl:
            #    pl.write(Superpomoyka.playlist)
        except Exception, e:
            Torrenttelik.logger.error("Can't download playlist!")
            Torrenttelik.logger.error('exception %s' % repr(e))
            return False

        return True

    def handle(self, connection):

        hostport = connection.headers['Host']

        connection.send_response(200)
        connection.send_header('Content-Type', 'application/x-mpegurl')
        connection.end_headers()

        if not self.downloadPlaylist(config.url):
            connection.dieWithError()
            return

        # Un-JSON channel list
        try:
            jsonplaylist = json.loads(Superpomoyka.playlist)
        except Exception as e:
            Superpomoyka.logger.error("Can't load JSON! " + repr(e))
            return

        try:
            channels = jsonplaylist['channels']
            Superpomoyka.logger.info('%d channels found' % len(channels))
        except Exception as e:
            Superpomoyka.logger.error("Can't parse JSON! " + repr(e))
            return

        playlistgen = PlaylistGenerator()

        for channel in channels:
            playlistgen.addItem(channel)

        exported = playlistgen.exportm3u(hostport, add_ts=False)
        exported = exported.encode('utf-8')
        connection.wfile.write(exported)

