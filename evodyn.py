#!/bin/python3

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import random
import os
import time
import logging
import shutil

# Specify backend, to allow usage from terminal
plt.switch_backend('agg')
# Logger
log = logging.getLogger('EvoDyn')
logging.basicConfig(level=logging.DEBUG)

ACTIONS = {
    'C': {
        'name': 'cooperate',
        'color': 'blue',
        'value': 0

    },
    'D': {
        'name': 'defect',
        'color': 'red',
        'value': 1
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
            exec(open("sample.py").read(), config)
            # FIXME find another way to parse to avoid del builtins
            del config['__builtins__']
            return config
        except FileNotFoundError:
            print("Error: no 'config.py' file found.")
            exit(1)
        except Exception as e:
            log.error("Config Error: ", e)
            exit(1)

    @staticmethod
    def plot(fig, data, axis, xlabel, ylabel, message=None):
        if message is None:
            message = "Plot x: %s; y:%s" % (xlabel, ylabel)
        log.info("%s in '%s'" % (message, fig))
        plt.axis(axis)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.plot(data)
        plt.savefig(fig, bbox_inches='tight')
        plt.close()

    def opposite_action(action):
        if action == 'D':
            return 'C'
        elif action == 'C':
            return 'D'


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
        return (up, left), (up, c), (up, right), \
               (r, left), (r, right), \
               (down, left), (down, c), (down, right)

    @staticmethod
    def von_neumann(r, c, nrows, ncols):
        up, down, left, right = Neighbor.alldirections(r, c, nrows, ncols)
        return (up, c), \
               (r, left), (r, right), \
               (down, c)


Neighbor.MOORE_NUMBER_OF_NEIGHBORS = 8


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

    def reset_current(self):
        """To avoid using too much memory, this method will:
        - remove the previous matrix
        - set the previous matrix as current,
        - and current set to a new zeros matrix.
        This should usually be used when only
        two matrix remains in the lattice.
        """
        self.l[-2] = self.l[-1]  # previous = current
        self.l[-1] = np.zeros((self.size, self.size))
        return self.current()

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
        return str(self)


class Simulation:

    def __init__(self, config, simuid=None):
        self.simuid = simuid
        self.config = config
        self.size = self.config['size']
        self._results_dir = None
        self.t = 0
        self._data = self.init_data()
        self.rounds, self.scores, self.thresholds = self.init_lattices()
        self.init_actions = np.zeros((self.size, self.size))
        self.intuitive_actions = Lattice(self.size)
        self.generate_results_dir()

    def data(self, key=None):
        return self._data if key is None else self._data[key]

    def init_data(self):
        return {
            'coop_levels': list()
        }

    def init_lattices(self):
        rounds, scores, thresholds = Lattice(self.size),\
                                     Lattice(self.size), Lattice(self.size)
        # Create current and previous matrix,
        # to be used with Lattice.reset_current()
        rounds.add_matrix()
        rounds.add_matrix()
        scores.add_matrix()
        scores.add_matrix()
        thresholds.add_matrix()
        thresholds.add_matrix()
        return rounds, scores, thresholds

    def build_payoff(self):
        if self.config['simulation_type'] == 'assign2':
            TRPS = self.config['game']['payoff']
            C, D = ACTIONS['C']['value'], ACTIONS['D']['value']
            return {C: {C: TRPS[1], D: TRPS[3]},
                    D: {C: TRPS[0], D: TRPS[2]},
                    'name': self.config['game']['name']}
        elif self.config['simulation_type'] == 'gamma':
            gamma_p = self.config['gamma_p']
            choice = np.random.choice([0, 1], p=[1 - gamma_p, gamma_p])
            game = self.config['gamma'][choice]
            TRPS = game['payoff']
            C, D = ACTIONS['C']['value'], ACTIONS['D']['value']
            return {C: {C: TRPS[1], D: TRPS[3]},
                    D: {C: TRPS[0], D: TRPS[2]},
                    'name': game['name']}
        else:
            raise SimulationException("Cannot build payoff "
                                      "for simulation_type %s" %
                                      self.config['simulation_type'])

    def neighbors(self, i, j):
        if self.config['neighbor_type'] == 'moore':
            return Neighbor.moore(i, j, self.size, self.size)
        elif self.config['neighbor_type'] == 'von_neumann':
            return Neighbor.von_neumann(i, j, self.size, self.size)
        else:
            raise SimulationException("Unknown neighbor_type" \
                                      ": '%s'" % self.config['neighbor_type'])

    def plot_coop_levels(self):
        message = "Plot cooperation level"
        axis = [0, self.nround() - 1, 0, 100]
        xlabel, ylabel = 'Rounds', 'Cooperation level in %'
        EvoDynUtils.plot(self.results_coop_fig(), self.data('coop_levels'),
                         axis, xlabel, ylabel, message)

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
                                                         self.results_fig(),
                                                         self.current_coop_percentage()), end=' ')
            if self.t == self.nround() - 1: print()
        else:
            log.debug("Plot t%d in '%s'" % (self.t, self.results_fig()))
        plt.savefig(self.results_fig(), bbox_inches='tight')
        plt.close()

    def nround(self):
        """Return the number of rounds played.
        Based on config.last_round scale."""
        return self.config['number_of_round']

    def generate_results_dir(self):
        """
        Generate the directory name used to store the simulations results.
        If self.simuid is None, the directory will be generated with a
        timestamp.
        """
        self._results_dir = os.path.join(self.config['results_dir'], 'simu_')
        if self.simuid is None:
            self._results_dir += time.strftime('%H:%M:%S')
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

    def play_random(self, return_action=False):
        """Play cooperate or defect based on config.start_coop_probability."""
        coop_prob = self.config['start_coop_probability']
        choice = np.random.choice(['C', 'D'], p=[coop_prob, 1 - coop_prob])
        if return_action:
            return choice
        else:
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

    def play_unconditional_imitation_with_threshold(self, i, j):
        previous_score = self.scores.previous()
        previous_round = self.rounds.previous()
        previous_threshold = self.thresholds.previous()
        neighbors = self.neighbors(i, j)
        best_action, best_score = previous_round[i, j], previous_score[i, j]
        best_threshold = previous_threshold[i, j]
        for ni, nj in neighbors:
            # TODO >= or > for unconditional_imitation
            if previous_score[ni, nj] > best_score:
                best_action = self.intuitive_actions.previous()[ni, nj]
                best_score = previous_score[ni, nj]
                best_threshold = previous_threshold[ni, nj]
        return best_action, best_threshold

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
                                 self.rounds.previous()[i, j]], p=[p, 1 - p])

    def play_mechanism(self, i, j):
        if self.is_update_mechanism('unconditional_imitation'):
            return self.play_unconditional_imitation(i, j)
        elif self.is_update_mechanism('replicator_rule'):
            return self.play_replicator_rule(i, j)
        else:
            raise SimulationException("Unknown update " \
                                      "mechanism: '%s'" % self.update_mechanism())

    def play_middle_cluster(self, i, j):
        cluster_action = self.config['middle_cluster_action']
        if self.config['random_cluster']:
            action = self.play_random(return_action=True)
        else:
            action = cluster_action
        oppaction = EvoDynUtils.opposite_action(cluster_action)
        cluster_size = self.config['middle_cluster_size']
        center = self.size // 2
        cluster = range(center - cluster_size, center + cluster_size)
        if i in cluster and j in cluster:
            return ACTIONS[action]['value']
        return ACTIONS[oppaction]['value']

    def play_first(self, i, j):
        if self.config['start_method'] == 'probability':
            return self.play_random()
        elif self.config['start_method'] == 'middle_cluster':
            return self.play_middle_cluster(i, j)
        else:
            raise SimulationException("Unknown start " \
                                      "method: '%s'" % self.config['start_method'])

    def play_gamma_first(self):
        a, b = self.config['threshold_dist']
        return self.play_random(), np.random.uniform(a, b)

    def generate_cost(self):
        a, b = self.config['cost_dist']
        z = np.random.uniform(a, b)
        return 1 - (1 / (1 + z) ** 4)

    def deliberate_action(self):
        if self.payoff['name'] == 'coordination game':
            return ACTIONS['C']['value']
        elif self.payoff['name'] == 'prisoners dilemma':
            return ACTIONS['D']['value']
        else:
            raise SimulationException("Unknown game name: %s" % self.payoff['name'])

    def play(self, i, j):
        if self.config['simulation_type'] == 'gamma':
            return self.play_gamma(i, j)
        elif self.t == 0:
            return self.play_first(i, j)
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

    def gather_current_data(self):
        self._data['coop_levels'].append(self.current_coop_percentage())

    def _run_simulation_assign2(self):
        log.info("Starting 'assign2' simulation")
        self.payoff = self.build_payoff()
        if self.config['time_visualize_all']:
            log.info("All rounds will be plotted")
        for t in range(self.nround()):
            self.t = t
            current_score = self.scores.reset_current()
            current_round = self.rounds.reset_current()
            for i in range(self.size):
                for j in range(self.size):
                    current_round[i, j] = self.play(i, j)
            for i in range(self.size):
                for j in range(self.size):
                    current_score[i, j] = self.calculate_score(i, j)
            if self.config['time_visualize_all'] \
                    or t in self.config['time_visualize']:
                self.plot_current()
            self.gather_current_data()
        self.plot_coop_levels()
        log.info("Simulation finished!")

    def play_gamma(self, i, j):
        if self.t == 0:
            action_and_thres = self.play_gamma_first()
            return action_and_thres
        else:
            action, threshold = self.play_unconditional_imitation_with_threshold(i, j)
            return action, threshold

        # if self.cost <= thresholds[i, j]:
        #     current_score = self.scores.reset_current()
        #     current_score[i, j] -= self.cost * Neighbor.MOORE_NUMBER_OF_NEIGHBORS
        #     action = self.deliberate_action()
        # else:
        #     action = self.init_actions[i, j]

        # if cost <= T:
        #     rewardij -= cost
        #     choice([C, D], [p, 1 - p])  # prob p to be in gamma1 i.e. play C
        #     return choice
        # else:
        #     # return self.play_unconditional_imitation(i, j)
        #     return self.play_random()

    def play_deliberate(self, i, j):
        thresholds = self.thresholds.current()
        if self.cost <= thresholds[i, j]:
            current_score = self.scores.current()
            current_score[i, j] -= self.cost * Neighbor.MOORE_NUMBER_OF_NEIGHBORS
            action = self.deliberate_action()
        else:
            action = self.intuitive_actions.current()[i, j]
        return action

    def _run_simulation_gamma(self):
        log.info("Starting 'gamma' simulation")
        if self.config['time_visualize_all']:
            log.info("All rounds will be plotted")
        for t in range(self.nround()):
            # Update gamma game
            self.payoff = self.build_payoff()
            # log.info("Game for round %d: %s" % (t, self.payoff['name']))
            self.t = t
            self.cost = self.generate_cost()
            current_score = self.scores.reset_current()
            current_round = self.rounds.reset_current()
            current_threshold = self.thresholds.reset_current()
            current_int_actions = self.intuitive_actions.add_matrix()
            for i in range(self.size):
                for j in range(self.size):
                    current_int_actions[i, j], current_threshold[i, j] \
                        = self.play_gamma(i, j)
                    current_round[i, j] = self.play_deliberate(i, j)
                    current_score[i, j] = self.calculate_score(i, j)

            if self.config['time_visualize_all'] \
                    or t in self.config['time_visualize']:
                self.plot_current()
            self.gather_current_data()
        self.plot_coop_levels()
        log.info("Simulation finished!")

    def run(self):
        try:
            runs = {
                'gamma': getattr(self, '_run_simulation_gamma'),
                'assign2': getattr(self, '_run_simulation_assign2')
            }
            if self.config['simulation_type'] not in runs:
                raise SimulationException("Unknown simulation type %s" %
                                          self.config['simulation_type'])
            runs[self.config['simulation_type']]()
        except KeyboardInterrupt:
            log.error("Simulation interupted.")
            exit(130)


