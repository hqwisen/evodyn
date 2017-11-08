#!/bin/python3

import numpy as np
import matplotlib.pyplot as plot
import matplotlib as mpl
import random

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

    def add_matrix(self):
        """Add a numpy.zeros matrix."""
        dims = (self.size, self.size)
        matrix = np.zeros(dims)
        self.l.append(matrix)
        return matrix

    def current(self):
        """Return (current) last matrix."""
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
        self._number_of_round = None

    def play_random(self):
        """Play cooperate or defect based on config.start_coop_probability."""
        coop_prob = self.config['start_coop_probability']
        choice = np.random.choice(['C', 'D'], p=[coop_prob, 1 - coop_prob])
        return ACTIONS[choice]['value']


    def first_round(self):
        """Play the first round randomly."""
        current_round = self.lattice.add_matrix()
        for i in range(self.size):
            for j in range(self.size):
                current_round[i, j] = self.play_random()

    def plot_current(self):
        cmap = mpl.colors.ListedColormap([ACTIONS['C']['color'], \
                                          ACTIONS['D']['color']])
        current = self.lattice.current()
        fig = plot.matshow(current, cmap=cmap)
        fig.axes.get_xaxis().set_visible(False)
        fig.axes.get_yaxis().set_visible(False)
        plot.axis('off')
        plot.savefig('demo.png', bbox_inches='tight')

    def nround(self):
        """Return the number of rounds played.
        Based on config.last_round scale."""
        if self._number_of_round is None:
            self._number_of_round = random.randint(self.config['last_round'][0],
                                                   self.config['last_round'][1])
        return self._number_of_round

    def run(self):
        for t in range(self.nround()):
            print("Round t", t)
        # self.first_round()
        # print(self.lattice.current())
        # print(self.plot_current())

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
