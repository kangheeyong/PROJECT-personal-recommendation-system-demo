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
            print_tree(key,
                       adj_dic,
                       func=lambda x: '{}({}) - {}'
                       .format(data_dic[x]['name'], data_dic[x]['id'], data_dic[x]['createdTime']))
            print('')

    def do_ls(self, arg):
        root = self._send('root', arg)
        data_dic = self._send('data_dic', arg)
        view_dic = self._send('view_dic', arg)
        print_tree(root,
                   view_dic,
                   func=lambda x: '{}({}) - {}'
                   .format(data_dic[x]['name'], data_dic[x]['id'], data_dic[x]['createdTime']))
        print('')

    def do_info_id(self, arg):
        data_dic = self._send('data_dic', arg)
        if arg not in data_dic:
            print('Can not find id')
        else:
            print(data_dic[arg])
        print('')

    def do_remove_list(self, arg):
        data_dic = self._send('data_dic', arg)
        remove_list = self._send('remove_list', arg)
        for x in remove_list:
            print('{}({}) - {}'.format(data_dic[x]['name'], data_dic[x]['id'], data_dic[x]['createdTime']))
        print('')

    def do_upload(self, arg):
        print('not yet', arg)

    def do_download(self, arg):
        print('not yet')

    def do_mkdir(self, arg):
        print('not yet')

    def do_remove(self, arg):
        result = self._send('remove', arg)
        print(result)
        print('')

    def do_empty_remove_list(self, arg):
        result = self._send('empty_list', arg)
        print(result)
        print('')

    def _send(self, cmd, arg):
        uri = 'ws://localhost:8765/'+cmd
        try:
            ws = create_connection(uri)
            ws.send(arg)
            result = ws.recv()
            ws.close()
        except Exception as e:
            print(e)
            return []
        return json.loads(result)

    def run(self):
        self.cmdloop()

if __name__ == '__main__':
    Fire(template_cmd)
