# TODO: Create a new object called WinTicket that stores information about the player that has won the neat-ai training


class WinTicket():
    # This class is used to store information surrounding the Player that has won the game.
    def __init__(self, player, generation, species, generation_time):
        self.player = player
        self.generation = generation
        self.species = species
        self.generation_time = generation_time

    def __str__(self):
        return f"Winner: {self.player.name}, Generation: {self.generation}, Species: {self.species}, Generation Time: {self.generation_time}"
