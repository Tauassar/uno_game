import functools
import io
import typing

import mode
import mode.utils.logging


class FileLogProxy(mode.utils.logging.FileLogProxy):
    @functools.cached_property
    def buffer(self) -> typing.BinaryIO:
        return io.BytesIO()


class Worker(mode.Worker):
    def _redirect_stdouts(self) -> None:
        """Overriding default stdouts redirecting method.

        This is needed since mode's 'FileLogProxy' does not implement
        'buffer' property and raises 'NotImplementedError' causing Pillow
        image saving method to be crashed.
        """
        original_cls = mode.utils.logging.FileLogProxy
        mode.utils.logging.FileLogProxy = FileLogProxy

        super()._redirect_stdouts()

        mode.utils.logging.FileLogProxy = original_cls
