#!/bin/python3

import numpy

ACTIONS = {
    'C' : {
        'value': 'cooperate',
        'color': 'blue'
    },
    'D' : {
        'value' : 'defect',
        'color' : 'red'
    }
}

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

    def current(self):
        return self.l[-1]

    def __str__(self):
        return str(self.l)

    def __repr__(self):
        return str(__self__)

class Simulation:

    def __init__(self, config):
        self.config = config
        self.size = config['size']
        self.lattice = Lattice(self.size)

    def play_random(self):
        coop_prob = self.config['start_coop_probability']
        return numpy.random.choice(['C', 'D'], p=[coop_prob, 1 - coop_prob])

    def first_round(self):
        current_round = self.lattice.add_depth()
        for i in range(self.size):
            for j in range(self.size):
                current_round[i][j] = self.play_random()

    def run(self):
        print("Running simulation..")
        self.first_round()
        print(self.lattice.current())

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
    Simulation(get_config()).run()
