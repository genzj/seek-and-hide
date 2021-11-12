import logging
from typing import Optional
from inotify_simple import INotify, flags

L = logging.getLogger(__name__)


class LoginWaiter:
    inotify: INotify

    def __init__(self, path: str = '/var/run/utmp') -> None:
        self.inotify = INotify()
        watch_flags = flags.CREATE | flags.DELETE | flags.MODIFY
        self.inotify.add_watch('/var/run/utmp', watch_flags)

    def wait(self, timeout: Optional[float] = None):
        for event in self.inotify.read(timeout):
            L.debug("get event: %s", event)
            for flag in flags.from_mask(event.mask):
                L.debug("    %s", flag)
