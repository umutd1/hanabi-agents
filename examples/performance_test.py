'''
    Experiment to map the the impact of parallel games on the CPU and Memory Usage.
'''


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
import psutil 
import pickle 


# Pickle Target
target = 'Experiments/performance.pickle'

# HyperParameters
n_players = 2
population_size = 200
n_generations = 2               
n_rules = 20
elite_count = 40

n_parallel = 50_000            # Starting value of parallel games to b played per generation
Max_Parallel = 400_000         # Maximum value of parallel games to be played per generation 
increment = 50_000

experiment = {
    'n_players' : n_players, 
    'population_size' : population_size, 
    'n_parallel' : Max_Parallel, 
    'n_generations' : n_generations,
    'n_rules' : n_rules,
    'elite_count' : elite_count, 
    'performance_data' : []
}

# Dictionary to store the data of all generations
performance_data = []

while n_parallel < Max_Parallel + increment:

    # Set up the environment    
    env_conf = make_hanabi_env_config('Hanabi-Full', n_players)
    env = hmf.HanabiParallelEnvironment(env_conf, n_parallel)

    #starting population is random
    my_rules = [rules.random_rules(n_rules) for _ in range(population_size)]

    # Generation List
    gen_list = []

    for i in range(n_generations):

        # Get the start time
        start_time = timeit.default_timer()
        scores = []

        for k in range(population_size):
            
            # Each agent plays against all other agents -> We take the agent and make  
            # it play against a composition of all agents  
            agents = [ParallelRulebasedAgent([my_rules[k]]), ParallelRulebasedAgent(my_rules)]
            
            # Set the parallel sesssion for these 2 agents
            parallel_session = hmf.HanabiParallelSession(env, agents)

            # Evaluate the results
            result = parallel_session.run_eval(dest=None, print_intermediate=False)

            # Append the scores       
            scores.append(result.mean())

        # Print the maximum score
        print("Max:", max(scores), "Avg:", statistics.mean(scores), "List:", scores)

        evolution_config = Evolution(my_rules, scores, elite_count)

        # Evolve the population 
        my_rules = evolution_config.evolve()
        
        # Get the best agent
        best_agent = my_rules[scores.index(max(scores))]
    
        # Get the stop time
        stop_time = timeit.default_timer()
        
        # Calculate the time difference for this generation
        time = stop_time - start_time
        # times.append(item)
        print("Time:", stop_time - start_time)

        cpu_usage = psutil.cpu_percent()

        mem_usage = psutil.virtual_memory()

        gen_list.append ({
            'Gen'    : i+1 ,  
            'Avg' : statistics.mean(scores) ,
            'Max': max(scores),
            'Time'   : time,  
            'CPU'    : cpu_usage, 
            'Memory' : mem_usage.percent  
        } )

    performance_data.append (
        {
            'n_parallel' : n_parallel, 
            'Gen_Data' : gen_list
        }
    )

    n_parallel = n_parallel + increment 

experiment['performance_data'] = performance_data

with open(target, 'wb') as handle:
    pickle.dump(experiment, handle)
