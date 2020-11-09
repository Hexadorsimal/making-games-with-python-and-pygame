# Tetromino (a Tetris clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

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
        game.start_game()
        game.run()
        game.end_game()
        game.reset()


if __name__ == '__main__':
    main()
