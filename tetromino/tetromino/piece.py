import random
from .piece_templates import piece_templates
from .colors import colors


class Piece:
    template_width = 5
    template_height = 5

    def __init__(self, shape, rotation, x, y, color):
        self.shape = shape
        self.rotation = rotation
        self.x = x
        self.y = y
        self.color = color

    @classmethod
    def create_random(cls, board_width):
        # return a random new piece in a random rotation and color
        shape = random.choice(list(piece_templates.keys()))
        return Piece(
            shape=shape,
            rotation=random.randint(0, len(piece_templates[shape]) - 1),
            x=int(board_width / 2) - int(cls.template_width / 2),
            y=-2,  # start it above the board (i.e. less than 0)
            color=random.randint(0, len(colors) - 1)
        )
