import os
import time
from fire import Fire
from collections import defaultdict

from Feynman.database import Mongodb
from Feynman.cloud import Google_drive
from Feynman.serialize import Pickle_serializer
from Feynman.etc.util import Config, get_logger


class Base_gc():
    def __init__(self):
        self.logger = get_logger()
        self._ps = Pickle_serializer()
        self._gd = Google_drive()
        self._opt = Config(open('config/demo_dist.json').read())
        self._mg_data_click = Mongodb(self._opt.mongodb.data_click)
        self._mg_data_choice = Mongodb(self._opt.mongodb.data_choice)

    def _init(self):
        self.data = dict()
        self.data['cluster'] = 1
        self.data['reco_p_cluster_user'] = [[1.]]
        self.data['reco_user_id_dic'] = {-1: -1}
        self.data['reco_p_item_cluster'] = {k: {-1: 1.} for k in range(self.data['cluster'])}
        if not os.path.exists('cache'):
            os.makedirs('cache')
        if not os.path.exists('cache/demo_gc'):
            os.makedirs('cache/demo_gc')

    def _run(self):
        dic = defaultdict(int)
        for data in self._mg_data_click.find():
            dic[int(data['item_id'])] += 1
        for data in self._mg_data_choice.find():
            dic[int(data['item_id'])] += 1

        self.data['reco_p_item_cluster'] = {k: dic for k in range(self.data['cluster'])}

        self._ps.dump(self.data, 'cache/demo_gc/reco_cluster_user.ps')
        self._ps.dump(self.data, 'cache/demo_gc/reco_item_cluster.ps')

        self._gd.upload(folder='demo_gc',
                        files={'reco_cluster_user.ps': 'cache/demo_gc/reco_cluster_user.ps',
                               'reco_item_cluster.ps': 'cache/demo_gc/reco_item_cluster.ps'},
                        max_data=1)

    def run(self):
        self.logger.info('Start...')
        self._init()
        while True:
            begin_t = time.time()
            # to do
            try:
                self._run()
            except KeyboardInterrupt:
                self.logger.warning('KeyboardInterrupt detect...')
                break
            # finishing
            sleep_t = max(0, 3600 - int(time.time() - begin_t))
            self.logger.info('Sleep {} secs before next start'.format(sleep_t))
            time.sleep(sleep_t)


if __name__ == '__main__':
    Fire(Base_gc)
