import logging

import utmp

L = logging.getLogger(__name__)


def has_user(username: str) -> bool:
    with open('/var/run/utmp', 'rb') as fd:
        buf = fd.read()
        for entry in utmp.read(buf):
            L.debug("%s %s %s", entry.time, entry.type, entry)
            if entry.user == username:
                L.info('found user %s at %s', username, entry.line)
                return True
    return False
