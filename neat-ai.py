import neat
from main import evaluate_genomes as main

max_gen = 50 #The maximum number of generation to run


# Define a function to run NEAT algorithm to play flappy bird
def run_NEAT(config_file):
    
    # The template for the configuration file can be found here:
    #https://github.com/CodeReclaimers/neat-python/blob/master/examples/xor/config-feedforward
    # The description of the options in the configuration file can be found here:
    #https://neat-python.readthedocs.io/en/latest/config_file.html#defaultgenome-section
    
    # Use NEAT algorithm to build a neural network based on the pre-set configurtion
    # Create a neat.config.Config object from the configuration file
    config = neat.config.Config(neat.DefaultGenome, 
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, 
                                neat.DefaultStagnation,
                                config_file)
    
    config.genome_config.initial_connection = "full_nodirect"

    # Create a neat.population.Population object using the Config object created above
    neat_pop = neat.population.Population(config)
    
    # Show the summary statistics of the learning progress
    neat_pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    neat_pop.add_reporter(stats)
    
    # Call the run method on the Population object, giving it your fitness function and (optionally) the maximum number of generations you want NEAT to run
    neat_pop.run(main, max_gen)
    
    # Get the most fit genome genome as our winner with the statistics.best_genome() function
    winner = stats.best_genome()
    
    # Visualize the results
    # node_names = {-1:'delta_x', -2: 'delta_y_top', -3:'delta_y_bottom', 0:'Jump or Not'}
    # draw_net(config, winner, True, node_names = node_names)
    # plot_stats(stats, ylog = False, view = True)
    # plot_species(stats, view = True)
    
    # Show the final statistics
    print(f'\nBest genome:\n{winner}')

#run the game!
config_file = 'config-feedforward.txt'

if __name__ == '__main__':
    try:
        # Clear console
        print('\033c')
        run_NEAT(config_file)
    except KeyboardInterrupt:
        print('\nUser quit the game!')
        quit()