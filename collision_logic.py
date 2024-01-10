""" Collision logic for the game """
import math
import time

from components.player import Player


def check_collision(obj1, obj2) -> bool:
    """Check if two objects are colliding
    NOTE: For food and players use only... for now
    Arguments:
        obj1 {object} -- First object
        obj2 {object} -- Second object
    """
    dx = obj1.x - obj2.x
    dy = obj1.y - obj2.y
    distance = math.sqrt(dx * dx + dy * dy)
    threshold = obj1.value + (obj1.value * 0.1) + obj2.value
    return distance <= threshold


def player_eaten_player(player: Player, colliding_player: Player) -> None:
    """ Player eats another player
    Handles the delegation of points and the assignment of failure for the eaten player
    Arguments:
        player {Player} -- Player that ate
        colliding_player {Player} -- Player that was eaten
    """
    # Is player 10% bigger than the colliding player
    if player.value > colliding_player.value * 1.1:
        # If the player's score is 0, then check if the player's radius is equal to radius
        if player.base_radius == player.value: 
            player.add_to_score(colliding_player.value)
        else:
            # ! To accomodate for a player that's lost some base radius size
            player.base_radius += colliding_player.base_radius
            if player.base_radius > 10:
                player.add_to_score(player.base_radius - 10)
                player.score = player.base_radius - 10
                player.base_radius = 10
        
        player.peak_score = max(player.score, player.peak_score)
        player.players_eaten += 1
        player.last_eaten_time = time.time()
        colliding_player.failed = True
        colliding_player.fail_reason += f"eaten by {player.name} at {player.score}"
