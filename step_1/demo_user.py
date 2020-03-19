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
        self._opt = Config(open('config/demo.json').read())
        self._url = self._opt.demo_user.url
        self._gd = Google_drive('~/token.pickle')
        self._ps = Pickle_serializer()

    def _make_user_list(self):
        user_num = self._traffic/24/60/60*self._opt.demo_user.sleep_t
        user_num = np.random.poisson(user_num)
        u_idxs = np.random.choice(range(self._user_count), user_num, p=self._p_user[0])
        return {'user_id': list(map(int, u_idxs))}

    def _make_user_choice(self, u_list):
        u_idxs = u_list['user_id']
        u_ks = [np.random.choice(range(self._cluster), p=self._p_cluster_user[u_idx]) for u_idx in u_idxs]
        i_idxs = [np.random.choice(range(self._item_count), p=self._p_item_cluster[u_k]/sum(self._p_item_cluster[u_k])) for u_k in u_ks]
        return dict(zip(u_idxs, i_idxs))

    def _make_user_interest(self, u_list):
        u_idxs = u_list['user_id']
        u_max_interest = self._opt.demo_user.max_interest
        return {u_idx: list(np.argsort(-np.dot(self._p_cluster_user[u_idx], self._p_item_cluster))[:u_max_interest]) for u_idx in u_idxs}

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
                self._opt = Config(open('config/demo.json').read())

                u_list = self._make_user_list()
                self._u_choice = self._make_user_choice(u_list)
                self._u_interest = self._make_user_interest(u_list)
                self.logger.info('demo user {} generate... '.format(len(u_list['user_id'])))
                dic_msg = self._pack_dic_msg(val=u_list, msg_type='user_list')
                await self.ws.send(json.dumps(dic_msg))
            except Exception as e:
                self.logger.warning('Somthing is wrong : {}'.format(e))
                break
            # finishing
            sleep_t = max(0, self._opt.demo_user.sleep_t - int(time.time() - begin_t))
            self.logger.info('Sleep {} secs before next start'.format(sleep_t))
            await asyncio.sleep(sleep_t)

    def _make_user_react(self, message):
        result = []
        reco_user_list = message['value']
        pss, choice, click, unclick = 0, 0, 0, 0
        for user_id in reco_user_list.keys():
            stat = np.random.choice(['pass', 'choice', 'click'], p=[0.4, 0.3, 0.3])
            if stat == 'pass':
                pss += 1
                continue
            elif stat == 'choice' and int(user_id) in self._u_choice:
                tmp = {'user_id': user_id,
                       'item_id': str(self._u_choice[int(user_id)]),
                       'bucket': reco_user_list[user_id]['bucket'],
                       'stat': 'choice'}
                choice += 1
                result.append(tmp)
            elif stat == 'click' and int(user_id) in self._u_interest:
                reco_item = set(list(zip(*reco_user_list[user_id]['list']))[0])
                interest_item = set(self._u_interest[int(user_id)])
                candidate_item = list(reco_item.intersection(interest_item))
                if candidate_item:
                    tmp = {'user_id': user_id,
                           'item_id': str(np.random.choice(candidate_item)),
                           'bucket': reco_user_list[user_id]['bucket'],
                           'stat': 'click'}
                    click += 1
                    result.append(tmp)
                else:
                    unclick += 1
        self.logger.info('Make user feedback -> pass: {}, choice: {}, click: {}, unclick: {}'
                         .format(pss, choice, click, unclick))
        return result

    async def _consumer(self):
        self.logger.info('Start consumer...')
        while True:
            message = json.loads(await self.ws.recv())
            # to do
            try:
                if message['type'] == 'reco_user_list':
                    u_feedback = self._make_user_react(message)
                    dic_msg = self._pack_dic_msg(val=u_feedback, msg_type='user_feedback')
                    await self.ws.send(json.dumps(dic_msg))
            except Exception as e:
                self.logger.warning('Somthing is wrong : {}'.format(e))
                break
            # finishing

    def _data_load(self):
        self._gd.download(folder=self._opt.demo_user.google_drive.folder,
                          path=self._opt.demo_user.google_drive.root_path)

        demo_user = self._ps.load(self._opt.demo_user.google_drive.data_path)

        self._traffic = demo_user['traffic']
        self._user_count = demo_user['user_count']
        self._item_count = demo_user['item_count']
        self._cluster = demo_user['cluster']
        self._p_user = demo_user['p_user']
        self._p_cluster_user = demo_user['p_cluster_user']
        self._p_item_cluster = demo_user['p_item_cluster']
        self._user_idx = demo_user['user_idx']
        self._item_idx = demo_user['item_idx']
        self._u_choice = {}
        self._u_interest = {}

    async def _main(self):
        self.logger.info('Start...')
        while True:
            try:
                self._data_load()
                self.ws = await websockets.connect(self._url)
                await asyncio.gather(self._producer(),
                                     self._consumer())
            except Exception as e:
                self.logger.warning('Restart... after {} secs -> {}'.format(60, e))
                await asyncio.sleep(60)
                continue

    def run(self):
        asyncio.run(self._main())


if __name__ == '__main__':
    Fire(Demo_user)
