"""
API for Deluge
"""

import base64
import os
import re

import aiobtclientrpc

from ... import errors, utils
from .. import base

import logging  # isort:skip
_log = logging.getLogger(__name__)


class DelugeAPI(base.APIBase, aiobtclientrpc.DelugeRPC):
    """
    Deluge API
    """

    common_rpc_error_map = {
        rf"^'?({utils.find_infohash_regex.pattern})'?$": (errors.NoSuchTorrentError, r'\1'),
    }

    async def _get_infohashes(self):
        return await self.call('core.get_session_state')

    def _normalize_infohash(self, infohash):
        # Deluge doesn't seem to understand uppercase infohashes (wtf!)
        return super()._normalize_infohash(infohash.lower())

    async def _get_torrent_fields(self, infohash, *fields):
        response = await self.call('core.get_torrent_status', infohash, keys=fields)
        if response:
            # Return only requested fields
            try:
                return {f: response[f] for f in fields}
            except KeyError as e:
                field = e.args[0]
                raise errors.ValueError(f'Unknown field: {field!r}')

        else:
            # Deluge returns an empty `dict` if:
            #   1. No torrent with `infohash` exists
            #   2. None of the `fields` are valid
            infohashes = await self.get_infohashes()
            if infohash not in infohashes:
                raise errors.NoSuchTorrentError(infohash)
            else:
                raise RuntimeError(f'Unexpected response: {response!r}')

    async def _make_add_torrent_args(self, *, torrent, location, stopped, verify):
        rpc_args = {
            'options': utils.without_None_values({
                'add_paused': bool(stopped),
                'seed_mode': not bool(verify),
                'download_location': location,
            }),
        }

        if utils.is_magnet(torrent):
            rpc_function = 'core.add_torrent_magnet'
            rpc_args['uri'] = str(torrent)

        elif utils.is_infohash(torrent):
            rpc_function = 'core.add_torrent_magnet'
            rpc_args['uri'] = f'magnet:?xt=urn:btih:{torrent}'

        else:
            if utils.is_url(torrent):
                torrent_bytes = await utils.torrent.download_bytes(torrent)
            else:
                # Assume `torrent` is local file
                torrent_bytes = utils.torrent.read_bytes(torrent)

            rpc_args['filedump'] = str(
                base64.b64encode(torrent_bytes),
                encoding='ascii',
            )
            rpc_args['filename'] = os.path.basename(torrent)
            rpc_function = 'core.add_torrent_file'

        return rpc_function, rpc_args

    async def _add_torrent(self, torrent, *, location, stopped, verify):
        rpc_function, rpc_args = await self._make_add_torrent_args(
            torrent=torrent,
            location=location,
            stopped=stopped,
            verify=verify,
        )

        try:
            infohash = await self.call(rpc_function, **rpc_args)
            yield ('added', infohash)

        except aiobtclientrpc.RPCError as e:
            dupe_regex = re.compile(r'Torrent already (?:in session|being added) \(([0-9a-zA-Z]+)\)')
            match = dupe_regex.search(str(e))
            if match:
                infohash = match.group(1)
                yield ('already_added', infohash)
                yield errors.TorrentAlreadyAdded(infohash, torrent)
            else:
                raise e.translate({
                    # Invalid torrent
                    r'decoding filedump failed': errors.InvalidTorrentError(torrent),
                    # Invalid magnet URI
                    r'invalid magnet info': errors.InvalidTorrentError(torrent),
                    r'non-hexadecimal number found': errors.InvalidTorrentError(torrent),
                })

    async def _start_torrent(self, infohash):
        # Check current state
        state = await self._get_torrent_field(infohash, 'state')
        if state == 'Error':
            yield ('errors', 'Cannot start torrent in error state')

        elif state != 'Paused':
            yield ('already_started', infohash)
            yield errors.TorrentAlreadyStarted(infohash)

        else:
            await self.call('core.resume_torrent', infohash)

            # Wait for command to take effect
            await utils.Monitor(
                call=utils.partial(self._get_torrent_field, infohash, 'state'),
                interval=self.monitor_interval,
                timeout=self.monitor_timeout,
            ).return_value_equals('Paused', negate=True)

            yield ('started', infohash)

    async def _stop_torrent(self, infohash):
        # Check current state
        state = await self._get_torrent_field(infohash, 'state')
        if state == 'Error':
            yield ('errors', 'Cannot stop torrent in error state')

        elif state == 'Paused':
            yield ('already_stopped', infohash)
            yield errors.TorrentAlreadyStopped(infohash)

        else:
            await self.call('core.pause_torrent', infohash)

            # Wait for command to take effect
            await utils.Monitor(
                call=utils.partial(self._get_torrent_field, infohash, 'state'),
                interval=self.monitor_interval,
                timeout=self.monitor_timeout,
            ).return_value_equals('Paused')

            yield ('stopped', infohash)

    async def _start_verifying(self, infohash):
        _log.debug('Start verifying: %r', infohash)
        await self.call('core.force_recheck', [infohash])

    async def _torrent_is_verifying(self, infohash):
        state = await self._get_torrent_field(infohash, 'state')
        _log.debug('torrent state: %r', state)
        return state == 'Checking'

    async def _get_verifying_progress(self, infohash):
        progress = await self._get_torrent_field(infohash, 'progress')
        _log.debug('verifying progress: %r', progress)
        return progress
