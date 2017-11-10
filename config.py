# Payoff matrix (player1, player2)
#      C  |  D
#  ------------
# C | R,R | S,T
# D | T,S | P,P

prisoners_dilemma = {
    'name':  'weak prisoner', # prisoner, snowdrift
    'payoff': (10, 7, 0, 0) # (T, R, P, S)
}

snowdrift_game = {
    'name':  'snowdrift', # prisoner, snowdrift
    'payoff': (10, 7, 0, 3) # (T, R, P, S)
}

size = 50
start_coop_probability = 0.5 # start_defect_prob = 1 - start_coop_prob
game = prisoners_dilemma
neighbor_type = 'moore' # moore, von_neumann
# update_mechanism is: 'unconditional_imitation'
update_mechanism = 'unconditional_imitation'
time_visualize_all = False # If False, show only time_visualize steps
time_visualize = (0, 1, 5, 10, 20, 50)
last_round = (10, 10) # To fix the size, put the same value for both
 # If True: results directory that already exists is removed, program stop
results_dir_rm = True
