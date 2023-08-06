import base64
import glob
import os
import re


def get_home(name, tmp_path):
    homepath = tmp_path / f'{name}.home'
    homepath.mkdir(parents=True, exist_ok=True)
    return homepath


def get_test_torrents(map='filepath:infohash'):
    torrent_files = {}
    torrents_dirpath = os.path.join(os.path.dirname(__file__), 'torrents')
    for filepath in glob.glob(f'{torrents_dirpath}/*.torrent'):
        infohash = re.sub(r'^.*([a-zA-Z0-9]{40})\.torrent$', r'\1', filepath)
        if map == 'filepath:infohash':
            torrent_files[filepath] = infohash
        elif map == 'infohash:filepath':
            torrent_files[infohash] = filepath
        else:
            raise ValueError('Invalid map: {map}')
    assert torrent_files, torrent_files
    return torrent_files


def read_torrent_file(filepath):
    with open(filepath, 'rb') as f:
        filecontent = f.read()
    return str(base64.b64encode(filecontent), encoding='ascii')
