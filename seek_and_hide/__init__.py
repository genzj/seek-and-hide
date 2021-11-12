__version__ = '0.1.0'

from process_hider import ProcessHider

import logging
from time import sleep

logging.basicConfig(level=logging.DEBUG)

# hider = ProcessHider(['/bin/cat', '/etc/passwd'], auto_restart=True)
hider = ProcessHider(['/bin/sleep', '20'], auto_restart=True)

sleep(10)

hider.hide()

sleep(10)

hider.resume()
sleep(10)
