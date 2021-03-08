
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

## Target for the pickle file
target = 'Experiments/Div_Add/Diversity_Test_10_agents_br_0.3_top_0.3.pickle'

load_pickled = False

start_time = timeit.default_timer()

n_players = 2
population_size = 10
n_generations = 100     
n_rules = 20      # Each agent is a list of these many rules
elite_count = int(0.3 * population_size)            # We take 20% of the agents with the best score and retain them 

'''
    Total number of games to be played -> Each agent plays 10 games against every other agent
    So, Population * population is one game for each against every other agent and then we multiply 
    it by n_games_per_pair to account for games per agent against every other agent
'''
n_games_per_pair = 10
n_parallel =  population_size * n_games_per_pair

top_x = 0.3
top_count = int(top_x * n_parallel)  

alpha = 0.3

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
    'scores' : np.zeros(population_size), 
    'eval' : 0
}

# Initialize the environment
env_conf = make_hanabi_env_config('Hanabi-Full', n_players)
env = hmf.HanabiParallelEnvironment(env_conf, n_parallel)

# For each generation, start the games
for i in range(n_generations):
    scores = []

    # Agent plays against all the other agents n_parallel times / population_size
    # But this happens sequentially -> TODO: Parallelize this loop 
    for k in range(population_size):
        # For each agent in the population, create a second agent composed of all other agents
        agents = [ParallelRulebasedAgent([my_rules[k]]), ParallelRulebasedAgent(my_rules)]

        # Start a parallel session with these two agents and pass the number of games to be played between 
        # them as the environment config
        parallel_session = hmf.HanabiParallelSession(env, agents)

        # Get the result and append the scores
        result = parallel_session.run_eval(dest = None, print_intermediate = False)
        # print(f"Shape of Result ----> {np.array(result).shape} ")
        
        result = np.array(result)
        # result = result / n_games_per_pair

        scores.append(np.mean(np.sort(result)[-top_count:]))

    # Average the scores from the games each agent plays against each other agent 
    scores = np.array(scores)
    # scores = scores / n_games_per_pair

    # Print some values for sanity check
    print("Gen:", i+1 , "Max:", np.max(scores), "Avg:", np.mean(scores) , "List:", scores)
    
    # Pass the current list of agents for the evolution magic and get the new evolved agnets
    evolution_config = Evolution(
        current_population=my_rules, 
        scores=scores, 
        elite_count=elite_count,
        mutation_rate=0.1, 
        tournament_size=1, 
        balance_ratio=alpha
        )
    my_rules = evolution_config.evolve()
    
    # Get the best agent as the index of the first instance of the highest value 
    best_agent = my_rules[np.argmax(scores)]
    
    # Log the metrics and pickle the current data for checkpointing
    experiment_data['current_gen'] = i + 1
    experiment_data['agents'] = my_rules
    experiment_data['best_agent'] = best_agent
    experiment_data['scores'] = np.vstack((experiment_data['scores'], scores))

    print(experiment_data['scores'].shape)

    # Pickle the log
    with open(target, 'wb') as handle:
        pickle.dump(experiment_data, handle)

    stop_time = timeit.default_timer()
    print("Time:" , stop_time - start_time)

# Evaluation of the best agent against the piers agent
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
