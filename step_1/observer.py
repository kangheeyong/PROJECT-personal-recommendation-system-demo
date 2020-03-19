import os
import sys
import time

from fire import Fire
from slacker import Slacker


class base():
    def __init__(self):
        self.slack = Slacker(os.environ['SLACK_TOKEN'])
        self.response = self.slack.rtm.start()
        self.endpoint = self.response.body['url']

    def write_stdout(self, s):
        sys.stdout.write(s)
        sys.stdout.flush()

    def run(self):
        while True:
            try:
                self.write_stdout('READY\n')
                line = sys.stdin.readline()
                headers = dict([x.split(':') for x in line.split() if len(x.split(':')) == 2])
                if 'processname' in headers:
                    data = '[WARNING]\n - process name : {}\n - state : {} -> {}\n - time : {}'\
                           .format(headers['processname'], headers['from_state'], headers['eventname'], time.ctime())
                    self.slack.chat.post_message('#warning-bot', data)
                self.write_stdout('RESULT 2\nOK')
            except Exception as e:
                self.slack.chat.post_message('#warning-bot', '[WARNING]\n - obsever.py Unexpected exit -> {}'.format(e))
                break

if __name__ == '__main__':
        Fire(base)
