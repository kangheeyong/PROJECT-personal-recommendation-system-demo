import sys
import time
from collections import defaultdict

import json
import asyncio
import numpy as np
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
        self._opt = Config(open('config/demo.json').read())
        self._gd = Google_drive('~/token.pickle')
        self._ps = Pickle_serializer()
        self._kp = Kafka_queue_producer(self._opt.demo_app.kafka.data_center)

        self._reco_p_item_cluster = {}
        self._reco_user_id_dic = {}
        self._cluster = {}
        self._reco_p_cluster_user = {}

    def _data_load(self):
        self._opt = Config(open('config/demo.json').read())
        for bucket in self._opt.demo_app.bucket.values():
            self._gd.download(folder=bucket.google_drive.folder,
                              path=bucket.google_drive.root_path)

            reco_item_cluster = self._ps.load(bucket.google_drive.reco_item_cluster_path)
            reco_cluster_user = self._ps.load(bucket.google_drive.reco_cluster_user_path)

            self._reco_p_item_cluster[bucket.name] = reco_item_cluster['reco_p_item_cluster']
            self._reco_user_id_dic[bucket.name] = reco_cluster_user['reco_user_id_dic']
            self._cluster[bucket.name] = reco_cluster_user['cluster']
            self._reco_p_cluster_user[bucket.name] = reco_cluster_user['reco_p_cluster_user']
            self.logger.info('Update [{}-{}] bucket...'.format(bucket.name, bucket.version))

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
            sleep_t = max(0, 60 - int(time.time() - begin_t))
            self.logger.info('Sleep {} secs before next start'.format(sleep_t))
            await asyncio.sleep(sleep_t)

    def __make_reco(self, user_id, bucket):
        if user_id in self._reco_user_id_dic[bucket]:
            cluster = self._reco_p_cluster_user[bucket][self._reco_user_id_dic[bucket][user_id]]
        else:
            cluster = [1./self._cluster[bucket] for _ in range(self._cluster[bucket])]

        dic = defaultdict(float)
        for k in range(self._cluster[bucket]):
            for item, prob in self._reco_p_item_cluster[bucket][k].items():
                dic[item] += prob*cluster[k]
        return sorted(dic.items(), key=lambda x: -x[1])[:10]

    def sample_bucket(self):
        name, prob = [], []
        for bucket in self._opt.demo_app.bucket.values():
            name.append(bucket.name)
            prob.append(bucket.ratio)
        return np.random.choice(name, p=prob)

    def _make_reco(self, massege):
        dic = defaultdict(float)
        user_list = massege['value']['user_id']
        for user_id in user_list:
            bucket = self.sample_bucket()
            dic[user_id] = {'list': self.__make_reco(user_id, bucket),
                            'bucket': bucket}
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
                    self._kp.push(dic_msg)
                elif message['type'] == 'user_feedback':
                    self._kp.push(message)
            except Exception as e:
                self.logger.warning('Somthing is wrong : {}'.format(e))
                sys.exit(1)
            # finishing

    def run(self):
        app.add_task(self._task)
        app.add_websocket_route(self._feed, self._opt.demo_app.sanic.websocket_route)
        app.run(host=self._opt.demo_app.sanic.host, port=self._opt.demo_app.sanic.port)


if __name__ == '__main__':
    Fire(Demo_app)
