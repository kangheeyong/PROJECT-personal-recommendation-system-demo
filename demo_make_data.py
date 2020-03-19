import numpy as np
from fire import Fire

from Feynman.serialize import Pickle_serializer
from Feynman.cloud import Google_drive

np.random.seed(0)


def make_demo_user():

    _ps = Pickle_serializer()
    data = dict()
    data['item_count'] = 100000
    data['user_count'] = 1000000
    data['cluster'] = 8
    data['traffic'] = 200000
    data['timing'] = 15
    data['item_idx'] = [i for i in range(data['item_count'])]
    data['user_idx'] = [u for u in range(data['user_count'])]

    data['p_item_cluster'] = np.random.dirichlet([1 for _ in range(data['cluster'])], data['item_count']).transpose()
    data['p_cluster_user'] = np.random.dirichlet([1 for _ in range(data['cluster'])], data['user_count'])
    data['p_user'] = np.random.dirichlet([1 for _ in range(data['user_count'])], 1)

    _ps.dump(data, 'demo_user.ps')

    _gd = Google_drive()
    _gd.upload(folder='demo_user_data',
               files={'demo_user.ps': 'demo_user.ps'},
               max_data=1)


def make_init_reco():

    _ps = Pickle_serializer()
    data = dict()
    item_count = 100000
    user_count = 1000000
    data['user_count'] = 1000
    data['cluster'] = 8
    data['reco_p_cluster_user'] = np.random.dirichlet([1 for _ in range(data['cluster'])], data['user_count'])
    data['reco_user_id_dic'] = {v: idx for idx, v in enumerate(map(int, np.random.rand(data['user_count'])*user_count))}

    _ps.dump(data, 'reco_cluster_user.ps')

    data = dict()
    demo_count = 1000
    data['cluster'] = 8

    sample = lambda: dict(zip(map(int, np.random.rand(demo_count)*item_count),
                              np.random.dirichlet([1 for _ in range(demo_count)])))
    data['reco_p_item_cluster'] = {k: sample() for k in range(data['cluster'])}

    _ps.dump(data, 'reco_item_cluster.ps')

    _gd = Google_drive()
    _gd.upload(folder='demo_reco',
               files={'reco_cluster_user.ps': 'reco_cluster_user.ps',
                      'reco_item_cluster.ps': 'reco_item_cluster.ps'},
               max_data=1)


if __name__ == '__main__':
    Fire()
