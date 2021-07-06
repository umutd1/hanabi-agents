
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


env_conf = make_hanabi_env_config('Hanabi-Full', 2)

agents = [ParallelRulebasedAgent([rules.test_rules]), ParallelRulebasedAgent([rules.test_rules])]
env = hmf.HanabiParallelEnvironment(env_conf, 100)
parallel_session = hmf.HanabiParallelSession(env, agents)
result = parallel_session.run_eval(dest = None, print_intermediate = False )
print("List:",result)
print("Avg:", result.mean())
print("Max:", max(result))

