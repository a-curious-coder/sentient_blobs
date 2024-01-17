""" Collision logic for the game """
import math
import time

import settings
from components.player import Player


def check_collision(obj1, obj2) -> bool:
    """Check if two objects are colliding
    NOTE: For food and players use only... for now
    Arguments:
        obj1 {object} -- First object
        obj2 {object} -- Second object
    """
    dx = obj1.position.x - obj2.position.x
    dy = obj1.position.y - obj2.position.y
    distance = math.sqrt(dx * dx + dy * dy)
    threshold = obj1.radius + (obj1.radius * 0.1) + obj2.radius
    return distance <= threshold


def player_eaten_player(player: Player, colliding_player: Player) -> bool:
    """ Player eats another player
    Handles the delegation of points and the assignment of failure for the eaten player
    Arguments:
        player {Player} -- Player that ate
        colliding_player {Player} -- Player that was eaten
    """
    # if colliding_player is None:
    #     return False
    # Is player 10% bigger than the colliding player
    if player.radius > colliding_player.radius * (1 + settings.player["eat_player_threshold"]):
        # If the player's score is 0, then check if the player's radius is equal to radius
        player.add_to_score(colliding_player.value * settings.player["score_consumption"])
        player.players_eaten += 1
        player.last_eaten_time = time.time()
        
        # ! Set the colliding player values
        colliding_player.failed = True
        colliding_player.fail_reason += f"eaten by {player.name} at {player.score}"
        return True
    return False