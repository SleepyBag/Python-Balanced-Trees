import random
import time
from matplotlib import pyplot as plt
from B import BTree
from RedBlack import RedBlackTree
from Splay import SplayTree


def timing(func, *args, **kwargs):
    tic = time.perf_counter()
    func(*args, **kwargs)
    toc = time.perf_counter()
    return toc - tic


def experiment_insert_delete_insert(arr, tree):
    delete = arr[:len(arr) // 2]
    for _, a in enumerate(arr):
        tree.insert(a)
        while delete and tree.has_val(delete[-1]):
            deleted = delete.pop()
            tree.delete(deleted)


def experiment_insert(arr, tree):
    for _, a in enumerate(arr):
        tree.insert(a)


def experiment_one_round(expriment_func, experiment_name):
    arrs = []
    lens = [100, 1000, 2000, 5000, 10000, 20000, 30000, 40000, 50000]
    for n in lens:
        arr = [i for i in range(-n, n)]
        random.shuffle(arr)
        arrs.append(arr)

    tree_factories = {
        'splay': lambda: SplayTree(),
        'red-black': lambda: RedBlackTree(),
        '2-3-4': lambda: BTree(2),
        'B-tree (degree 8)': lambda: BTree(4),
        'B-tree (degree 16)': lambda: BTree(8),
    }
    for tree_name in tree_factories:
        durations = []
        for arr in arrs:
            tree = tree_factories[tree_name]()
            print(experiment_name, tree_name, 'with', len(arr), 'elements...')
            duration = timing(expriment_func, arr, tree)
            durations.append(duration)
            print('Finished with', duration)
        plt.plot([l * 2 for l in lens], durations, label=tree_name)
    plt.xlabel('number of inserted elements')
    plt.ylabel('time (seconds)')
    plt.legend()
    plt.savefig(experiment_name)
    plt.clf()

experiment_one_round(experiment_insert, 'benchmark-insert')
experiment_one_round(experiment_insert_delete_insert, 'benchmark-insert-delete-insert')