"""
Provide :mod:`aiobtclientapi` APIs
"""

import aiobtclientapi

from .. import utils


def client_names():
    """
    Return sequence of valid `client_name` values that may be passed to
    :class:`BittorrentClient`
    """
    return aiobtclientapi.client_names()


def client_defaults(client_name):
    """
    Create default client configuration

    The return value is a :class:`dict` with the following keys:

        - ``url``
        - ``username``
        - ``password``
        - ``check_after_add``

    :param client_name: Name of the client (see :func:`client_names`)
    """
    for cls in aiobtclientapi.api_classes():
        if cls.name == client_name:
            config = {
                'url': cls.URL.default,
                'username': '',
                'password': '',
                'check_after_add': utils.types.Bool('no'),
            }

            if cls.name == 'transmission':
                # Transmission < 4.0 cannot add torrent without verifying it
                # Transmission >= 4.0 decides itself if it wants to verify
                config['check_after_add'] = utils.types.Bool('yes')

            # TODO: Add support for qBittorrent category
            # if cls.name == 'qbittorrent':
            #     # Only qBittorrent has categories
            #     config['category'] = ''

            return config


class BtClient:
    """
    Thin wrapper class around a :class:`aiobtclientapi.APIBase` subclass

    :param name: Name of the client (see
        :func:`aiobtclientapi.names`)
    :param url: How to connect to the client API
    :param username: API password for authentication
    :param password: API password for authentication
    :param download_path: Where to download added torrents to
    :param check_after_add: Verify added torrents if content already exists
    """

    def __init__(self, name, *, url, username, password, download_path, check_after_add):
        self._api = aiobtclientapi.api(
            name=name,
            url=url,
            username=username,
            password=password,
        )
        self._download_path = download_path
        self._check_after_add = check_after_add

    @property
    def name(self):
        """Name of the client (same as :attr:`aiobtclientrpc.RPCBase.name`)"""
        return self._api.name

    @property
    def label(self):
        """Label of the client (same as :attr:`aiobtclientrpc.RPCBase.label`)"""
        return self._api.label

    async def add_torrent(self, torrent):
        """
        Add `torrent` to client

        :param torrent: ``.torrent`` file/URL, magnet link or infohash
        """
        return await self._api.add(
            torrent,
            location=self._download_path,
            verify=self._check_after_add,
        )
