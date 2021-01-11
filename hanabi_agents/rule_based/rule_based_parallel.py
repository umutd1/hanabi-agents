from .ruleset import Ruleset
from hanabi_learning_environment import pyhanabi_pybind as pyhanabi
import numpy as np
import random


class ParallelRulebasedAgent():

    def __init__(self, rules, parallel_agents = False ):
        #print("Initializing agent")
        self.rules = rules
        #print("nr rules: " + str(len(rules)))
        self.totalCalls = 0
        self.histogram = [0 for i in range(len(rules)+1)]
        
        self.n_agents = len(rules)
        self.agent_turn = -1

        self.agent_id = random.randint(0,100)
        self.total_moves = 0

        #if parallel_agents:
        #    self.parallel_rules = parallel_rules
        #    self.n_parallel = n_parallel
        #    self.agent_turn = 0

    def next_agent(self):
        self.agent_turn = (self.agent_turn +1) % self.n_agents


    def get_move(self, observation):
        if observation.current_player_offset == 0:
            self.next_agent()
            #print(self.rules[self.agent_turn])
            for index, rule in enumerate(self.rules[self.agent_turn]):
                #print("current agent: " + str(self.agent_turn))
                action = rule(observation)
                if action is not None:
                    #self.histogram[index] += 1
                    self.totalCalls += 1
                    return action
            #self.histogram[-1] += 1
            self.totalCalls += 1
            print("random rule exception")
            return Ruleset.legal_random(observation)
        return None

    def explore(self, observations):
        actions = pyhanabi.HanabiMoveVector()
        #print("Current agent:" + str(self.agent_id))
        for observation in observations:
            actions.append(self.get_move(observation))
        #moves = list(map(self.get_move, observations))
        #actions.append(moves)
        return actions

    def exploit(self, observations):
        return self.explore(observations)


    def requires_vectorized_observation(self):
        return False


    def add_experience_first(self, o,  st):
        pass

    def add_experience(self, o, a, r, st):
        pass

    def update(self):
        pass


