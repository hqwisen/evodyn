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

### Game configuration ###

size = 50
# To have a fix number of rounds put the same value for both
last_round = (50, 50)
game = prisoners_dilemma
# start_defect_probability = 1 - start_coop_probability
start_coop_probability = 0.5
# Accepted values: 'moore', 'von_neumann'
neighbor_type = 'von_neumann'
# Accepted values: 'unconditional_imitation'
update_mechanism = 'unconditional_imitation'

### Plot configuration ###

# If False, show only time_visualize steps
time_visualize_all = True
time_visualize = (0, 1, 5, 10, 20, 50)
show_color_bar = False
show_axis = True

### EvoDyn configuration ###

# If True: results directory that already exists is removed, program stop
results_dir_rm = True
