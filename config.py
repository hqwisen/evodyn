prisoners_dilemma = {
    'type':  'prisoner', # prisoner, snowdrift
    'payoff': [10, 7, 3, 0] # T, R, P, S
}

snowdrift_game = {
    'type':  'snowdrift', # prisoner, snowdrift
    'payoff': [10, 7, 0, 0] # T, R, P, S
}

config = {
    'size': 50,
    'start_probability': 0.5,
    'game': prisonners_dilemma
    'neighbor_type': 'moore' # moore, von_neumann
    'update_mechanism': 'unconditional_imitation'
    'time_steps': [1, 5, 10, 20, 50]
}