class MultipleSimulation:

    def __init__(self, config):
        self.config = config
        self.nsimul = self.config['number_of_simulations']
        self.all_data = []
        self.generate_number_of_round()

    def generate_number_of_round(self):
        self.config['number_of_round'] = random.randint(
            self.config['last_round'][0],
            self.config['last_round'][1])

    def results_dir(self):
        return self.config['results_dir']

    def results_coop_fig(self):
        return os.path.join(self.results_dir(), 'average_coop')

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

    def plot_average_coop_levels(self):
        nround = self.config['number_of_round']
        average_coop_levels = [0 for r in range(nround)]
        for s in range(self.nsimul):
            for r in range(nround):
                average_coop_levels[r] += self.all_data[s]['coop_levels'][r]
        for r in range(nround):
            average_coop_levels[r] = average_coop_levels[r] / self.nsimul
        message = "Plot average cooperation levels for %s simulations" \
                  % (self.nsimul)
        xlabel, ylabel = "Rounds", "Average coop. level for %s simulations" \
                         % (self.nsimul)
        axis = [0, nround - 1, 0, 100]
        EvoDynUtils.plot(self.results_coop_fig(), average_coop_levels,
                         axis, xlabel, ylabel, message)

    def _run_simu(self, simuid):
        print()
        log.info('Running simluation #%d' % simuid)
        simu = Simulation(self.config, simuid)
        simu.run()
        self.all_data.append(simu.data())

    def run(self):
        self.create_results_dir()
        start_time = time.time()
        for simuid in range(self.nsimul):
            self._run_simu(simuid)
        self.plot_average_coop_levels()
        print()
        log.info("%d simulations in %d seconds"
                 % (self.nsimul, time.time() - start_time))


if __name__ == "__main__":
    MultipleSimulation(EvoDynUtils.get_config()).run()
