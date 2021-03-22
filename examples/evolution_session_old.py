
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

start_time = timeit.default_timer()

games_played = 5 # games played per agent per generation
n_players = 2
population_size = 6
n_rules = 10
elite_count = int(population_size * (0.2))
n_generations = 5
n_parallel = population_size * games_played
top_count = int(population_size * (0.4))
#top_count = 1



env_conf = make_hanabi_env_config('Hanabi-Full', n_players)

env = hmf.HanabiParallelEnvironment(env_conf, n_parallel)

#starting pupulation is random
my_rules = [rules.random_rules(n_rules) for _ in range(population_size-1)]
my_rules.insert(0,rules.piers_rules)

# number of generations
for i in range(n_generations):
    scores = []
    s = []
    
    #with open("agents.txt", "r") as agents_file:
    #    my_rules = list(agents_file.read())
    #print("rules: ", type(my_rules))

    #agent plays against all the other agents
    for k in range(population_size):
        agents = [ParallelRulebasedAgent([my_rules[k]], n_parallel), ParallelRulebasedAgent(my_rules, n_parallel)]
        parallel_session = hmf.HanabiParallelSession(env, agents)
        result = parallel_session.run_eval(dest = None, print_intermediate = False)            
        #print("Average: ", result.mean())
        #print(np.reshape(result, (population_size,-1)))
        #print(result)
        #print("ordered list:", result[0::population_size])
        #print("full list:", result)
        temp = np.average(np.reshape(result, (-1, games_played )), axis=1)
        #print(np.reshape(result, (-1, games_played)))
        #print(temp)
        #print(result)
        scores.append((temp))
        s.append(result.mean())

    print("Scores:", scores)

    avg_tmp = np.average(scores, axis = 1)
    scores_sorted = np.sort(scores)[...,::-1]
    scores_sorted = scores_sorted[...,:top_count]
    scores_sorted = list(np.average(scores_sorted, axis = 1))
    #average of only top scores for the selection of best agents
    #for i in range(top_agents):


    #print(agents[0].rule_times, agents[0].total_time)
    #print(agents[1].rule_times, agents[1].total_time)
    print("average:", avg_tmp)
    print("average_old:" ,scores_sorted)
    print("Max:", np.max(scores), "Avg:", np.average(temp))
    evolution_config = Evolution(my_rules, scores_sorted, elite_count)
    #print("old population: ", my_rules)
    my_rules = evolution_config.evolve()
    #print("new population: ", my_rules)
    best_agent = my_rules[scores_sorted.index(max(scores_sorted))]
    #print("Index:", scores.index(max(scores)))
    
    #with open("agents.txt", "w") as agents_file:
    #    agents_file.write(str(my_rules))
    stop_time = timeit.default_timer()
    print("Time:" , stop_time - start_time)

#evaluation of the best agent
agents = [ParallelRulebasedAgent([best_agent]), ParallelRulebasedAgent([rules.piers_rules])]
#print(best_agent)
env = hmf.HanabiParallelEnvironment(env_conf, 100)
parallel_session = hmf.HanabiParallelSession(env, agents)
result = parallel_session.run_eval(dest = None, print_intermediate = False )
print("Evaluation score:", result.mean())

with open("agents.txt", "w") as f:
    f.write(str(my_rules))
with open("scores.txt", "w") as f:
    f.write(str(scores))


stop_time = timeit.default_timer()
print("Time:" , stop_time - start_time)