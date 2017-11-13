#!/bin/python3

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import random
import os
import time
import logging
import shutil

log = logging.getLogger('EvoDyn')
logging.basicConfig(level = logging.DEBUG)

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

class SimulationException(Exception):
    pass

class EvoDynUtils:

    @staticmethod
    def mkdir(directory):
        log.info("Creating new '%s' directory" % directory)
        os.mkdir(directory)

    @staticmethod
    def get_config():
        try:
            config = {}
            exec(open("config.py").read(), config)
            # FIXME find another way to parse to avoid del builtins
            del config['__builtins__']
            return config
        except Exception as e:
            log.error("Config Error: ", e)
            exit(1)



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

    def current_counts(self, value):
        return np.count_nonzero(self.current() == value)

    def __str__(self):
        return str(self.l)

    def __repr__(self):
        return str(__self__)

class Simulation:

    def __init__(self, config, simuid = None):
        self.simuid = simuid
        self.config = config
        self.size = config['size']
        self.payoff = self.build_payoff()
        self.rounds = Lattice(self.size)
        self.scores = Lattice(self.size)
        self._number_of_round = random.randint(self.config['last_round'][0],
                                               self.config['last_round'][1])
        self._results_dir = None
        self.t = 0
        self.coop_levels = []
        self.generate_results_dir()

    def build_payoff(self):
        TRPS = self.config['game']['payoff']
        C, D = ACTIONS['C']['value'], ACTIONS['D']['value']
        return {C: {C: TRPS[1], D: TRPS[3]}, \
                D: {C: TRPS[0], D: TRPS[2]}}

    def neighbors(self, i, j):
        if self.config['neighbor_type'] == 'moore':
            return Neighbor.moore(i, j, self.size, self.size)
        elif self.config['neighbor_type'] == 'von_neumann':
            return Neighbor.von_neumann(i, j, self.size, self.size)
        else:
            raise SimulationException("Unknown neighbor_type" \
            ": '%s'" % self.config['neighbor_type'])

    def plot_coop_levels(self):
        log.info("Plot cooperation level in '%s'" % self.results_coop_fig())
        plt.axis([0, self.nround() - 1, 0, 100])
        plt.ylabel('Cooperation level in %')
        plt.xlabel('Rounds')
        plt.plot(self.coop_levels)
        plt.savefig(self.results_coop_fig(), bbox_inches='tight')
        plt.close()


    def plot_current(self):
        """Plot the self.rounds.current() matrix."""
        # NOTE from_level_colors will color blue between 0, 1 and
        # red between 1 and 2, there is maybe a better way for discrete values.
        levels = [0, 1, 2]
        colors = [ACTIONS['C']['color'], ACTIONS['D']['color']]
        cmap, norm = mpl.colors.from_levels_and_colors(levels, colors)
        fig = plt.matshow(self.rounds.current(), cmap=cmap, norm=norm)
        if not self.config['show_axis']:
            fig.axes.get_xaxis().set_visible(False)
            fig.axes.get_yaxis().set_visible(False)
            plt.axis('off')
        if self.config['show_color_bar']:
            plt.colorbar()
        if self.config['time_visualize_all']:
            # print replacing to avoid too much output
            print("\rPlot t{0} {1} ( coop {2}% )".format(self.t,
                self.results_fig(), self.current_coop_percentage()),end=' ')
            if self.t == self.nround() - 1: print()
        else:
            log.debug("Plot t%d in '%s'" % (self.t,self.results_fig()))
        plt.savefig(self.results_fig(), bbox_inches='tight')
        plt.close()

    def nround(self):
        """Return the number of rounds played.
        Based on config.last_round scale."""
        return self._number_of_round

    def generate_results_dir(self):
        """
        Generate the directory name used to store the simulations results.
        If self.simuid is None, the directory will be generated with a
        timestamp.
        """
        self._results_dir = os.path.join(self.config['results_dir'], 'simu_')
        if self.simuid is None:
            self._results_dir +=  time.strftime('%H:%M:%S')
        else:
            self._results_dir += str(self.simuid)
        EvoDynUtils.mkdir(self.results_dir())

    def results_dir(self):
        return self._results_dir

    def results_fig(self):
        return os.path.join(self.results_dir(), 't' + str(self.t))

    def results_coop_fig(self):
        return os.path.join(self.results_dir(), "coop")

    def is_update_mechanism(self, mechanism):
        return self.update_mechanism() == mechanism

    def update_mechanism(self):
        return self.config['update_mechanism']

    def play_random(self):
        """Play cooperate or defect based on config.start_coop_probability."""
        coop_prob = self.config['start_coop_probability']
        choice = np.random.choice(['C', 'D'], p=[coop_prob, 1 - coop_prob])
        return ACTIONS[choice]['value']

    def play_unconditional_imitation(self, i, j):
        previous_score = self.scores.previous()
        previous_round = self.rounds.previous()
        neighbors = self.neighbors(i, j)
        best_action, best_score = previous_round[i, j], previous_score[i, j]
        for ni, nj in neighbors:
            # TODO >= or > for unconditional_imitation
            if previous_score[ni, nj] > best_score:
                best_action = previous_round[ni, nj]
                best_score = previous_score[ni, nj]
        return best_action

    def play_replicator_rule(self, i, j):
        # Following the same notation as the specifications
        # TODO check that it is working as expected
        neighbors = self.neighbors(i, j)
        neighbor, N = random.choice(neighbors), len(neighbors)
        maxpayoff = max(self.config['game']['payoff'])
        minpayoff = min(self.config['game']['payoff'])
        wi, wj = self.scores.previous()[i, j], self.scores.previous()[neighbor]
        p = (1 + (wj - wi) / (N * (maxpayoff - minpayoff))) / 2
        return np.random.choice([self.rounds.previous()[neighbor],
                                 self.rounds.previous()[i, j]], p=[p, 1-p])

    def play_mechanism(self, i, j):
        if self.is_update_mechanism('unconditional_imitation'):
            return self.play_unconditional_imitation(i, j)
        elif self.is_update_mechanism('replicator_rule'):
            return self.play_replicator_rule(i, j)
        else:
            raise SimulationException("Unknown update " \
            "mechanism: '%s'" % self.update_mechanism())

    def play(self, i, j):
        if self.t == 0:
            return self.play_random()
        else:
            return self.play_mechanism(i, j)

    def calculate_score(self, i, j):
        current_round = self.rounds.current()
        neighbors = self.neighbors(i, j)
        score = 0
        player_action = current_round[i, j]
        for ni, nj in neighbors:
            neighbor_action = current_round[ni, nj]
            score += self.payoff[player_action][neighbor_action]
        return score

    def npeople(self):
        """Return the number of people playing the game."""
        return self.size * self.size

    def current_coop_percentage(self):
        ncoop = self.rounds.current_counts(ACTIONS['C']['value'])
        return round((ncoop / self.npeople()) * 100, 2)

    def _run_simulation(self):
        if self.config['time_visualize_all']:
            log.info("All rounds will be plotted")
        for t in range(self.nround()):
            self.t = t
            # FIXME is it necessary to create new matrix for every new round
            # FIXME to much memory used for this
            current_score = self.scores.add_matrix()
            current_round = self.rounds.add_matrix()
            for i in range(self.size):
                for j in range(self.size):
                    current_round[i, j] = self.play(i, j)
            for i in range(self.size):
                for j in range(self.size):
                    current_score[i, j] = self.calculate_score(i, j)
            if self.config['time_visualize_all'] \
            or t in self.config['time_visualize']:
                self.plot_current()
            self.coop_levels.append(self.current_coop_percentage())
        self.plot_coop_levels()
        log.info("Simulation finished!")

    def run(self):
        try:
            self._run_simulation()
        except KeyboardInterrupt:
            log.error("Simulation interupted.")
            exit(130)

class MultipleSimulation:

    def __init__(self, config):
        self.config = config


    def results_dir(self):
        return self.config['results_dir']

    def create_results_dir(self):
        if os.path.exists(self.results_dir()):
            if self.config['results_dir_rm']:
                log.warning("Removing existing directory '%s'"
                % self.results_dir())
                shutil.rmtree(self.results_dir())
            else:
                log.error("Abort. Results directory '" + self.results_dir() +
                "' already exists.")
                exit(1)
        EvoDynUtils.mkdir(self.results_dir())

    def run(self):
        self.create_results_dir()
        start_time = time.time()
        nsimul = self.config['number_of_simulations']
        for simuid in range(nsimul):
            print()
            log.info('Running simluation #%d' % simuid)
            Simulation(self.config, simuid).run()
        print()
        log.info("%d simulations in %d seconds"
                 % (nsimul, time.time() - start_time))

if __name__ == "__main__":
    MultipleSimulation(EvoDynUtils.get_config()).run()
