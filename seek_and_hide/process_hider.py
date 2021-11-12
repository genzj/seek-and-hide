import logging
import typing
from os.path import basename
from queue import Empty, Queue
from select import select
from subprocess import PIPE, Popen
from threading import Thread
from time import sleep

RESUME = 'RESUME'
HIDE = 'HIDE'

L = logging.getLogger(__name__)


class ProcessHider:
    args: typing.List[str]
    auto_restart: bool
    cmds: Queue
    daemon: Thread
    hidden: bool
    logger: logging.Logger
    process: typing.Optional[Popen]
    slug: str

    def __init__(
        self,
        args: typing.List[str],
        auto_restart: bool = True,
        slug: typing.Optional[str] = None,
    ):
        self.args = args
        self.auto_restart = auto_restart
        self.cmds = Queue()
        self.process = None
        self.hidden = False
        self.slug = slug or basename(args[0])
        self.logger = L.getChild(self.slug)

        self.daemon = Thread(target=self._loop, daemon=True)
        self.daemon.start()

        self._spawn()

    def _spawn(self):
        self.process = None
        self.process = Popen(args=self.args, stderr=PIPE, stdout=PIPE)
        L.info("spawn PID=%d %s", self.process.pid, self.args)

    def _stop(self):
        if self.process is None:
            return

        if self.process.poll() is not None:
            self.logger.info(
                "PID=%d has exited with code %d",
                self.process.pid,
                self.process.returncode,
            )
            self.process = None
            return

        L.info("killing PID=%d", self.process.pid)
        self.process.kill()
        L.info("waiting PID=%d to exit for 10 secs", self.process.pid)
        try:
            retcode = self.process.wait(10)
            L.info("PID=%d exited with code %d", self.process.pid, retcode)
        except TimeoutError:
            L.info(
                "PID=%d hasn't exited after 10secs, try terminating",
                self.process.pid,
            )
            self.process.terminate()
        self.process = None

    def _poll_process(self):
        if not self.process:
            return

        if self.process.poll() is None:
            # process is still running
            self._poll_pipe(10)
            return

        self.logger.info(
            "PID=%d exited with code %d",
            self.process.pid,
            self.process.returncode,
        )
        # poll potential error message
        self._poll_pipe(0)
        self.process = None
        if not self.hidden and self.auto_restart:
            self._spawn()

    def _handle_cmd(self):
        try:
            cmd = self.cmds.get_nowait()
        except Empty:
            # no command in queue
            return

        if cmd is HIDE:
            self.hidden = True
            self.logger.info("hide process")
            self._stop()
        elif cmd is RESUME:
            self.hidden = False
            self.logger.info("resume process")
            self._spawn()

    def _poll_pipe(self, timeout: float):
        if self.process is None:
            return
        rds, _, _ = select(
            [self.process.stdout, self.process.stderr], [], [], timeout
        )
        for fd in rds:
            fd = typing.cast(typing.IO, fd)
            name = "STDOUT" if fd == self.process.stdout else "STDERR"
            out = fd.read()
            if not out:
                continue
            for line in out.split(b"\n"):
                self.logger.info("[%s] %s", name, line)

    def _loop(self):
        while True:
            self._poll_process()
            self._handle_cmd()
            if self.process is None:
                sleep(3)

    def hide(self):
        self.cmds.put(HIDE)

    def resume(self):
        self.cmds.put(RESUME)
