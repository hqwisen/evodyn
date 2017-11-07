#!/bin/python3

import numpy as np
import matplotlib.pyplot as plot

ACTIONS = {
    'C' : {
        'name': 'cooperate',
        # TODO use the colors in the plots
        'color': 'blue',
        'value': 0

    },
    'D' : {
        'name' : 'defect',
        'color' : 'red',
        'value' : 1
    }
}

class Lattice:

    def __init__(self, size):
        self.l = []
        self.size = size

    def add_depth(self):
        dims = (self.size, self.size)
        depth = np.zeros(dims)
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
        choice = np.random.choice(['C', 'D'], p=[coop_prob, 1 - coop_prob])
        return ACTIONS[choice]['value']


    def first_round(self):
        current_round = self.lattice.add_depth()
        for i in range(self.size):
            for j in range(self.size):
                current_round[i, j] = self.play_random()

    def plot_current(self):
        current = self.lattice.current()
        
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
