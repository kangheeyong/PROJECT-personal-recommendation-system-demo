import time
import asyncio
import websockets

import json
from fire import Fire

from Feynman.etc.util import get_logger
from Feynman.cloud import Google_drive_data_base


class template_manager():
    def __init__(self):
        self.logger = get_logger()

    def _check(self):
        import pickle
        with open('google_drive_data_example.pickle', 'rb') as f:
            data = pickle.load(f)
        self.file_data = Google_drive_data_base(data)
        self.file_data.pruning_overlap_file()
        self.file_data.pruning_zombie_file()

    async def _task(self):
        self.logger.info('Start task...')
        while True:
            begin_t = time.time()

            self._check()

            sleep_t = max(0, 60 - int(time.time() - begin_t))
            self.logger.info('Sleep {} secs before next start'.format(sleep_t))
            await asyncio.sleep(sleep_t)

    def do_remove_set(self, arg):
        return self.file_data.remove_set

    def do_all_dic(self, arg):
        return self.file_data.all_dic

    def do_view_dic(self, arg):
        return self.file_data.view_dic

    def do_adj_dic(self, arg):
        return self.file_data.adj_dic

    def do_data_dic(self, arg):
        return self.file_data.data_dic

    def do_root(self, arg):
        return self.file_data.root

    async def _cmd_recv(self, ws, path):
        arg = await ws.recv()
        self.logger.info('Start consumer... at {}:{}{} {}'.format(ws.host, ws.port, path, arg))
        func = getattr(self, 'do_' + path[1:])
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
