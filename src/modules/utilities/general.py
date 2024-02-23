

def get_random_colour():
    """ Generate a random colour.
    Returns:
        tuple: A tuple containing the RGB values of the colour
    """
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def conflicting_moves(keys) -> bool:
    return (keys[pygame.K_LEFT] and keys[pygame.K_RIGHT]) or \
        (keys[pygame.K_DOWN] and keys[pygame.K_UP])

def get_distance(x1, y1, x2, y2):
    return sqrt( (x2 - x1) * (x2-x1) + (y2 - y1) * (y2 - y1) )
