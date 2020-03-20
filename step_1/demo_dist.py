import time
from fire import Fire

from Feynman.etc.util import Config, get_logger
from Feynman.database import Kafka_queue_producer, Kafka_queue_consumer


class Kafka_dist():
    def __init__(self):
        self.logger = get_logger()
        self._opt = Config(open('config/demo_dist.json').read())
        self._kc_data_center = Kafka_queue_consumer(self._opt.data_center)
        self._kp_data_feedback = Kafka_queue_producer(self._opt.data_feedback)
        self._kp_data_monitoring = Kafka_queue_producer(self._opt.data_monitoring)

    def _run(self):
        list_monitoring, list_feedback = [], []
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
                                    'datatime': data['datatime']}
                            list_monitoring.append(temp)
                elif data['value']['type'] == 'user_feedback':
                    for temp in data['value']['value']:
                        temp['type'] = 'user_feedback'
                        temp['datatime'] = data['datatime']
                        if temp['stat'] == 'click':
                            list_monitoring.append(temp)
                            list_feedback.append(temp)
                        elif temp['stat'] == 'choice':
                            list_feedback.append(temp)
            except Exception as e:
                self.logger.info('Somthing is wrong -> {}'.format(e))
                continue
        self._kp_data_monitoring.push(list_monitoring)
        self._kp_data_feedback.push(list_feedback)

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
