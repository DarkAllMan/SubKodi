from operator import itemgetter
import sys
import urllib
import urlparse
#sys.path.append('./resources/lib/')
import requests

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)


class Subsonic(object):

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def api(self, method, parameters={'none': 'none'}):
        return self.url + '/rest/' + method + '?u=%s&p=enc:%s&v=1.1.0&c=xbmc-subsonic&f=json&' % (
            self.username, self.password.encode('hex')) + urllib.urlencode(parameters)

    def artist_list(self):
        api_url = self.api('getIndexes.view',
                           parameters={'musicFolderId': '0'})
        r = requests.get(api_url)
        artists = []
        for index in r.json()['subsonic-response']['indexes']['index']:
            for artist in index['artist']:
                item = {}
                #item['name'] = artist['name'].encode('utf-8')
                #item['id'] = artist['id'].encode('utf-8')
                item['name'] = artist['name']
                item['id'] = artist['id']
                artists.append(item)

        return artists

    def music_directory_list(self, id):
        api_url = self.api('getMusicDirectory.view',
                           parameters={'id': id})
        r = requests.get(api_url)

        return r.json()['subsonic-response']['directory']['child']

    def genre_list(self):
        api_url = self.api('getGenres.view')
        r = requests.get(api_url)

        return sorted(r.json()['subsonic-response']['genres']['genre'],
                      key=itemgetter('value'))

    def albums_by_genre_list(self, genre):
        api_url = self.api('getAlbumList.view',
                           parameters={'type': 'byGenre',
                                       'genre': genre,
                                       'size': '500'})
        r = requests.get(api_url)

        return r.json()['subsonic-response']['albumList']['album']

    def random_songs_by_genre(self, genre):
        api_url = self.api('getRandomSongs.view',
                           parameters={'size': '500',
                                       'genre': genre})
        r = requests.get(api_url)
        return r.json()['subsonic-response']['randomSongs']['song']

    def random_songs_from_to_year(self, from_year, to_year):
        api_url = self.api('getRandomSongs.view',
                           parameters={'size': '500',
                                       'fromYear': from_year,
                                       'toYear': to_year})
        r = requests.get(api_url)
        return r.json()['subsonic-response']['randomSongs']['song']

    def cover_art(self, id):
        return self.api('getCoverArt.view', parameters={'id': id})


def main_page():
    menu = [{'mode': 'artist_list', 'foldername': 'Artists'},
            {'mode': 'genre_list', 'foldername': 'Genres'},
            {'mode': 'random_list', 'foldername': 'Random'}]
    for entry in menu:
        url = build_url(entry)
        li = xbmcgui.ListItem(entry['foldername'],
                              iconImage='DefaultFolder.png')
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            url=url,
            listitem=li,
            isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)


def genre_list():
    subsonic = Subsonic(subsonic_url, username, password)
    genres = subsonic.genre_list()
    for genre in genres:
        url = build_url({'mode': 'albums_by_genre_list',
                         'foldername': genre['value']})
        li = xbmcgui.ListItem(genre['value'],
                              iconImage='DefaultFolder.png')
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            url=url,
            listitem=li,
            isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)


def albums_by_genre_list():
    genre = args.get('foldername', None)
    subsonic = Subsonic(subsonic_url, username, password)
    albums = subsonic.albums_by_genre_list(genre[0])
    for album in albums:
        url = build_url({'mode': 'track_list',
                         #'foldername': unicode(album['title']).encode('utf-8'),
                         #'album_id': unicode(album['id']).encode('utf-8')})
                         'foldername': unicode(album['title']),
                         'album_id': unicode(album['id'])})						 
        li = xbmcgui.ListItem(album['artist'] + ' - ' + album['title'])
        li.setIconImage(subsonic.cover_art(album['id']))
        li.setThumbnailImage(subsonic.cover_art(album['id']))
        li.setProperty('fanart_image', subsonic.cover_art(album['id']))
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            url=url,
            listitem=li,
            isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)


def artist_list():
    subsonic = Subsonic(subsonic_url, username, password)
    artists = subsonic.artist_list()
    for artist in artists:
        url = build_url({'mode': 'album_list',
                         'foldername': artist['name'],
                         'artist_id': artist['id']})
        li = xbmcgui.ListItem(artist['name'])
        li.setIconImage(subsonic.cover_art(artist['id']))
        li.setThumbnailImage(subsonic.cover_art(artist['id']))
        li.setProperty('fanart_image', subsonic.cover_art(artist['id']))
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            url=url,
            listitem=li,
            isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)


def album_list():
    artist_id = args.get('artist_id', None)
    subsonic = Subsonic(subsonic_url, username, password)
    albums = subsonic.music_directory_list(artist_id[0])
    for album in albums:
        url = build_url({'mode': 'track_list',
                         #'foldername': unicode(album['title']).encode('utf-8'),
                         #'album_id': unicode(album['id']).encode('utf-8')})
                         'foldername': unicode(album['title']),
                         'album_id': unicode(album['id'])})
        li = xbmcgui.ListItem(album['title'])
        li.setIconImage(subsonic.cover_art(album['id']))
        li.setThumbnailImage(subsonic.cover_art(album['id']))
        li.setProperty('fanart_image', subsonic.cover_art(album['id']))
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            url=url,
            listitem=li,
            isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)


