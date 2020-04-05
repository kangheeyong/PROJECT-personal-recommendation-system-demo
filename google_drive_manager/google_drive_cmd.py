import cmd

from fire import Fire
from websocket import create_connection


class template_cmd(cmd.Cmd):
    intro = 'This is templete cmd'
    prompt = 'templete_cmd > '
    file = None

    def do_send(self, arg):
        if not arg:
            return
        self._send(arg)

    def _send(self, name):
        uri = "ws://localhost:8765/123"
        ws = create_connection(uri)
        ws.send(name)
        print('> {}'.format(name))
        greeting = ws.recv()
        print('< {}'.format(greeting))
        ws.close()

    def run(self):
        self.cmdloop()

if __name__ == '__main__':
    Fire(template_cmd)
