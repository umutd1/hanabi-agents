from .ruleset import Ruleset
from hanabi_learning_environment import pyhanabi_pybind as pyhanabi
import numpy as np
import random
import timeit


class ParallelRulebasedAgent():

    def __init__(self, rules):
        #print("Initializing agent")
        self.rules = rules
        #print("nr rules: " + str(len(rules)))
        self.totalCalls = 0
        self.histogram = [0 for i in range(len(rules)+1)]
        
        self.n_agents = len(rules)
        self.agent_turn = -1

        self.agent_id = random.randint(0,100)
        self.total_moves = 0

        self.rule_times =[]
        for i in range(self.n_agents):
            self.rule_times.append([])
            for k in range(len(rules[i])):
                self.rule_times[i].append([rules[i][k].__name__ ,0,0])
            #print(len(rules[i]))

        self.total_time = 0
        #print(self.rule_times)

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
                start_time = timeit.default_timer()
                action = rule(observation)
                end_time = timeit.default_timer()
                self.rule_times[self.agent_turn][index][1] += (end_time - start_time) 
                self.rule_times[self.agent_turn][index][2] += 1
                self.total_time += end_time - start_time
                if action is not None:
                    #self.histogram[index] += 1
                    self.totalCalls += 1
                    #print("called rule:", rule)
                    #print("called action: ", action)
                    
                    #print(self.rule_times)
                    return action
            #self.histogram[-1] += 1
            self.totalCalls += 1
            #print("random rule exception")
            return Ruleset.legal_random(observation)
        return None

    def explore(self, observations):
        actions = pyhanabi.HanabiMoveVector()
        #print("Current agent:" + str(self.agent_id))
        for observation in observations:
            actions.append(self.get_move(observation))
        #moves = list(map(self.get_move, observations))
        #actions.append(moves)
        #print(self.rule_times)
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


