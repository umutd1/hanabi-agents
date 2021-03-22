import numpy as np
import random
import hanabi_agents.rule_based.predefined_rules as rules
# import .predefined_rules as rules
#Class for evolving


class Diversity():


    @staticmethod
    def Name_Distance(
        agent_1, 
        agent_2, 
        rulebase
        ) : 

        A = np.array(agent_1)
        B = np.array(agent_2)


        # define the N-Dimensional Axis based on unique rule names
        axes = []

        for rule in rulebase:
            if rule.__name__ not in axes:
                axes.append(rule.__name__)

        axes = np.array(axes)
        
        # Calculate the frequency of the rule occurences in each agent,
        # and define this as a point in this N-dimensional Name space

        A_ = np.zeros(axes.shape[0])
        B_ = np.zeros(axes.shape[0])

        for rule in A: 
            index = np.where(axes == rule.__name__)
            A_[index] += 1
            
        for rule in B: 
            index = np.where(axes == rule.__name__ )
            B_[index] += 1
        
        # A_ = A_ / np.linalg.norm(A_)
        # B_ = B_ / np.linalg.norm(B_)

        # # Calculate the Norm between the two points in this space
        # norm_ = np.linalg.norm(A_ - B_)

        norm_ = 1 - (A_ @ B_) / (np.linalg.norm(A_) * np.linalg.norm(B_))

        return (norm_)

    @staticmethod
    def Name_similarity(A, B):

        pass


    @staticmethod
    def Intra_Agent_Entropy(my_rules):

        # Get the all the unique rule names
        my_rules = np.array(my_rules)

        rule_names = []
        for i in range(my_rules.shape[0]):
            for j in range(my_rules.shape[1]):
                rule_names.append(my_rules[i, j].__name__)

        rule_names = np.unique(rule_names)

        # Create a dictionary of the maximal set of all therules in the ruleset
        names_dict = {}
        for i in rule_names:
            names_dict[i] = 1e-6

        #Copy this maximal dictionary for all agents
        agent_rules = []
        for _ in range(my_rules.shape[0]):
            agent_rules.append(names_dict.copy())

        agent_rules = np.array(agent_rules)

        # Update the frequency of rules in each agent
        for i in range(my_rules.shape[0]):
            rule_list = my_rules[i]
            agent = agent_rules[i]
            for rule in rule_list:
                if agent[rule.__name__] == 1e-6:
                    agent[rule.__name__] = 1

                else:
                    agent[rule.__name__] += 1

        # Normalize to get the Frequentist probability
        agent_probs = []

        for agent in agent_rules:
            agent_probs.append(agent.copy())

        for agent in agent_probs:
            for rule in agent.keys():
                agent[rule] = agent[rule] / my_rules.shape[1]

        # Calculate Entropy based on probabilities
        X = []
        for agent in agent_probs:
            E = 0
            for rules in agent.keys():
                E += - agent[rule] * math.log(agent[rule])

            X.append(E)

        X = np.array(X)

        return X
