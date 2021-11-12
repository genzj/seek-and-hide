__version__ = '0.1.0'

import logging
from time import sleep

from process_hider import ProcessHider
from seek_and_hide.notify import LoginWaiter
from seek_and_hide.user_seeker import has_user

logging.basicConfig(level=logging.DEBUG)

hider = ProcessHider(['/bin/sleep', '20'], auto_restart=True)

waiter = LoginWaiter()

waiter.wait()
if has_user("xxx"):
    hider.hide()

waiter.wait()
if not has_user("xxx"):
    hider.resume()

sleep(10)
