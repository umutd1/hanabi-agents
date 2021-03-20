import numpy as np
import random
import hanabi_agents.rule_based.predefined_rules as rules
from hanabi_agents.rule_based.Diversity import Diversity

#Class for evolving
class Evolution:


    def __init__(self, 
                current_population, 
                scores,
                rulebase = rules.big_ruleset, 
                elite_count = 3,
                mutation_rate = 0.1, 
                tournament_size = 1, 
                alpha = 0.1,
                top_x = 0.2 
                ):
        
        self.top_x = top_x
        self.alpha = alpha
        self.current_population = np.array(current_population)
        self.scores = scores
        self.rulebase = rulebase
        self.population_size = len(current_population)
        self.rule_size = len(current_population[0])
        #print("Rule size: " + str(self.rule_size))
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size
        self.crossover_count = len(current_population) - elite_count
        self.elite_count = elite_count
        self.next_population = []
    
    #Evolution steps:
    #1 - Taking elites directly to next generation
    #2 - Selection for crossover
    #3 - Crossover
    #4 - Mutation
    #5 - Optional: Implementing Threshhold for saving good agents

    #currently random selection
    def crossover_selection(self):
        population_random = self.current_population.copy()
        random.shuffle(population_random)
        return population_random[:self.crossover_count]

    def crossover(self,crossover_list ,agent_list):
        for i in range(len(crossover_list)):
            new_agent = []
            random_index = random.randrange(0, len(crossover_list))
            while random_index == i:
                random_index = random.randrange(0, len(crossover_list))
                #print("Random index is same")
            for k in range(self.rule_size):
                roll = random.randint(0,1)
                if roll == 0:
                    new_agent.append(crossover_list[i][k])
                else:
                    new_agent.append(crossover_list[random_index][k])
            agent_list.append(new_agent)

    def mutate(self):
        ruleset = rules.big_ruleset
        for i in range(self.elite_count, self.population_size):
            for k in range(len(self.next_population[i])):
                roll_mutation = random.random()
                if(roll_mutation < self.mutation_rate):
                    #print("Mutation...")
                    roll_swap = random.randint(0,len(ruleset)-1)
                    self.next_population[i][k] = ruleset[roll_swap]

    def calculate_fitness(self):
        
        # Scores is a 2D array for average socres of each agent against each other agent

        performances = np.zeros((self.scores.shape[0], self.scores.shape[1]))

        D_list = np.zeros((self.scores.shape[0], self.scores.shape[1]))

        Diversities = np.zeros((self.scores.shape[0]))

        for i in range(self.scores.shape[0]):
            
            diversity = np.zeros((self.scores.shape[1]))
            
            for j in range(self.scores.shape[1]):
                
                div = Diversity.Name_Distance(  self.current_population[i],
                                                self.current_population[j],
                                                self.rulebase)

                diversity[j] = div
                
                d_i_j = self.scores[i, j] + self.alpha * div 
                performances[i, j] = d_i_j


            Diversities[i] =  np.mean(diversity)

        top_count = int(self.top_x * performances.shape[1])

        fitness = np.array([arr[-top_count:] for arr in np.sort(performances, axis=1)])
        
        fitness = np.mean(fitness, axis=1)

        return (fitness, Diversities)
    
    
    def evolve(self):
        
        #1 - elites -> Retain the top agents on a mixture of top scores and most diverse

        # fitness = self.balance_ratio * self.scores + (1 - self.balance_ratio) * self.Entropies
        # index_elites = np.argsort(fitness)[-self.elite_count:]
        
        # performance = np.array(self.scores + self.balance_ratio * self.Entropies)
        # fitness = np.argsort(performance)[-(top_x ):]

        fitness, Diversity = self.calculate_fitness()

        index_elites = np.argsort(fitness)[-self.elite_count:]

        for i in index_elites:
            self.next_population.append(self.current_population[i])
        
        #2 - crossover_selection
        crossover_list = self.crossover_selection()
        
        #3 - crossover
        self.crossover(crossover_list, self.next_population)
        
        #4 - mutation
        self.mutate()
        
        #print("Next generation: " + str(self.next_population))
        return (self.next_population, fitness, Diversity)

if __name__ == "__main__":

    test_pop = []
    scores = []
    for i in range(20):
        random_agent = [random.randint(0,9),random.randint(10,19),random.randint(20,30), 250]
        test_pop.append(random_agent)
        scores.append(i)
    print("original: " + str(test_pop))
    print("scores:" + str(scores))
    test_evo = Evolution(test_pop, scores, 1)
    test_evo.evolve()
        


