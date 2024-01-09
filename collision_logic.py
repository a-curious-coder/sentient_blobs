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
    threshold = obj1.radius + (obj1.radius * 0.1) + obj2.radius
    return distance <= threshold


def player_eaten_player(player: Player, colliding_player: Player) -> None:
    """ Player eats another player
    Handles the delegation of points and the assignment of failure for the eaten player
    Arguments:
        player {Player} -- Player that ate
        colliding_player {Player} -- Player that was eaten
    """
    if math.floor(player.radius) > math.floor(colliding_player.radius * 1.1):
        if player.score != 0:
            player.score += colliding_player.radius
        else:
            player.base_radius += colliding_player.base_radius
            if player.base_radius > 10:
                player.score = player.base_radius - 10
                player.base_radius = 10
        player.peak_score = max(player.score, player.peak_score)
        player.players_eaten += 1
        player.last_eaten_time = time.time()
        colliding_player.failed = True
        colliding_player.fail_reason += f"eaten by {player.name} at {player.score}"
