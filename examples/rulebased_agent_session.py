"""
An example with a mock agent on how to operate the framework.
"""
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

def make_hanabi_env_config_custom(environment_name="Hanabi-Custom",players=2, colors=5, ranks=5, hand_size=5, tokens=8, life=3):
    if environment_name in ["Hanabi-Full", "Hanabi-Full-CardKnowledge"]:
        config = {
            "colors":
                colors,
            "ranks":
                ranks,
            "players":
                players,
            "hand_size":
                hand_size,
            "max_information_tokens":
                tokens,
            "max_life_tokens":
                life,
            "observation_type":
                pyhanabi.AgentObservationType.CARD_KNOWLEDGE.value
        }
    else:
        raise ValueError("Unknown environment {}".format(environment_name))
    return {k : str(v) for k, v in config.items()}

n_colors = 2
n_ranks = 5
n_tokens = 3
n_lives = 2
n_hand_size = 3

n_players = 2
n_parallel = 1

start_time = timeit.default_timer()

#env_conf = make_hanabi_env_config_custom('Hanabi-Full', n_players, n_colors, n_ranks, n_hand_size, n_tokens, n_lives)
env_conf = make_hanabi_env_config('Hanabi-Full', n_players)

#print("Random agent: ", rules.random_agent(5))
#print("PIERS: ", rules.piers_rules)

env = hmf.HanabiParallelEnvironment(env_conf, n_parallel)
#agents_1 = [RulebasedAgent(rules.umuts_rules) for _ in range(n_players)]
#agents_2 = [RulebasedAgent(rules.piers_rules) for _ in range(n_players)]

n_agents = 2
population_size = 2

# number of generations
for i in range(1):
    my_rules = [rules.piers_rules for _ in range(population_size-1)]
    #my_rules.insert(0, rules.piers_rules)
    #my_rules2 = [rules.piers_rules]
    scores = []

    #agent plays against all the other agents n_parallel times / population_size
    #for k in range(len(my_rules)):
    for k in range(1):
        #agents = [ParallelRulebasedAgent([my_rules[k]]), ParallelRulebasedAgent(my_rules)]
        agents = [ParallelRulebasedAgent([rules.test_rules]), ParallelRulebasedAgent([rules.piers_rules])]
        parallel_session = hmf.HanabiParallelSession(env, agents)
        #print("Game config", env.game_config)
        result = parallel_session.run_eval(dest = None, print_intermediate = False )
        print(result)
        #print("Average: ", result.mean())
        scores.append(result.mean())
   
    print(agents[0].rule_times, agents[0].total_time)
    print(agents[1].rule_times, agents[1].total_time)
    print(scores)
    #evolution_config = Evolution(my_rules, scores, elite_count = 1)
    #evolution_config.evolve()
    

stop_time = timeit.default_timer()
print("Time: " , stop_time - start_time)