def track_list():
    album_id = args.get('album_id', None)
    subsonic = Subsonic(subsonic_url, username, password)
    tracks = subsonic.music_directory_list(album_id[0])
    for track in tracks:
        url = subsonic.api(
            'stream.view',
            parameters={'id': track['id'],
                        'maxBitRate': bitrate,
                        'format': trans_format})
        li = xbmcgui.ListItem(track['title'])
        li.setIconImage(subsonic.cover_art(track['id']))
        li.setThumbnailImage(subsonic.cover_art(track['id']))
        li.setProperty('fanart_image', subsonic.cover_art(track['id']))
        li.setProperty('IsPlayable', 'true')
        li.setInfo(
            type='Music',
            infoLabels={'Artist': track['artist'],
                        'Title': track['title']})
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            url=url,
            listitem=li)

    xbmcplugin.endOfDirectory(addon_handle)


def random_list():
    menu = [{'mode': 'random_by_genre_list', 'foldername': 'by Genre'},
            {'mode': 'random_from_to_year_list', 'foldername': 'from - to Year'}]
    for entry in menu:
        url = build_url(entry)
        li = xbmcgui.ListItem(entry['foldername'],
                              iconImage='DefaultFolder.png')
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            url=url,
            listitem=li,
            isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)


def random_by_genre_list():
    subsonic = Subsonic(subsonic_url, username, password)
    genres = subsonic.genre_list()
    for genre in genres:
        url = build_url({'mode': 'random_by_genre_track_list',
                         'foldername': genre['value']})
        li = xbmcgui.ListItem(genre['value'],
                              iconImage='DefaultFolder.png')
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            url=url,
            listitem=li,
            isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)


def random_by_genre_track_list():
    genre = args.get('foldername', None)[0]
    subsonic = Subsonic(subsonic_url, username, password)
    tracks = subsonic.random_songs_by_genre(genre)
    for track in tracks:
        url = subsonic.api(
            'stream.view',
            parameters={'id': track['id'],
                        'maxBitRate': bitrate,
                        'format': trans_format})
        li = xbmcgui.ListItem(track['artist'] + ' - ' + track['title'])
        li.setIconImage(subsonic.cover_art(track['id']))
        li.setThumbnailImage(subsonic.cover_art(track['id']))
        li.setProperty('fanart_image', subsonic.cover_art(track['id']))
        li.setProperty('IsPlayable', 'true')
        li.setInfo(
            type='Music',
            infoLabels={'Artist': track['artist'],
                        'Title': track['title']})
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            url=url,
            listitem=li)

    xbmcplugin.endOfDirectory(addon_handle)


def random_from_to_year_list():
    dialog = xbmcgui.Dialog()
    from_year = dialog.input('From Year', type=xbmcgui.INPUT_NUMERIC)
    dialog = xbmcgui.Dialog()
    to_year = dialog.input('To Year', type=xbmcgui.INPUT_NUMERIC)
    subsonic = Subsonic(subsonic_url, username, password)
    tracks = subsonic.random_songs_from_to_year(from_year, to_year)
    for track in tracks:
        url = subsonic.api(
            'stream.view',
            parameters={'id': track['id'],
                        'maxBitRate': bitrate,
                        'format': trans_format})
        li = xbmcgui.ListItem(track['artist'] + ' - ' + track['title'])
        li.setIconImage(subsonic.cover_art(track['id']))
        li.setThumbnailImage(subsonic.cover_art(track['id']))
        li.setProperty('fanart_image', subsonic.cover_art(track['id']))
        li.setProperty('IsPlayable', 'true')
        li.setInfo(
            type='Music',
            infoLabels={'Artist': track['artist'],
                        'Title': track['title']})
        xbmcplugin.addDirectoryItem(
            handle=addon_handle,
            url=url,
            listitem=li)

    xbmcplugin.endOfDirectory(addon_handle)


if __name__ == '__main__':
    import xbmcaddon
    import xbmcgui
    import xbmcplugin

    my_addon = xbmcaddon.Addon('plugin.audio.subsonic')
    subsonic_url = my_addon.getSetting('subsonic_url')
    username = my_addon.getSetting('username')
    password = my_addon.getSetting('password')
    trans_format = my_addon.getSetting('format')
    bitrate = my_addon.getSetting('bitrate')

    base_url = sys.argv[0]
    addon_handle = int(sys.argv[1])
    args = urlparse.parse_qs(sys.argv[2][1:])

    xbmcplugin.setContent(addon_handle, 'songs')

    mode = args.get('mode', None)

    if mode is None:
        main_page()
    elif mode[0] == 'artist_list':
        artist_list()
    elif mode[0] == 'album_list':
        album_list()
    elif mode[0] == 'track_list':
        track_list()
    elif mode[0] == 'genre_list':
        genre_list()
    elif mode[0] == 'albums_by_genre_list':
        albums_by_genre_list()
    elif mode[0] == 'random_list':
        random_list()
    elif mode[0] == 'random_by_genre_list':
        random_by_genre_list()
    elif mode[0] == 'random_by_genre_track_list':
        random_by_genre_track_list()
    elif mode[0] == 'random_from_to_year_list':
        random_from_to_year_list()
