from __future__ import annotations

import logging
import os
import time
from os.path import isfile, join

import leanit_mweb

logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

class Manage:
    def __init__(self):
        import argparse
        parser = argparse.ArgumentParser(description='')

        subparsers = parser.add_subparsers(dest='command', required=True)

        dev_parser = subparsers.add_parser('dev')
        dev_parser.add_argument('-p', '--port', type=int, default=20102, help='Port number')

        migrate_parser = subparsers.add_parser('migrate')

        # test
        test_parser = subparsers.add_parser('test')

        self.args = parser.parse_args()

    def main(self):
        getattr(self, f"on_command_{self.args.command}")()

    def _get_app_dir(self):
        app_dir = None
        # find directories in current directory containing a main.py file, select the first one
        for directory in os.listdir("."):
            if not os.path.isdir(directory):
                continue
            if isfile(join(directory, "main.py")):
                app_dir = directory
                break

        if not app_dir:
            raise RuntimeError("No app directory found")

        return app_dir

    def on_command_dev(self):
        directory = self._get_app_dir()

        port = self.args.port

        import webbrowser
        def open_webbrowser():
            # ensure app is up
            time.sleep(2)

            url = f"http://localhost:{port}/docs"
            print(f"Open {url} in your browser")
            webbrowser.open(url)

        import threading
        thread = threading.Thread(target=open_webbrowser)
        thread.start()

        cmd = ["uvicorn", f"{directory}.main:app", "--host", "0.0.0.0", "--port", str(port), "--reload"]
        print(" ".join(cmd))
        os.system(" ".join(cmd))


    def on_command_test(self):
        print("test")


def main():
    Manage().main()
