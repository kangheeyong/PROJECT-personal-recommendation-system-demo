import time
import asyncio
import websockets

import json
from fire import Fire

from Feynman.etc.util import get_logger
from Feynman.cloud import Google_drive_data, Google_drive


class template_manager():
    def __init__(self):
        self.logger = get_logger()
        self._gd = Google_drive()

    def _check(self):
        self._gd.update_list()

    async def _task(self):
        self.logger.info('Start task...')
        while True:
            begin_t = time.time()

            self._check()

            sleep_t = max(0, 60 - int(time.time() - begin_t))
            self.logger.info('Sleep {} secs before next start'.format(sleep_t))
            await asyncio.sleep(sleep_t)

    def do_update(self, arg):
        return 'dumy'

    async def _cmd_recv(self, ws, path):
        arg = await ws.recv()
        self.logger.info('Start consumer... at {}:{}{} {}'.format(ws.host, ws.port, path, arg))
        self._gd.update_list()
        try:
            result = getattr(self._gd._file_data, path[1:])
        except AttributeError:
            func = getattr(self._gd, path[1:])
            result = func(arg)
        await ws.send(json.dumps(result))

    async def _main(self):
        coroutine_list = [websockets.serve(self._cmd_recv, '0.0.0.0', 8765),
                          self._task()]
        await asyncio.gather(*coroutine_list)

    def run(self):
        asyncio.run(self._main())


if __name__ == '__main__':
    Fire(template_manager)
