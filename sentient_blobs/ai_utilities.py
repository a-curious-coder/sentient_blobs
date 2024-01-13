import random

import numpy as np
import pygame


# Adjust network output with random noise
def adjust_output_with_noise(network_output, noise_level=0.03):
    """ Adjust the network output with random noise. 
    This encourages the network to explore more of the action space and not get stuck in a local minima.
    Args:
        network_output (np.array): The network's output
        noise_level (float): The amount of noise to add to the network's output
    Returns:
        np.array: The network's output with random noise added
    """
    # Add random noise to the network's output
    noisy_output = network_output + np.random.normal(0, noise_level, size=network_output.shape)
    # Ensure the probabilities sum to 1
    noisy_output = np.clip(noisy_output, 0, 1) / np.sum(noisy_output)
    return noisy_output

def get_random_colour():
    """ Generate a random colour.
    Returns:
        tuple: A tuple containing the RGB values of the colour
    """
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def conflicting_moves(keys) -> bool:
    return (keys[pygame.K_LEFT] and keys[pygame.K_RIGHT]) or \
        (keys[pygame.K_DOWN] and keys[pygame.K_UP])
