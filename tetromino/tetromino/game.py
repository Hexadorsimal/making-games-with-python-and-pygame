import sys
import time
import pygame
from pygame.locals import *

from .board import Board
from .piece import Piece
from .piece_templates import piece_templates
from .colors import colors, light_colors, blue, black, white, gray


class Game:
    border_color = blue
    background_color = black
    text_color = white
    text_shadow_color = gray
    fps = 25
    move_sideways_freq = 0.15
    move_down_freq = 0.1

    def __init__(self, window_width, window_height, board_width, board_height, box_size):
        self.window_width = window_width
        self.window_height = window_height
        self.box_size = box_size
        self.x_margin = int((window_width - board_width * box_size) / 2)
        self.top_margin = window_height - (board_height * box_size) - 5

        pygame.init()
        self.fps_clock = pygame.time.Clock()
        self.display_surface = pygame.display.set_mode((window_width, window_height))
        self.basic_font = pygame.font.Font('freesansbold.ttf', 18)
        self.big_font = pygame.font.Font('freesansbold.ttf', 100)
        pygame.display.set_caption('Tetromino')

        self.board = Board(board_width, board_height)
        self.last_move_down_time = time.time()
        self.last_move_sideways_time = time.time()
        self.last_fall_time = time.time()
        self.moving_down = False  # note: there is no movingUp variable
        self.moving_left = False
        self.moving_right = False
        self.score = 0

    def reset(self):
        self.board = Board(self.board.width, self.board.height)
        self.last_move_down_time = time.time()
        self.last_move_sideways_time = time.time()
        self.last_fall_time = time.time()
        self.moving_down = False  # note: there is no movingUp variable
        self.moving_left = False
        self.moving_right = False
        self.score = 0

    @property
    def blank(self):
        return self.board.blank

    def run(self):
        # setup variables for the start of the game
        level, fall_freq = self.calculate_level_and_fall_frequency()

        falling_piece = Piece.create_random(self.board.width)
        next_piece = Piece.create_random(self.board.width)

        while True:  # game loop
            if falling_piece is None:
                # No falling piece in play, so start a new piece at the top
                falling_piece = next_piece
                next_piece = Piece.create_random(self.board.width)
                self.last_fall_time = time.time()  # reset lastFallTime

                if not self.board.is_valid_position(falling_piece):
                    return  # can't fit a new piece on the board, so game over

            self.check_for_quit()
            for event in pygame.event.get():  # event handling loop
                if event.type == KEYUP:
                    if event.key == K_p:
                        # Pausing the game
                        self.display_surface.fill(self.background_color)
                        pygame.mixer.music.stop()
                        self.show_text_screen('Paused')  # pause until a key press
                        pygame.mixer.music.play(-1, 0.0)
                        self.last_fall_time = time.time()
                        self.last_move_down_time = time.time()
                        self.last_move_sideways_time = time.time()
                    elif event.key == K_LEFT or event.key == K_a:
                        self.moving_left = False
                    elif event.key == K_RIGHT or event.key == K_d:
                        self.moving_right = False
                    elif event.key == K_DOWN or event.key == K_s:
                        self.moving_down = False

                elif event.type == KEYDOWN:
                    # moving the piece sideways
                    if (event.key == K_LEFT or event.key == K_a) and self.board.is_valid_position(falling_piece, adjX=-1):
                        falling_piece.x -= 1
                        self.moving_left = True
                        self.moving_right = False
                        self.last_move_sideways_time = time.time()

                    elif (event.key == K_RIGHT or event.key == K_d) and self.board.is_valid_position(falling_piece, adjX=1):
                        falling_piece.x += 1
                        self.moving_right = True
                        self.moving_left = False
                        self.last_move_sideways_time = time.time()

                    # rotating the piece (if there is room to rotate)
                    elif event.key == K_UP or event.key == K_w:
                        falling_piece.rotation = (falling_piece.rotation + 1) % len(piece_templates[falling_piece.shape])
                        if not self.board.is_valid_position(falling_piece):
                            falling_piece.rotation = (falling_piece.rotation - 1) % len(
                                piece_templates[falling_piece.shape])
                    elif event.key == K_q:  # rotate the other direction
                        falling_piece.rotation = (falling_piece.rotation - 1) % len(piece_templates[falling_piece.shape])
                        if not self.board.is_valid_position(falling_piece):
                            falling_piece.rotation = (falling_piece.rotation + 1) % len(
                                piece_templates[falling_piece.shape])

                    # making the piece fall faster with the down key
                    elif event.key == K_DOWN or event.key == K_s:
                        self.moving_down = True
                        if self.board.is_valid_position(falling_piece, adjY=1):
                            falling_piece.y += 1
                        self.last_move_down_time = time.time()

                    # move the current piece all the way down
                    elif event.key == K_SPACE:
                        self.moving_down = False
                        self.moving_left = False
                        self.moving_right = False
                        for i in range(1, self.board.height):
                            if not self.board.is_valid_position(falling_piece, adjY=i):
                                break
                        falling_piece.y += i - 1

            # handle moving the piece because of user input
            if (self.moving_left or self.moving_right) and time.time() - self.last_move_sideways_time > self.move_sideways_freq:
                if self.moving_left and self.board.is_valid_position(falling_piece, adjX=-1):
                    falling_piece.x -= 1
                elif self.moving_right and self.board.is_valid_position(falling_piece, adjX=1):
                    falling_piece.x += 1
                self.last_move_sideways_time = time.time()

            if self.moving_down and time.time() - self.last_move_down_time > self.move_down_freq and self.board.is_valid_position(falling_piece, adjY=1):
                falling_piece.y += 1
                self.last_move_down_time = time.time()

            # let the piece fall if it is time to fall
            if time.time() - self.last_fall_time > fall_freq:
                # see if the piece has landed
                if not self.board.is_valid_position(falling_piece, adjY=1):
                    # falling piece has landed, set it on the board
                    self.board.add_piece(falling_piece)
                    self.score += self.board.remove_complete_lines()
                    level, fall_freq = self.calculate_level_and_fall_frequency()
                    falling_piece = None
                else:
                    # piece did not land, just move the piece down
                    falling_piece.y += 1
                    self.last_fall_time = time.time()

            # drawing everything on the screen
            self.display_surface.fill(self.background_color)
            self.draw_board()
            self.draw_status(self.score, level)
            self.draw_next_piece(next_piece)
            if falling_piece is not None:
                self.draw_piece(falling_piece)

            pygame.display.update()
            self.fps_clock.tick(self.fps)

    def draw_status(self, score, level):
        # draw the score text
        score_surf = self.basic_font.render('Score: %s' % score, True, self.text_color)
        score_rect = score_surf.get_rect()
        score_rect.topleft = (self.window_width - 150, 20)
        self.display_surface.blit(score_surf, score_rect)

        # draw the level text
        level_surf = self.basic_font.render('Level: %s' % level, True, self.text_color)
        level_rect = level_surf.get_rect()
        level_rect.topleft = (self.window_width - 150, 50)
        self.display_surface.blit(level_surf, level_rect)

    def draw_piece(self, piece, pixelx=None, pixely=None):
        shapeToDraw = piece_templates[piece.shape][piece.rotation]
        if pixelx is None and pixely is None:
            # if pixelx & pixely hasn't been specified, use the location stored in the piece data structure
            pixelx, pixely = self.convert_to_pixel_coords(piece.x, piece.y)

        # draw each of the boxes that make up the piece
        for x in range(Piece.template_width):
            for y in range(Piece.template_height):
                if shapeToDraw[y][x] != self.board.blank:
                    self.draw_box(None, None, piece.color, pixelx + (x * self.box_size), pixely + (y * self.box_size))

    def draw_next_piece(self, piece):
        # draw the "next" text
        next_surf = self.basic_font.render('Next:', True, self.text_color)
        next_rect = next_surf.get_rect()
        next_rect.topleft = (self.window_width - 120, 80)
        self.display_surface.blit(next_surf, next_rect)
        # draw the "next" piece
        self.draw_piece(piece, pixelx=self.window_width - 120, pixely=100)

    def show_text_screen(self, text):
        # This function displays large text in the
        # center of the screen until a key is pressed.
        # Draw the text drop shadow
        title_surf, title_rect = self.make_text_objs(text, self.big_font, self.text_shadow_color)
        title_rect.center = (int(self.window_width / 2), int(self.window_height / 2))
        self.display_surface.blit(title_surf, title_rect)

        # Draw the text
        title_surf, title_rect = self.make_text_objs(text, self.big_font, self.text_color)
        title_rect.center = (int(self.window_width / 2) - 3, int(self.window_height / 2) - 3)
        self.display_surface.blit(title_surf, title_rect)

        # Draw the additional "Press a key to play." text.
        press_key_surf, press_key_rect = self.make_text_objs('Press a key to play.', self.basic_font, self.text_color)
        press_key_rect.center = (int(self.window_width / 2), int(self.window_height / 2) + 100)
        self.display_surface.blit(press_key_surf, press_key_rect)

        while self.check_for_key_press() is None:
            pygame.display.update()
            self.fps_clock.tick()

    def check_for_quit(self):
        for event in pygame.event.get(QUIT):  # get all the QUIT events
            self.terminate()  # terminate if any QUIT events are present
        for event in pygame.event.get(KEYUP):  # get all the KEYUP events
            if event.key == K_ESCAPE:
                self.terminate()  # terminate if the KEYUP event was for the Esc key
            pygame.event.post(event)  # put the other KEYUP event objects back

    def calculate_level_and_fall_frequency(self):
        # Based on the score, return the level the player is on and
        # how many seconds pass until a falling piece falls one space.
        level = int(self.score / 10) + 1
        fall_freq = 0.27 - (level * 0.02)
        return level, fall_freq

    @staticmethod
    def terminate():
        pygame.quit()
        sys.exit()

    def check_for_key_press(self):
        # Go through event queue looking for a KEYUP event.
        # Grab KEYDOWN events to remove them from the event queue.
        self.check_for_quit()

        for event in pygame.event.get([KEYDOWN, KEYUP]):
            if event.type == KEYDOWN:
                continue
            return event.key
        return None

    @staticmethod
    def make_text_objs(text, font, color):
        surf = font.render(text, True, color)
        return surf, surf.get_rect()

    def convert_to_pixel_coords(self, boxx, boxy):
        # Convert the given xy coordinates of the board to xy
        # coordinates of the location on the screen.
        return (self.x_margin + (boxx * self.box_size)), (self.top_margin + (boxy * self.box_size))

    def draw_box(self, boxx, boxy, color, pixelx=None, pixely=None):
        # draw a single box (each tetromino piece has four boxes)
        # at xy coordinates on the board. Or, if pixelx & pixely
        # are specified, draw to the pixel coordinates stored in
        # pixelx & pixely (this is used for the "Next" piece).
        if color == self.blank:
            return
        if pixelx is None and pixely is None:
            pixelx, pixely = self.convert_to_pixel_coords(boxx, boxy)

        pygame.draw.rect(self.display_surface, colors[color], (pixelx + 1, pixely + 1, self.box_size - 1, self.box_size - 1))
        pygame.draw.rect(self.display_surface, light_colors[color], (pixelx + 1, pixely + 1, self.box_size - 4, self.box_size - 4))

    def draw_board(self):
        # draw the border around the board
        pygame.draw.rect(
            self.display_surface,
            self.border_color,
            (
                self.x_margin - 3,
                self.top_margin - 7,
                (self.board.width * self.box_size) + 8,
                (self.board.height * self.box_size) + 8
            ),
            5
        )

        # fill the background of the board
        pygame.draw.rect(
            self.display_surface,
            self.background_color,
            (
                self.x_margin,
                self.top_margin,
                self.box_size * self.board.width,
                self.box_size * self.board.height
            )
        )

        # draw the individual boxes on the board
        for x in range(self.board.width):
            for y in range(self.board.height):
                self.draw_box(x, y, self.board.board[x][y])
