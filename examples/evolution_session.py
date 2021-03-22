
import hanabi_multiagent_framework as hmf
from hanabi_multiagent_framework.utils import make_hanabi_env_config
import numpy as np
from numpy import ndarray
from hanabi_agents.rule_based import ParallelRulebasedAgent
import hanabi_agents.rule_based.predefined_rules as rules
from hanabi_learning_environment import pyhanabi, rl_env
from hanabi_agents.rule_based.ruleset import Ruleset 
from evolve import Evolution
import timeit
import statistics
import dill as pickle
import matplotlib.pyplot as plt
import plotter

## Target for the pickle file
target = 'Experiments/populatation_20.pickle'

load_pickled = False

start_time = timeit.default_timer()

n_players = 2
population_size = 50
n_generations = 10     
n_rules = 10      # Each agent is a list of these many rules
elite_count = int(0.25 * population_size)            # We take 20% of the agents with the best score and retain them 
top_count = int(population_size * (0.2)) #evaluation of percentage of scores for evolution
games_played = 5 #games played per agent

'''
    Total number of games to be played -> Each agent plays 10 games against every other agent
    So, Population * population is one game for each against every other agent and then we multiply 
    it by 10 make it 10 games per agent against every other agent
'''
n_parallel = population_size * games_played

# Initialize the environment
env_conf = make_hanabi_env_config('Hanabi-Full', n_players)
env = hmf.HanabiParallelEnvironment(env_conf, n_parallel)
#print(env_conf)

my_rules = []

if load_pickled == True:
    with open(target, 'rb') as handle:
        loaded_data = pickle.Unpickler(handle).load()['agents']
        loaded_data = np.array(loaded_data)
        if loaded_data.shape[0] == population_size:
            my_rules = loaded_data
        else:
            my_rules = [rules.random_rules(n_rules) for _ in range(population_size)]
else:    
    my_rules = [rules.random_rules(n_rules) for _ in range(population_size)]

my_rules = np.array(my_rules)

experiment_data = {
    'n_players': n_players,
    'n_generations': n_generations,
    'n_rules': n_rules,
    'elite_count': elite_count,
    'current_gen' : 0,
    'agents': [] ,
    'best_agent' : [], 
    'scores' : [], 
    'eval' : 0
}

rule_counter = {}
for rule in rules.big_ruleset:
    rule_name = rule.__name__
    try:
        for x in rule.__closure__[::-1]:
            rule_name = rule_name + "_" + str(x.cell_contents) 
    except:
        pass
    rule_counter[rule_name] = [0,0]
    

# number of generations
for i in range(n_generations):

    scores = []
    for x in rule_counter:
        rule_counter[x] = [0,0]
    

    #agent plays against all the other agents n_parallel times / population_size
    for k in range(population_size):
        agents = [ParallelRulebasedAgent([my_rules[k]],n_parallel), ParallelRulebasedAgent(my_rules,n_parallel)]
        parallel_session = hmf.HanabiParallelSession(env, agents)
        #print("Game config", env.game_config)
        result = parallel_session.run_eval(dest = None, print_intermediate = False)
        #print(result)
        result_average = np.average(np.reshape(result, (-1, games_played )), axis=1)
        #print(result)
        #print("Average: ", result.mean())
        scores.append(result_average)
        #print(agents[0].rule_times)
        for agent in agents[0].rule_times:
            for l  in range(0, len(agent)-1):
                rule_used = agent[l][2] - agent[l+1][2]
                rule_counter[agent[l][0]][1] += rule_used
                rule_counter[agent[l][0]][0] += agent[l][1]
            rule_used = agent[-1][2]
            rule_counter[agent[l][0]][1] += rule_used
            rule_counter[agent[l][0]][0] += agent[l][1]
        #print(rule_counter)

    #discard the the unwanted percentage of scores, this is used for evolution
    scores_sorted = np.sort(scores)[...,::-1]
    scores_sorted = scores_sorted[...,:top_count]
    scores_sorted = list(np.average(scores_sorted, axis = 1))


    print("Gen:", i+1 , "Max:", max(scores_sorted), "Avg_best:", statistics.mean(scores_sorted) , "List:", scores)
    evolution_config = Evolution(my_rules, scores_sorted, elite_count)
    
    target_file = "Experiments/Heatmaps/heatmap_gen_" + str(i+1)
    plotter.plot(scores, target_file)
    target_file = "Experiments/Charts/barchart_gen_" + str(i+1)
    plotter.barchart_rule_count(rule_counter, target_file)

    my_rules = evolution_config.evolve()
    
    best_agent = my_rules[scores_sorted.index(max(scores_sorted))]
    
    # Log the metrics and pickle the current data for checkpointing
    experiment_data['current_gen'] = i + 1
    experiment_data['agents'] = my_rules
    experiment_data['best_agent'] = best_agent
    experiment_data['scores'] = scores

    with open(target, 'wb') as handle:
        pickle.dump(experiment_data, handle)

    stop_time = timeit.default_timer()
    print("Time:" , stop_time - start_time)

# Evaluation of the best agent against te piers agent
agents = [ParallelRulebasedAgent([best_agent]), ParallelRulebasedAgent([rules.piers_rules])]
env = hmf.HanabiParallelEnvironment(env_conf, 100)

parallel_session = hmf.HanabiParallelSession(env, agents)
result = parallel_session.run_eval(dest = None, print_intermediate = False )

print("Evaluation score:", result.mean())

experiment_data['eval'] = result.mean()

with open(target, 'wb') as handle:
    pickle.dump(experiment_data, handle)


stop_time = timeit.default_timer()
print("Time:" , stop_time - start_time)
