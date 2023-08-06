import webbrowser
from logging import getLogger
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.request import urlopen as open_uri

from invisibleroads_macros_process import LoggableProcess


def open_browser(uri, check_interval_in_seconds=1):

    def wait_then_run():
        try:
            while True:
                try:
                    open_uri(uri)
                except HTTPError as e:
                    L.error(e)
                    return
                except URLError:
                    sleep(check_interval_in_seconds)
                else:
                    break
            webbrowser.open(uri)
        except KeyboardInterrupt:
            pass

    process = LoggableProcess(
        name='browser', target=wait_then_run, daemon=True)
    process.start()


L = getLogger(__name__)
