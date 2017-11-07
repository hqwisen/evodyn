#!/bin/python3

class Lattice:

    def __init__(self, size):
        self.l = []
        self.size = size

    def add_depth(self):
        depth = []
        for i in range(self.size):
            depth.append([])
            for j in range(self.size):
                depth[i].append(None)
        self.l.append(depth)
        return depth

    def __str__(self):
        return str(self.l)

    def __repr__(self):
        return str(__self__)


def get_config():
    try:
        config = {}
        exec(open("config.py").read(), config)
        # FIXME find another way to parse to avoid del builtins
        del config['__builtins__']
        return config
    except Exception as e:
        print("Config Error: ", e)

if __name__ == "__main__":
    config = get_config()
    print(config)
    l = Lattice(2)
    l.add_depth()
    l.add_depth()
    print(l)
