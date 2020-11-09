# Tetromino (a Tetris clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random
import pygame

from tetromino import Game


def main():
    game = Game(
        window_width=640,
        window_height=480,
        board_width=10,
        board_height=20,
        box_size=20,
    )

    game.show_text_screen('Tetromino')
    while True:  # game loop
        if random.randint(0, 1) == 0:
            pygame.mixer.music.load('tetrisb.mid')
        else:
            pygame.mixer.music.load('tetrisc.mid')
        pygame.mixer.music.play(-1, 0.0)
        game.run()
        pygame.mixer.music.stop()
        game.show_text_screen('Game Over')
        game.reset()


if __name__ == '__main__':
    main()
