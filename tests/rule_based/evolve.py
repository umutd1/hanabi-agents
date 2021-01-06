import numpy as np
import random

#Class for evolving

class Evolution:


    def __init__(self, current_population, scores, rule_size = 10, elite_count = 10,
                    mutation_rate = 0.1, tournament_size = 1):
        
        self.current_population = current_population
        self.scores = np.array(scores)
        self.population_size = len(current_population)
        self.rule_size = rule_size
        self.mutation_rate = mutation_rate
        self.tournament_size = tournament_size
        self.crossover_count = len(current_population) - elite_count
        self.elite_count = elite_count
        self.next_generation = []
    #Evolution steps:
    #1 - Taking elites directly to next generation
    #2 - Tournament selection + crossover
    #3 - Crossover including tournament winnders and elites
    #4 - Mutation

    
    #currently random selection
    def crossover_selection(self):
        population_random = self.current_population.copy()
        random.shuffle(population_random)
        return population_random[:self.crossover_count]

    def crossover(self,crossover_list ,agent_list = []):
        for i in range(len(crossover_list)):
            new_agent = []
            random_index = random.randrange(0, len(crossover_list))
            while random_index == i:
                random_index = random.randrange(0, len(crossover_list))
            for k in range(self.rule_size):
                roll = random.randint(0,1)
                if roll == 0:
                    new_agent.append(crossover_list[i][k])
                else:
                    new_agent.append(crossover_list[random_index][k])
            agent_list.append(new_agent)
            

    def evolve(self):
        #1
        index_elites = (-self.scores).argsort()[:self.elite_count]
        #print(index_elites)
        for i in index_elites:
            self.next_generation.append(self.current_population[i])
        #print(self.next_generation)
        
        #2
        crossover_list = self.crossover_selection()
        #print(crossover_list)

        #3
        self.crossover(crossover_list, self.next_generation)
        print("Next generation: " + str(self.next_generation))

test_pop = []
scores = []
for i in range(20):
    random_agent = [random.randint(0,9),random.randint(10,19),random.randint(20,30)]
    test_pop.append(random_agent)
    scores.append(i)
print("original: " + str(test_pop))
print("scores:" + str(scores))
test_evo = Evolution(test_pop, scores, 1)
test_evo.evolve()
        


