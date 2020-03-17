import sys
import time

import json
import asyncio
import websockets
import numpy as np
from fire import Fire

from Feynman.cloud import Google_drive
from Feynman.serialize import Pickle_serializer
from Feynman.etc.util import Config, get_logger


class Demo_user():
    def __init__(self):
        self.logger = get_logger()
        self.opt = Config(open('config/demo.json').read())
        self.url = self.opt.demo_user.url
        self.gd = Google_drive('token.pickle')
        self.ps = Pickle_serializer()

    def _make_user_list(self):
        user_num = self._traffic/24/60/60*self.opt.demo_user.sleep_t
        user_num = np.random.poisson(user_num)
        u_idxs = np.random.choice(range(self._user_count), user_num, p=self._p_user[0])
        return {'user_id': list(map(int, u_idxs))}

    def _pack_dic_msg(self, val, msg_type):
        dic_msg = {}
        dic_msg['type'] = msg_type
        dic_msg['value'] = val
        dic_msg['timestamp'] = time.ctime()
        dic_msg['servive'] = 'demo_personal_reco_system'
        return dic_msg

    async def _producer(self):
        self.logger.info('Start producer...')
        while True:
            begin_t = time.time()
            # to do
            try:
                u_list = self._make_user_list()
                self.logger.info('demo user {} generate... '.format(len(u_list['user_id'])))
                dic_msg = self._pack_dic_msg(val=u_list, msg_type='user_list')
                await self.ws.send(json.dumps(dic_msg))
            except Exception as e:
                self.logger.warning('Somthing is wrong : {}'.format(e))
                break
                # sys.exit(1)
            # finishing
            sleep_t = max(0, self.opt.demo_user.sleep_t - int(time.time() - begin_t))
            self.logger.info('Sleep {} secs before next start'.format(sleep_t))
            await asyncio.sleep(sleep_t)

    async def _consumer(self):
        self.logger.info('Start consumer...')
        while True:
            message = json.loads(await self.ws.recv())
            # to do
            try:
                print(message)
            except Exception as e:
                self.logger.warning('Somthing is wrong : {}'.format(e))
                break
                # sys.exit(1)
            # finishing

    async def _main(self):
        self.logger.info('Start...')
        while True:
            try:
                self._data_load()
                self.ws = await websockets.connect(self.url)
                await asyncio.gather(
                    self._producer(),
                    self._consumer()
                )
            except:
                self.logger.warning('Restart... after {} secs'.format(self.opt.demo_user.waiting_t))
                await asyncio.sleep(self.opt.demo_user.waiting_t)
                continue

    def _data_load(self):
        self.gd.download(folder=self.opt.demo_user.data.folder,
                         path=self.opt.demo_user.data.root_path)

        demo_user = self.ps.load(self.opt.demo_user.data.data_path)

        self._traffic = demo_user['traffic']
        self._user_count = demo_user['user_count']
        self._p_user = demo_user['p_user']

    def run(self):
        asyncio.run(self._main())


if __name__ == '__main__':
    Fire(Demo_user)
