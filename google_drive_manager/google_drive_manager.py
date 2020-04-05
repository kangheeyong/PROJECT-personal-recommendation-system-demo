import time
import asyncio
import websockets

from fire import Fire

from Feynman.etc.util import get_logger


class template_manager():
    def __init__(self):
        self.logger = get_logger()

    async def _task(self):
        self.logger.info('Start task...')
        while True:
            begin_t = time.time()

            print('tesk test')

            sleep_t = max(0, 60 - int(time.time() - begin_t))
            self.logger.info('Sleep {} secs before next start'.format(sleep_t))
            await asyncio.sleep(sleep_t)

    async def _cmd_recv(self, ws, path):
        self.logger.info('Start consumer... at {}:{}{}'.format(ws.host, ws.port, path))
        name = await ws.recv()
        print('< {}'.format(name))
        greeting = 'Hello {}!'.format(name)
        await ws.send(greeting)
        print('> {}'.format(greeting))

    async def _main(self):
        coroutine_list = []
        coroutine_list.append(websockets.serve(self._cmd_recv, '0.0.0.0', 8765))
        coroutine_list.append(self._task())
        await asyncio.gather(*coroutine_list)

    def run(self):
        asyncio.run(self._main())


if __name__ == '__main__':
    Fire(template_manager)
