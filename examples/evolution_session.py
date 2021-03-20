
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
import dill as pickle
import gin


def session(
    n_players=2,
    population_size=20,
    n_generations=100,
    n_rules=20,
    elite_percentage=0.3,
    n_games_per_pair=10,
    top_x=0.2,
    alpha=0.1, 
    agent = None,
    rulebase=rules.big_ruleset,
    target = None
):

    # n_players = n_players
    # population_size = population_size
    # n_generations = n_generations
    # n_rules = n_rules      # Each agent is a list of these many rules
    
    # We take 20% of the agents with the best score and retain them 
    elite_count = int(elite_percentage * population_size)

    '''
        Total number of games to be played -> Each agent plays 10 games against every other agent
        So, Population * population is one game for each against every other agent and then we multiply 
        it by n_games_per_pair to account for games per agent against every other agent
    '''
    n_parallel = population_size * n_games_per_pair
    top_count = int(top_x * population_size)

    if agent is None: 
        return None
    else:
        my_rules = np.array(agent)

    experiment_data = {
        'n_players': n_players,
        'n_generations': n_generations,
        'n_rules': n_rules,
        'elite_count': elite_count,
        'current_gen': 0,
        'agents': [],
        'best_agent': [],
        'scores': np.zeros(population_size),
        'fitness': np.zeros(population_size),
        'diversity': np.zeros(population_size),
        'eval': 0
    }


    # Initialize the environment
    env_conf = make_hanabi_env_config('Hanabi-Full', n_players)
    env = hmf.HanabiParallelEnvironment(env_conf, n_parallel)

    # For each generation, start the games
    for i in range(n_generations):
        scores = np.zeros((population_size, population_size, n_games_per_pair))

        # individual_scores = []

        # Agent plays against all the other agents n_parallel times / population_size
        # But this happens sequentially -> TODO: Parallelize this loop
        for k in range(population_size):
            # For each agent in the population, create a second agent composed of all other agents
            agents = [ParallelRulebasedAgent(
                [my_rules[k]], n_parallel), ParallelRulebasedAgent(my_rules, n_parallel)]

            # Start a parallel session with these two agents and pass the number of games to be played between
            # them as the environment config
            parallel_session = hmf.HanabiParallelSession(env, agents)

            # Get the result and append the scores
            result = np.array(parallel_session.run_eval(dest=None, print_intermediate=False))
            # print(f"Shape of Result ----> {np.array(result).shape} ")

            result = np.array(result)
            # len(result) = {population_size * n_games } = 200 == 20 * 10

            # split the results into a 2D array of individual scores
            scores[k] = np.array(np.split(result, population_size))

        # Average the scores from the games each agent plays against each other agent
        scores = np.mean(scores, axis = 2)

        avg_scores = np.mean(scores, axis = 1)
        # Print some values for sanity check
        print("Gen:", i+1, "Max:", np.max(avg_scores),
            "Avg:", np.mean(avg_scores), "List:", avg_scores)

        # Pass the current list of agents for the evolution magic and get the new evolved agnets
        evolution_config = Evolution(
            current_population=my_rules,
            scores=scores,
            elite_count=elite_count,
            mutation_rate=0.1,
            tournament_size=1,
            rulebase = rulebase,
            alpha = alpha,
            top_x=top_x
        )
        my_rules, fitness, diversity = evolution_config.evolve()

        # Get the best agent as the index of the first instance of the highest value
        best_agent = my_rules[np.argmax(avg_scores)]

        # Log the metrics and pickle the current data for checkpointing
        experiment_data['current_gen'] = i + 1
        experiment_data['agents'] = my_rules
        experiment_data['best_agent'] = best_agent
        experiment_data['scores'] = np.vstack((experiment_data['scores'], avg_scores))
        experiment_data['fitness'] = np.vstack((experiment_data['fitness'], fitness))
        experiment_data['diversity'] = np.vstack((experiment_data['diversity'], diversity))

        # print(experiment_data['scores'].shape)

        # Pickle the log
        with open(target, 'wb') as handle:
            pickle.dump(experiment_data, handle)

    # Evaluation of the best agent against the piers agent
    agents = [ParallelRulebasedAgent(
        [best_agent]), ParallelRulebasedAgent([rules.piers_rules])]
    env = hmf.HanabiParallelEnvironment(env_conf, 100)

    parallel_session = hmf.HanabiParallelSession(env, agents)
    result = parallel_session.run_eval(dest=None, print_intermediate=False)

    print("Evaluation score:", result.mean())

    experiment_data['eval'] = result.mean()

    with open(target, 'wb') as handle:
        pickle.dump(experiment_data, handle)


def main (args):

    agent = []

    start_time = timeit.default_timer()

    # Load agent from the pickled file
    if args.agent_config_file is not None:
        with open(args.agent_config_file, 'rb') as handle:
            loaded_data = pickle.Unpickler(handle).load()['agents']
            loaded_data = np.array(loaded_data)
            if loaded_data.shape[0] == args.population_size:
                agent = loaded_data
            else:
                for _ in range(args.population_size):
                    x, rulebase = rules.random_rules(args.n_rules)
                    agent.append(np.array(x))

                agent = np.array(agent)

    else:
        for _ in range(args.population_size):
            x, rulebase = rules.random_rules(args.n_rules)
            agent.append(np.array(x))

        agent = np.array(agent)

    session(
        n_players=args.n_players,
        population_size=args.population_size,
        n_generations=args.n_generations,
        n_rules=args.n_rules,
        elite_percentage=args.elite_percentage,
        n_games_per_pair=args.n_games_per_pair,
        top_x=args.top_x,
        alpha=args.alpha ,
        agent=agent,
        rulebase = rulebase,
        target = args.output_file
    )

    stop_time = timeit.default_timer()
    print("Time:", stop_time - start_time)



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train a set of rule-based agents.")

    parser.add_argument(
        "--output_file",
        type = str, 
        default ='Experiments/Div_Add/2_Average_Test_alpha_0.3_top_0.2_0.5.pickle',
        help = 'Path to store the logs of this session in a pickle file'
    )

    parser.add_argument(
        '--agent_config_file', 
        type = str , 
        default = None,  
        help = "Path to an already stored set of rules that can be loaded"
    )

    parser.add_argument(
        '--n_players', 
        type = int , 
        default = 2 , 
        help = "Number of players in the Game"
    )

    parser.add_argument(
        '--population_size', 
        type = int, 
        default = 10, 
        help = 'Size of the population that will play in each generation '
    )

    parser.add_argument(
        '--n_generations', 
        type = int, 
        default = 100, 
        help = "Number of generations for which the agents need to train"
    )

    parser.add_argument(
        '--elite_percentage' ,
        type = float, 
        default = 0.3, 
        help = 'Percentage of agents that need to be considered to retain fit agents '
    )

    parser.add_argument(
        '--n_rules', 
        type = int, 
        default = 20, 
        help = 'Number of rules that each agents needs to sample'
    )

    parser.add_argument(
        '--n_games_per_pair', 
        type = int, 
        default = 10, 
        help = "Number of games that each agent needs to play against each other agent"
    )

    parser.add_argument(
        '--alpha',
        type=float,
        default=0.1,
        help="Importance of Diversity in Performance Calculation"
    )

    parser.add_argument(
        '--top_x',
        type=float,
        default=0.1,
        help="Top Percentage of high performances that we need to average to determine fitness"
    )


    args = parser.parse_args()

    main(args)




    






