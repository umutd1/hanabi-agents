
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

n_players = 2
n_parallel = 10 # n_paralllel / population size = games played by each agent against all the other agents
population_size = 10
n_rules = 20
elite_count = 3



env_conf = make_hanabi_env_config('Hanabi-Full', n_players)

env = hmf.HanabiParallelEnvironment(env_conf, n_parallel)

#starting pupulation is random
my_rules = [rules.random_rules(n_rules) for _ in range(population_size)]
#print(my_rules)
#with open("agents.txt", "w") as f:
#    f.write(str(my_rules))

# number of generations
for i in range(10):
    scores = []
    
    #with open("agents.txt", "r") as agents_file:
    #    my_rules = list(agents_file.read())
    #print("rules: ", type(my_rules))

    #agent plays against all the other agents n_parallel times / population_size
    for k in range(population_size):
        agents = [ParallelRulebasedAgent([my_rules[k]]), ParallelRulebasedAgent(my_rules)]
        parallel_session = hmf.HanabiParallelSession(env, agents)
        #print("Game config", env.game_config)
        result = parallel_session.run_eval(dest = None, print_intermediate = False)
        #print(result)
        #print("Average: ", result.mean())
        scores.append(result.mean())
   
    #print(agents[0].rule_times, agents[0].total_time)
    #print(agents[1].rule_times, agents[1].total_time)
    print("Max:", max(scores), "Avg:", statistics.mean(scores) , "List:", scores)
    evolution_config = Evolution(my_rules, scores, elite_count)
    #print("old population: ", my_rules)
    my_rules = evolution_config.evolve()
    #print("new population: ", my_rules)
    best_agent = my_rules[scores.index(max(scores))]
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