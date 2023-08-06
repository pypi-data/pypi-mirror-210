import platform
import os
import signal
import sys


class Watcher:
    def __init__(self):
        if not platform.system().lower() == "linux":
            sys.exit("Watcher only works on Linux")
        self.child = os.fork()
        if self.child == 0:
            return
        else:
            self.watch()

    def watch(self):
        try:
            os.wait()
        except KeyboardInterrupt:
            self.kill()
        sys.exit()

    def kill(self):
        try:
            print("kill")
            os.kill(self.child, signal.SIGKILL)
        except OSError:
            pass


if __name__ == "__main__":
    Watcher()
