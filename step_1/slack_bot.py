import os
import sys
import asyncio
from datetime import datetime, timedelta

import websockets
from fire import Fire
from slacker import Slacker

from Feynman.etc.util import Config, get_logger
from Feynman.database import Mongodb


class base():

    def __init__(self):
        self.slack = Slacker(os.environ['SLACK_TOKEN'])
        self.logger = get_logger()
        self.response = self.slack.rtm.start()
        self.endpoint = self.response.body['url']
        self._demo_dist_opt = Config(open('config/demo_dist.json').read())
        self._mg_data_click = Mongodb(self._demo_dist_opt.mongodb.data_click)
        self._mg_data_imp = Mongodb(self._demo_dist_opt.mongodb.data_imp)

    def _time_between(self, st, ed, bucket):
        return {'$and': [
            {'timestamp': {'$gte': st.timestamp()}},
            {'timestamp': {'$lt': ed.timestamp()}},
            {'bucket': bucket}
        ]}

    def _dashboard(self, channal):
        now_t = datetime.now()
        for bucket in self._mg_data_click._collection.distinct('bucket'):
            click = self._mg_data_click.count_documents(self._time_between(now_t-timedelta(hours=1, minutes=0), now_t, bucket))
            imp = self._mg_data_imp.count_documents(self._time_between(now_t-timedelta(hours=1, minutes=0), now_t, bucket))
            self.slack.chat.post_message(channal, 'bucket : {}, ctr : {}'.format(bucket, click/(imp + 0.1)))

    async def _execute_bot(self):
        self.logger.info('start execute_bot')
        while True:
            try:
                self._dashboard('#demo-system-dashboard')
                await asyncio.sleep(3600)
            except Exception as e:
                self.logger.warning('something is wrong... -> {}'.format(e))
                break

    async def _reaction_bot(self):
        self.logger.info('start reaction_bot')
        ws = await websockets.connect(self.endpoint)
        while True:
            try:
                message_json = await ws.recv()
                self.logger.info('get message...')
                message_json = Config(message_json)
                if message_json.text and message_json.subtype != 'bot_message':
                    if '안녕' in message_json.text and '봇' in message_json.text:
                        self.slack.chat.post_message(message_json.channel, '안녕하세요')
                    if 'dashboard' in message_json.text and '봇' in message_json.text:
                        self._dashboard(message_json.channel)
            except Exception as e:
                self.logger.warning('something is wrong...-> {}'.format(e))
                break

    async def _main(self):
        self.logger.info('start process...')
        try:
            await asyncio.gather(
                self._execute_bot(),
                self._reaction_bot()
            )
        except:
            self.logger.warning('something is wrong...')
            sys.exit()

    def run(self):
        asyncio.run(self._main())


if __name__ == '__main__':
    Fire(base)
