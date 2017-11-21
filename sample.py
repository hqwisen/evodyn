###############
#### Games ####
###############

# Payoff matrix (player1, player2)
#      C  |  D
#  ------------
# C | R,R | S,T
# D | T,S | P,P

### Prisoner's dilemma ###
#     C  |  D
#  ------------
# C | 7  |  0
# D | 10 |  0
prisoners_dilemma = {
    'name':  'weak prisoner', # prisoner, snowdrift
    'payoff': (10, 7, 0, 0) # (T, R, P, S)
}
strong_prisoners_dilemma = {
    'name': 'prisoners dilemma',
    'payoff': (10, 7, 5, 0)
}

### Snowdrift Game
#     C  |  D
#  ------------
# C | 7  |  3
# D | 10 |  0

snowdrift_game = {
    'name':  'snowdrift', # prisoner, snowdrift
    'payoff': (10, 7, 0, 3) # (T, R, P, S)
}

##################################
#### Simulation configuration ####
##################################

### Simulation configuation ###

number_of_simulations = 1 

### Game configuration ###

# Matrix sizexsize
size = 50
# Last round is generated randomly between the specified values.
# To have a fix number of rounds put the same value.
# Make sure that the first value is smaller than the second value.
# The numbe of round is the same for all the simulations of the same run.
last_round = (100, 100)
# See defined games above
game = strong_prisoners_dilemma 
# Start method: 'probability', 'middle_cluster'
start_method = 'probability'
# Middle cluster action: C or D
middle_cluster_action = 'C'
# Middle cluster size
middle_cluster_size = 5
# start_defect_probability = 1 - start_coop_probability
start_coop_probability = 0.5
# Accepted values: 'moore', 'von_neumann'
neighbor_type = 'moore'
# Accepted values: 'unconditional_imitation', 'replicator_rule'
update_mechanism = 'unconditional_imitation'

### Matrix plot configuration ###

# If False, show only time_visualize steps
# Note that more you plot, more it takes time!
time_visualize_all = True 
# First t is t0
time_visualize = (1, 5, 10, 20, 50)
show_color_bar = False
show_axis = True

### EvoDyn configuration ###

# Directory name where the simulations plots will be stored
results_dir = "results"
# If set to True and a directory named 'results_dir' exists,
# it will be removed, the program stops otherwise
results_dir_rm = True
