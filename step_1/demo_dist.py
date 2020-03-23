import time
from fire import Fire

from Feynman.etc.util import Config, get_logger
from Feynman.database import Kafka_queue_consumer, Mongodb


class Kafka_dist():
    def __init__(self):
        self.logger = get_logger()
        self._opt = Config(open('config/demo_dist.json').read())
        self._kc_data_center = Kafka_queue_consumer(self._opt.kafka.data_center)
        self._mg_data_click = Mongodb(self._opt.mongodb.data_click)
        self._mg_data_imp = Mongodb(self._opt.mongodb.data_imp)
        self._mg_data_choice = Mongodb(self._opt.mongodb.data_choice)

    def _run(self):
        list_click, list_imp, list_choice = [], [], []
        for data in self._kc_data_center.pop():
            try:
                if data['value']['type'] == 'reco_user_list':
                    for key, value in data['value']['value'].items():
                        for item in list(zip(*value['list']))[0]:
                            temp = {'type': 'reco_user_list',
                                    'user_id': key,
                                    'item_id': str(item),
                                    'stat': 'imp',
                                    'bucket': value['bucket'],
                                    'timestamp': data['value']['timestamp']}
                            list_imp.append(temp)
                elif data['value']['type'] == 'user_feedback':
                    for temp in data['value']['value']:
                        temp['type'] = 'user_feedback'
                        temp['timestamp'] = data['value']['timestamp']
                        if temp['stat'] == 'click':
                            list_click.append(temp)
                        elif temp['stat'] == 'choice':
                            list_choice.append(temp)
            except Exception as e:
                self.logger.info('Somthing is wrong -> {}'.format(e))
                continue
        self._mg_data_click.insert(list_click)
        self._mg_data_imp.insert(list_imp)
        self._mg_data_choice.insert(list_choice)

    def run(self):
        self.logger.info('Start...')
        while True:
            begin_t = time.time()
            # to do
            try:
                self._run()
            except KeyboardInterrupt:
                self.logger.warning('KeyboardInterrupt detect...')
                break
            # finishing
            sleep_t = max(0, 30 - int(time.time() - begin_t))
            self.logger.info('Sleep {} secs before next start'.format(sleep_t))
            time.sleep(sleep_t)


if __name__ == '__main__':
    Fire(Kafka_dist)
