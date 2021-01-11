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

def make_hanabi_env_config_custom(environment_name="Hanabi-Full", players=2, colors=5, ranks=5, hand_size=5, tokens=8, life=3):
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
n_tokens = 5
n_lives = 2
n_hand_size = 5

n_players = 2
n_parallel = 10

start_time = timeit.default_timer()

#env_conf = make_hanabi_env_config_custom('Hanabi-Full', n_players, n_colors, n_ranks, n_hand_size, n_tokens, n_lives)
env_conf = make_hanabi_env_config('Hanabi-Full', n_players)

#print("Random agent: ", rules.random_agent(5))
#print("PIERS: ", rules.piers_rules)

env = hmf.HanabiParallelEnvironment(env_conf, n_parallel)
#agents_1 = [RulebasedAgent(rules.umuts_rules) for _ in range(n_players)]
#agents_2 = [RulebasedAgent(rules.piers_rules) for _ in range(n_players)]

n_agents = 2
population_size = 4


for i in range(1):
    my_rules = [rules.flawed_rules for _ in range(population_size)]
    my_rules.append(rules.piers_rules)

    my_rules2 = [rules.piers_rules]
    #print(my_rules)
    #print(len(my_rules))
    #agents = [ParallelRulebasedAgent(my_rules, n_agents) for _ in range(n_players)]
    agents = [ParallelRulebasedAgent(my_rules), ParallelRulebasedAgent(my_rules2)]
    parallel_session = hmf.HanabiParallelSession(env, agents)

    print("Game config", env.game_config)
    result = parallel_session.run_eval(dest = None, print_intermediate = False )
    print(result)

    #scores = [10,2,3,5]
    #evolution_config = Evolution(my_rules, scores, elite_count = 1)
    #evolution_config.evolve()
    

stop_time = timeit.default_timer()
print("Time: " , stop_time - start_time)