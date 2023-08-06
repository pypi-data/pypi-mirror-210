"""
API for qBittorrent
"""

import os

import aiobtclientrpc

from ... import errors, utils
from .. import base

import logging  # isort:skip
_log = logging.getLogger(__name__)


class QbittorrentAPI(base.APIBase, aiobtclientrpc.QbittorrentRPC):
    """
    qBittorrent API
    """

    async def _get_infohashes(self):
        torrents = await self.call('torrents/info')
        return (t['hash'] for t in torrents)

    async def _get_torrent_fields(self, infohash, *fields):
        torrents = await self.call('torrents/info', hashes=[infohash])
        if torrents and len(torrents) == 1:
            torrent = torrents[0]
            # Only return wanted information
            try:
                return {field: torrent[field] for field in fields}
            except KeyError as e:
                field = e.args[0]
                raise errors.ValueError(f'Unknown field: {field!r}')

        else:
            # qBittorrent returns all torrents if it can't find `infohash`
            known_infohashes = await self.get_infohashes()
            if infohash not in known_infohashes:
                raise errors.NoSuchTorrentError(infohash)
            else:
                raise RuntimeError(f'Unexpected response: {torrents!r}')

    async def _make_add_torrent_args(self, *, torrent, location, stopped, verify):
        rpc_args = utils.without_None_values({
            'paused': 'true' if stopped else 'false',
            'skip_checking': 'false' if verify else 'true',
            'savepath': location,
        })

        if utils.is_magnet(torrent):
            rpc_args['urls'] = [str(torrent)]
            infohash = utils.torrent.get_infohash(torrent)

        elif utils.is_infohash(torrent):
            rpc_args['urls'] = [f'magnet:?xt=urn:btih:{torrent}']
            infohash = utils.torrent.get_infohash(torrent)

        else:
            if utils.is_url(torrent):
                torrent_bytes = await utils.torrent.download_bytes(torrent)
            else:
                # Assume `torrent` is local file
                torrent_bytes = utils.torrent.read_bytes(torrent)
            infohash = utils.torrent.get_infohash(torrent_bytes)
            rpc_args['files'] = (
                ('filename', (
                    os.path.basename(torrent),   # File name
                    torrent_bytes,               # File content
                    'application/x-bittorrent',  # MIME type
                )),
            )

        return rpc_args, infohash

    async def _add_torrent(self, torrent, *, location, stopped, verify):
        rpc_args, infohash = await self._make_add_torrent_args(
            torrent=torrent,
            location=location,
            stopped=stopped,
            verify=verify,
        )

        try:
            response = await self.call('torrents/add', **rpc_args)

        except aiobtclientrpc.RPCError as e:
            raise e.translate({
                r'not a valid torrent': errors.InvalidTorrentError(torrent),
            })

        else:
            if response == 'Fails.':
                # qBittorrent doesn't report duplicate torrents, it just "Fails."
                # with HTTP status "200 OK"
                if infohash in await self.get_infohashes():
                    yield ('already_added', infohash)
                    yield errors.TorrentAlreadyAdded(infohash, name=torrent)
                else:
                    raise errors.InvalidTorrentError(torrent)

            else:
                # Wait for command to take effect
                await utils.Monitor(
                    call=self.get_infohashes,
                    interval=self.monitor_interval,
                    timeout=self.monitor_timeout,
                ).return_value_contains(infohash)
                yield ('added', infohash)

    async def _start_torrent(self, infohash):
        # Check current state
        state = await self._get_torrent_field(infohash, 'state')
        if not state.startswith('paused'):
            yield ('already_started', infohash)
            yield errors.TorrentAlreadyStarted(infohash)
        else:
            await self.call('torrents/resume', hashes=[infohash])

            # Wait for command to take effect
            await utils.Monitor(
                call=utils.partial(self._get_torrent_field, infohash, 'state'),
                interval=self.monitor_interval,
                timeout=self.monitor_timeout,
            ).return_value_contains('paused', negate=True)

            yield ('started', infohash)

    async def _stop_torrent(self, infohash):
        # Check current state
        state = await self._get_torrent_field(infohash, 'state')
        if state.startswith('paused'):
            yield ('already_stopped', infohash)
            yield errors.TorrentAlreadyStopped(infohash)
        else:
            await self.call('torrents/pause', hashes=[infohash])

            # Wait for command to take effect
            await utils.Monitor(
                call=utils.partial(self._get_torrent_field, infohash, 'state'),
                interval=self.monitor_interval,
                timeout=self.monitor_timeout,
            ).return_value_contains('paused')

            yield ('stopped', infohash)

    async def _start_verifying(self, infohash):
        response = await self.call('torrents/recheck', hashes=[infohash])
        _log.debug('started verifying: %r', response)

    async def _torrent_is_verifying(self, infohash):
        state = await self._get_torrent_field(infohash, 'state')
        _log.debug('torrent state: %r', state)
        return state.startswith('checking')

    async def _get_verifying_progress(self, infohash):
        progress = await self._get_torrent_field(infohash, 'progress')
        _log.debug('verifying progress: %r', progress)
        return progress * 100
