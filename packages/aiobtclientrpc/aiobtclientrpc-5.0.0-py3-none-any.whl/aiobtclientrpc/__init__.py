"""
Asynchronous low-level communication with BitTorrent clients
"""

__project_name__ = 'aiobtclientrpc'
__description__ = 'Asynchronous low-level communication with BitTorrent clients'
__homepage__ = 'https://codeberg.org/plotski/aiobtclientrpc'
__version__ = '5.0.0'
__author__ = 'plotski'
__author_email__ = 'plotski@example.org'

# isort:skip_file

from ._base import RPCBase
from ._errors import *

from ._deluge import DelugeRPC, DelugeURL
from ._qbittorrent import QbittorrentRPC, QbittorrentURL
from ._rtorrent import RtorrentRPC, RtorrentURL
from ._transmission import TransmissionRPC, TransmissionURL

from ._utils import URL, ConnectionStatus, client, clients
