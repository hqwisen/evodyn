#!/bin/python3

import numpy as np
import matplotlib.pyplot as plot
import matplotlib as mpl
import random
import os
import time
import logging
import shutil

log = logging.getLogger(__name__)

class SimulationException(Exception):
    pass

ACTIONS = {
    'C' : {
        'name': 'cooperate',
        'color': 'blue',
        'value': 0

    },
    'D' : {
        'name' : 'defect',
        'color' : 'red',
        'value' : 1
    }
}

class Neighbor:

    @staticmethod
    def up(r, nrows):
        return r - 1 if r != 0 else (nrows - 1)

    @staticmethod
    def down(r, nrows):
        return r + 1 if r != (nrows - 1) else 0

    @staticmethod
    def left(c, ncols):
        return c - 1 if c != 0 else (ncols - 1)

    @staticmethod
    def right(c, ncols):
        return c + 1 if c != (ncols - 1) else 0

    @staticmethod
    def alldirections(r, c, nrows, ncols):
        """Return direction in the following order: (up, down, left, right)"""
        return Neighbor.up(r, nrows), Neighbor.down(r, nrows), \
               Neighbor.left(c, ncols), Neighbor.right(c, ncols)

    @staticmethod
    def moore(r, c, nrows, ncols):
        up, down, left, right = Neighbor.alldirections(r, c, nrows, ncols)
        return  (up, left), (up, c), (up, right), \
                (r, left), (r, right), \
                (down, left), (down, c), (down, right)

    @staticmethod
    def von_neumann(r, c, nrows, ncols):
        up, down, left, right = Neighbor.alldirections(r, c, nrows, ncols)
        return  (up, c), \
                (r, left), (r, right), \
                (down, c)


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

    def previous(self):
        """Return (previous) before last matrix."""
        return self.l[-2]

    def __str__(self):
        return str(self.l)

    def __repr__(self):
        return str(__self__)

class Simulation:

    def __init__(self, config):
        self.config = config
        self.size = config['size']
        self.lattice = Lattice(self.size)
        self._number_of_round = random.randint(self.config['last_round'][0],
                                               self.config['last_round'][1])
        self._results_dir = None
        self.t = 0
        self.generate_results_dir()

    def plot_current(self):
        cmap = mpl.colors.ListedColormap([ACTIONS['C']['color'], \
                                          ACTIONS['D']['color']])
        current = self.lattice.current()
        fig = plot.matshow(current, cmap=cmap)
        fig.axes.get_xaxis().set_visible(False)
        fig.axes.get_yaxis().set_visible(False)
        plot.axis('off')
        log.warning("Plot t%d in '%s'" % (self.t,self.results_fig()))
        plot.savefig(self.results_fig(), bbox_inches='tight')
        plot.close()

    def nround(self):
        """Return the number of rounds played.
        Based on config.last_round scale."""
        return self._number_of_round

    def generate_results_dir(self):
        # TODO in production use with time
        # self._results_dir = 'results_' + time.strftime('%H:%M:%S')
        self._results_dir = 'results'
        self.create_results_dir()

    def results_dir(self):
        return self._results_dir

    def create_results_dir(self):
        if self.config['results_dir_rm']:
            if os.path.exists(self.results_dir()):
                log.warning("Removing existing directory '%s'"
                 % self.results_dir())
                shutil.rmtree(self.results_dir())
            log.warning("Creating new '%s' directory" % self.results_dir())
            os.mkdir(self.results_dir())
        else:
            print("Abort. Results directory '" + self.results_dir() +
            "' already exists.")
            exit(1)

    def results_fig(self):
        return os.path.join(self.results_dir(), 't' + str(self.t))

    def is_update_mechanism(self, mechanism):
        return self.update_mechanism() == mechanism

    def update_mechanism(self):
        return self.config['update_mechanism']

    def play_random(self):
        """Play cooperate or defect based on config.start_coop_probability."""
        coop_prob = self.config['start_coop_probability']
        choice = np.random.choice(['C', 'D'], p=[coop_prob, 1 - coop_prob])
        return ACTIONS[choice]['value']

    def play_unconditional_imitation(self):
        previous, current =  self.lattice.previous(), self.lattice.current()


    def play_mechanism(self):
        if self.is_update_mechanism('unconditional_imitation'):
            return self.play_unconditional_imitation()
        else:
            raise SimulationException("Unknown update \
            mechanism '%s'" % self.update_mechanism())

    def play(self):
        if self.t == 0:
            return self.play_random()
        else:
            return self.play_mechanism()

    def run(self):
        for t in range(self.nround()):
            self.t = t
            current_round = self.lattice.add_matrix()
            for i in range(self.size):
                for j in range(self.size):
                    current_round[i, j] = self.play()
            if self.config['time_visualize_all'] \
            or t in self.config['time_visualize']:
                self.plot_current()

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
