
class WindowInformationPacket:
    def __init__(self, screen_width, screen_height, generation=0, game_fps=0, game_time="Unknown", high_score=0):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.generation = generation
        self.game_fps = game_fps
        self.game_time = game_time
        self.high_score = high_score

    def get_information(self):
        return {
            'SCREEN_WIDTH': self.screen_width,
            'SCREEN_HEIGHT': self.screen_height,
            'GENERATION' : self.generation,
            'FPS': self.game_fps,
            'GAME_TIME': self.game_time,
            'HIGH_SCORE': self.high_score
        }