"""
Exceptions

::

    Error
    ├── ValueError
    ├── ReadError
    ├── WriteError
    ├── NotImplementedError
    ├── ConnectionError
    │   ├── TimeoutError
    │   └── AuthenticationError
    └── ResponseError
        ├── NoSuchTorrentError
        ├── InvalidTorrentError
        ├── AddTorrentError
        ├── StartTorrentError
        ├── StopTorrentError
        └── VerifyTorrentError

    Warning
    └── TorrentWarning
        ├── TorrentAlreadyAdded
        ├── TorrentAlreadyStarted
        ├── TorrentAlreadyStopped
        └── TorrentAlreadyVerifying
"""


class Error(Exception):
    """Parent class of all fatal exceptions"""

    def __eq__(self, other):
        return (
            type(self) is type(other)
            and str(self) == str(other)
        )


class ValueError(Error, ValueError):
    """Invalid value"""


class ReadError(Error):
    """Failed reading operation"""


class WriteError(Error):
    """Failed writing operation"""


class NotImplementedError(Error, NotImplementedError):
    """Unimplemented or unsupported functionality"""


class ConnectionError(Error, ConnectionError):
    """Unable to connect to client"""


class TimeoutError(ConnectionError, TimeoutError):
    """Something took too long and was cancelled"""


class AuthenticationError(ConnectionError):
    """Wrong login credentials"""


class ResponseError(Error):
    """Generic error from a client API request, e.g. torrent does't exist"""

    def __new__(cls, cause, *args, **kwargs):
        self = super().__new__(cls, cause, *args, **kwargs)
        if isinstance(cause, Exception):
            self._cause = cause
        else:
            self._cause = None
        return self

    @property
    def cause(self):
        """
        :class:`Exception` that caused this error or `None`

        For example, :class:`AddTorrentError` can be caused by
        :class:`ConnectionError` or :class:`InvalidTorrentError`.
        """
        return self._cause


class NoSuchTorrentError(ResponseError):
    """Torrent identifier doesn't point to a known torrent"""

    def __init__(self, torrent):
        super().__init__(f'No such torrent: {torrent}')


class InvalidTorrentError(ResponseError):
    """Bad torrent file or magnet URI"""

    def __init__(self, torrent):
        super().__init__(f'Invalid torrent: {torrent}')


class AddTorrentError(ResponseError):
    """Failed to add torrent"""

    def __init__(self, cause):
        super().__init__(f'Adding torrent failed: {cause}')


class StartTorrentError(ResponseError):
    """Failed to start torrent"""

    def __init__(self, cause):
        super().__init__(f'Starting torrent failed: {cause}')


class StopTorrentError(ResponseError):
    """Failed to stop torrent"""

    def __init__(self, cause):
        super().__init__(f'Stopping torrent failed: {cause}')


class VerifyTorrentError(ResponseError):
    """Failed to verify torrent"""

    def __init__(self, cause):
        super().__init__(f'Verifying torrent failed: {cause}')


class Warning(Exception):
    """
    Generic warning about an acceptable, non-serious issue (e.g. adding
    duplicate torrent)
    """

    def __eq__(self, other):
        return (
            type(self) is type(other)
            and str(self) == str(other)
        )


class TorrentWarning(Warning):
    """
    :class:`Warning` about a torrent that provides the infohash and an
    optional name

    :param infohash: Infohash of the torrent
    :param name: Torrent name or user-provided torrent file, magnet URI, etc

    `infohash` should be a machine-readable ID while `name` should be a
    user-readable ID or an argument from user.
    """

    _msg_with_name = NotImplemented
    _msg_without_name = NotImplemented

    def __init__(self, infohash, name=None):
        if name and name != infohash:
            msg_format = self._msg_with_name
        else:
            msg_format = self._msg_without_name

        if msg_format is NotImplemented:
            raise RuntimeError(f'You are supposed to subclass {type(self).__name__}')
        else:
            msg = msg_format.format(infohash=infohash, name=name)
            super().__init__(msg)
            self._infohash = infohash
            self._name = name

    @property
    def infohash(self):
        """Infohash of the relevant torrent"""
        return self._infohash

    @property
    def name(self):
        """Name of the relevant torrent or `None`"""
        return self._name


class TorrentAlreadyAdded(TorrentWarning):
    """Torrent was already added"""

    _msg_with_name = 'Torrent already added: {name}: {infohash}'
    _msg_without_name = 'Torrent already added: {infohash}'


class TorrentAlreadyStarted(TorrentWarning):
    """Torrent is already started"""

    _msg_with_name = 'Torrent already started: {name}: {infohash}'
    _msg_without_name = 'Torrent already started: {infohash}'


class TorrentAlreadyStopped(TorrentWarning):
    """Torrent is already stopped"""

    _msg_with_name = 'Torrent already stopped: {name}: {infohash}'
    _msg_without_name = 'Torrent already stopped: {infohash}'


class TorrentAlreadyVerifying(TorrentWarning):
    """Torrent is already being verified"""

    _msg_with_name = 'Torrent already verifying: {name}: {infohash}'
    _msg_without_name = 'Torrent already verifying: {infohash}'
