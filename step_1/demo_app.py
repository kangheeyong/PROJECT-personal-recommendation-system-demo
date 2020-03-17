import sys
import time
from collections import defaultdict

import json
import asyncio
from fire import Fire
from sanic import Sanic

from Feynman.cloud import Google_drive
from Feynman.serialize import Pickle_serializer
from Feynman.etc.util import Config, get_logger
from Feynman.database import Kafka_queue_producer


app = Sanic('Demo_app')


class Demo_app():
    def __init__(self):
        self.logger = get_logger()
        self.opt = Config(open('config/demo.json').read())
        self.gd = Google_drive('token.pickle')
        self.ps = Pickle_serializer()
        self.kp = Kafka_queue_producer('config/kafka.json')

    def _data_load(self):
        self.gd.download(folder='demo_reco',
                         path='cache')

        reco_item_cluster = self.ps.load('cache/demo_reco/reco_item_cluster.ps')
        reco_cluster_user = self.ps.load('cache/demo_reco/reco_cluster_user.ps')

        self._reco_p_item_cluster = reco_item_cluster['reco_p_item_cluster']
        self._reco_user_id_dic = reco_cluster_user['reco_user_id_dic']
        self._cluster = reco_cluster_user['cluster']
        self._reco_p_cluster_user = reco_cluster_user['reco_p_cluster_user']

    async def _task(self):
        self.logger.info('Start task...')
        while True:
            begin_t = time.time()
            # to do
            try:
                self._data_load()
            except Exception as e:
                self.logger.warning('Somthing is wrong : {}'.format(e))
                sys.exit(1)
            # finishing
            sleep_t = max(0, self.opt.demo_app.sleep_t - int(time.time() - begin_t))
            self.logger.info('Sleep {} secs before next start'.format(sleep_t))
            await asyncio.sleep(sleep_t)

    def __make_reco(self, user_id):
        if user_id in self._reco_user_id_dic:
            cluster = self._reco_p_cluster_user[self._reco_user_id_dic[user_id]]
        else:
            cluster = [1./self._cluster for _ in range(self._cluster)]

        dic = defaultdict(float)
        for k in range(self._cluster):
            for item, prob in self._reco_p_item_cluster[k].items():
                dic[item] += prob*cluster[k]
        return sorted(dic.items(), key=lambda x: -x[1])[:10]

    def _make_reco(self, massege):
        dic = defaultdict(float)
        user_list = massege['value']['user_id']
        for user_id in user_list:
            dic[user_id] = self.__make_reco(user_id)
        self.logger.info('Make {} users reco list...'.format(len(dic.keys())))
        return dic

    def _pack_dic_msg(self, val, msg_type):
        dic_msg = {}
        dic_msg['type'] = msg_type
        dic_msg['value'] = val
        dic_msg['timestamp'] = time.ctime()
        dic_msg['servive'] = 'demo_personal_reco_system'
        return dic_msg

    async def _feed(self, request, ws):
        self.logger.info('Start feed throw :{}:{}'.format(request.ip, request.port))
        while True:
            message = json.loads(await ws.recv())
            # to do
            try:
                if message['type'] == 'user_list':
                    reco_user_list = self._make_reco(message)
                    dic_msg = self._pack_dic_msg(val=reco_user_list, msg_type='reco_user_list')
                    await ws.send(json.dumps(dic_msg))
                    self.kp.push(dic_msg)
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
