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

import time
import timeit
import statistics
import psutil 
import pickle 
import math

## Memory Usage
import tracemalloc

# Pickle Target
target = 'Experiments/Performance_Tests/worker_1_performance.pickle'

# HyperParameters
n_players = 2
population_size = 20
n_generations = 2               
n_rules = 20
elite_count = int(0.2 * population_size)

n_parallel = population_size * population_size            # Starting value of parallel games to b played per generation
# Max_Parallel = 40_000         # Maximum value of parallel games to be played per generation 

# Processes increase by factor of this value while memory increases by a factor of square root 
# of this value
increment = 2

experiment = {
    'n_players' : n_players,  
    'n_generations' : n_generations,
    'n_rules' : n_rules,
    'elite_count' : elite_count, 
    'iter_data' : []
}

with open(target, 'wb') as handle:
    pickle.dump(experiment, handle)


# time_limit = 60               # Number of hours to run 
# time_break = True

# starting_time = time.time()

tracemalloc.start()

try:

    while True:

        # now_time = time.time()
        # elapsed_time = now_time - starting_time
        # if (elapsed_time > time_limit):
        #     print("Time Limit Reached!!")
        #     time_break = False
        #     break

        # Set up the environment    
        env_conf = make_hanabi_env_config('Hanabi-Full', n_players)
        env = hmf.HanabiParallelEnvironment(env_conf, n_parallel)

        #starting population is random
        my_rules = [rules.random_rules(n_rules) for _ in range(population_size)]

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
            time_diff = stop_time - start_time
            # times.append(item)
            print("Time:", stop_time - start_time)

            cpu_usage = psutil.cpu_percent()

            mem_usage = psutil.virtual_memory()

            experiment['iter_data'].append( {
                'population_size': population_size,
                'n_parallel'     : n_parallel,
                'Gen'            : i+1 ,  
                'Avg_Score'      : statistics.mean(scores) ,
                'Max_Score'      : max(scores),
                'Time'           : time_diff,
                'CPU'            : cpu_usage, 
                'Memory'         : mem_usage.percent  
            } )

            with open(target, 'wb') as handle:
                pickle.dump(experiment, handle)

        n_parallel = n_parallel * increment 
        population_size = int(population_size * math.sqrt(increment))

    current, peak = tracemalloc.get_traced_memory()
    print(
        f"Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB"
        )
    tracemalloc.stop()

except KeyboardInterrupt:
    current, peak = tracemalloc.get_traced_memory()
    print(
        f"Current memory usage is {current / 10**6}MB; Peak was {peak / 10**6}MB"
    )
    tracemalloc.stop()
    pass
