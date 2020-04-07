import cmd

import json
from fire import Fire
from websocket import create_connection

from Feynman.algorithms.tree.print_tree import print_tree


class template_cmd(cmd.Cmd):
    intro = '''
this is google drive manager
version 0.0.1
            '''
    prompt = 'google_drive > '
    file = None

    def do_all(self, arg):
        all_dic = self._send('all_dic', arg)
        data_dic = self._send('data_dic', arg)
        adj_dic = self._send('adj_dic', arg)
        for key in all_dic.keys():
            print_tree(key, adj_dic)

    def do_ls(self, arg):
        root = self._send('root', arg)
        data_dic = self._send('data_dic', arg)
        adj_dic = self._send('adj_dic', arg)
        print_tree(root, adj_dic)

    def do_upload(self, arg):
        print('not yet')

    def do_download(self, arg):
        print('not yet')

    def _send(self, cmd, arg):
        uri = 'ws://localhost:8765/'+cmd
        ws = create_connection(uri)
        ws.send(arg)
        result = ws.recv()
        ws.close()
        return json.loads(result)

    def run(self):
        self.cmdloop()

if __name__ == '__main__':
    Fire(template_cmd)