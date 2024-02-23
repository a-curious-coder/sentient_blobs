"""A NEAT (NeuroEvolution of Augmenting Topologies) implementation"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src/modules/neat')))

import neat.ctrnn as ctrnn
import neat.distributed as distributed
import neat.iznn as iznn
import neat.nn as nn
from neat.checkpoint import Checkpointer
from neat.config import Config
from neat.distributed import DistributedEvaluator, host_is_local
from neat.genome import DefaultGenome
from neat.parallel import ParallelEvaluator
from neat.population import CompleteExtinctionException, Population
from neat.reporting import StdOutReporter
from neat.reproduction import DefaultReproduction
from neat.species import DefaultSpeciesSet
from neat.stagnation import DefaultStagnation
from neat.statistics import StatisticsReporter
from neat.threaded import ThreadedEvaluator
