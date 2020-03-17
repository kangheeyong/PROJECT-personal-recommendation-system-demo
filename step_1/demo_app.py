import sys
import time

import json
import asyncio
from fire import Fire
from sanic import Sanic

from Feynman.etc.util import Config, get_logger


app = Sanic('Demo_app')


class Demo_app():

    def __init__(self):
        self.logger = get_logger()
        self.opt = Config(open('config/demo.json').read())

    async def _task(self):
        self.logger.info('Start task...')
        while True:
            begin_t = time.time()
            # to do
            try:
                print('app task...')
            except Exception as e:
                self.logger.warning('Somthing is wrong : {}'.format(e))
                sys.exit(1)
            # finishing
            sleep_t = max(0, self.opt.demo_app.sleep_t - int(time.time() - begin_t))
            self.logger.info('Sleep {} secs before next start'.format(sleep_t))
            await asyncio.sleep(sleep_t)

    async def _feed(self, request, ws):
        self.logger.info('Start feed throw :{}:{}'.format(request.ip, request.port))
        while True:
            message = json.loads(await ws.recv())
            # to do
            try:
                print('get: {}'.format(message))
                await ws.send(json.dumps({'demo app': 'hello world!!!'}))
            except Exception as e:
                self.logger.warning('Somthing is wrong : {}'.format(e))
                sys.exit(1)
            # finishing

    def run(self):
        app.add_task(self._task)
        app.add_websocket_route(self._feed, self.opt.demo_app.base.websocket_route)
        app.run(host=self.opt.demo_app.base.host, port=self.opt.demo_app.base.port)


if __name__ == '__main__':
    Fire(Demo_app)
