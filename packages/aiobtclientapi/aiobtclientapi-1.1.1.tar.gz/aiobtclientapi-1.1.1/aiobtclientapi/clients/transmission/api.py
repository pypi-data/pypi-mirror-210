"""
API for the Transmission daemon
"""

import base64

import aiobtclientrpc

from ... import errors, utils
from .. import base
from . import enums

import logging  # isort:skip
_log = logging.getLogger(__name__)


class TransmissionAPI(base.APIBase, aiobtclientrpc.TransmissionRPC):
    """
    Transmission daemon API
    """

    async def _get_infohashes(self):
        response = await self.call('torrent-get', fields=['hashString'])
        return (t['hashString'] for t in response['arguments']['torrents'])

    async def _get_torrent_fields(self, infohash, *fields):
        response = await self.call('torrent-get', ids=[infohash], fields=fields)
        torrents = response['arguments']['torrents']
        if len(torrents) == 0:
            raise errors.NoSuchTorrentError(infohash)
        elif len(torrents) == 1:
            torrent = torrents[0]
            try:
                return {field: torrent[field] for field in fields}
            except KeyError as e:
                field = e.args[0]
                raise errors.ValueError(f'Unknown field: {field!r}')
        else:
            raise RuntimeError(f'Unexpected torrent list: {torrents!r}')

    async def _add_torrents(self, torrents, **kwargs):
        # TODO: Provide a different warning for Transmission 4.*, which decides
        # on its own if the content is verified
        if not kwargs.get('verify', True):
            yield errors.Warning(f'Adding torrents without verification is not supported by {self.label}')

        async for result in super()._add_torrents(torrents, **kwargs):
            yield result

    async def _make_add_torrent_args(self, *, torrent, location, stopped, verify):
        rpc_args = utils.without_None_values({
            'paused': bool(stopped),
            'download-dir': location,
        })

        if utils.is_magnet(torrent):
            rpc_args['filename'] = str(torrent)

        elif utils.is_infohash(torrent):
            rpc_args['filename'] = f'magnet:?xt=urn:btih:{torrent}'

        else:
            if utils.is_url(torrent):
                torrent_bytes = await utils.torrent.download_bytes(torrent)
            else:
                # Assume `torrent` is local file
                torrent_bytes = utils.torrent.read_bytes(torrent)

            rpc_args['metainfo'] = str(
                base64.b64encode(torrent_bytes),
                encoding='ascii',
            )

        return rpc_args

    async def _add_torrent(self, torrent, *, location, stopped, verify):
        rpc_args = await self._make_add_torrent_args(
            torrent=torrent,
            location=location,
            stopped=stopped,
            verify=verify,
        )

        try:
            result = await self.call('torrent-add', rpc_args)

        except aiobtclientrpc.RPCError as e:
            # Transmission 4.* sends
            # {"result": "duplicate torrent", "arguments": {"torrent-duplicate": ...}}
            if e.info and 'torrent-duplicate' in e.info:
                infohash = e.info['torrent-duplicate']['hashString']
                yield ('already_added', infohash)
                yield errors.TorrentAlreadyAdded(infohash, name=torrent)

            else:
                raise e.translate({
                    # Transmission 3.*
                    r'Invalid or corrupt': errors.InvalidTorrentError(torrent),
                    # Transmission 4.*
                    r'Unrecognized info': errors.InvalidTorrentError(torrent),
                })

        else:
            arguments = result['arguments']

            # Transmission 3.* sends
            # {"result": "success", "arguments": {"torrent-duplicate": ...}}
            if 'torrent-duplicate' in arguments:
                infohash = arguments['torrent-duplicate']['hashString']
                yield ('already_added', infohash)
                yield errors.TorrentAlreadyAdded(infohash, name=torrent)

            elif 'torrent-added' in arguments:
                infohash = arguments['torrent-added']['hashString']
                yield ('added', arguments['torrent-added']['hashString'])

            else:
                raise RuntimeError(f'Unexpected response: {result}')

    async def _start_torrent(self, infohash):
        # Check current state
        status = await self._get_torrent_field(infohash, 'status')
        if status != enums.TR_STATUS.STOPPED:
            yield ('already_started', infohash)
            yield errors.TorrentAlreadyStarted(infohash)
        else:
            await self.call('torrent-start', ids=[infohash])

            # Wait for command to take effect
            await utils.Monitor(
                call=utils.partial(self._get_torrent_field, infohash, 'status'),
                interval=self.monitor_interval,
                timeout=self.monitor_timeout,
            ).return_value_equals(enums.TR_STATUS.STOPPED, negate=True)

            yield ('started', infohash)

    async def _stop_torrent(self, infohash):
        # Check current state
        status = await self._get_torrent_field(infohash, 'status')
        if status == enums.TR_STATUS.STOPPED:
            yield ('already_stopped', infohash)
            yield errors.TorrentAlreadyStopped(infohash)
        else:
            await self.call('torrent-stop', ids=[infohash])

            # Wait for command to take effect
            await utils.Monitor(
                call=utils.partial(self._get_torrent_field, infohash, 'status'),
                interval=self.monitor_interval,
                timeout=self.monitor_timeout,
            ).return_value_equals(enums.TR_STATUS.STOPPED)

            yield ('stopped', infohash)

    async def _start_verifying(self, infohash):
        _log.debug('Start verifying: %r', infohash)
        await self.call('torrent-verify', ids=[infohash])

    async def _torrent_is_verifying(self, infohash):
        status = await self._get_torrent_field(infohash, 'status')
        return status in (enums.TR_STATUS.CHECK, enums.TR_STATUS.CHECK_WAIT)

    async def _get_verifying_progress(self, infohash):
        torrent = await self._get_torrent_fields(infohash, 'status', 'recheckProgress', 'percentDone')
        if torrent['status'] in (enums.TR_STATUS.CHECK, enums.TR_STATUS.CHECK_WAIT):
            return torrent['recheckProgress'] * 100
        else:
            # NOTE: Despite the name, "percentDone" is also a fraction from 0.0
            #       to 1.0.
            return torrent['percentDone'] * 100
