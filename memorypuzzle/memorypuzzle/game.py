import random
import sys

import pygame
from pygame.locals import *

from .colors import *
from .shapes import *


class Game:
    def __init__(self):
        self.fps = 30  # frames per second, the general speed of the program
        self.window_width = 640  # size of window's width in pixels
        self.window_height = 480  # size of windows' height in pixels
        self.reveal_speed = 8  # speed boxes' sliding reveals and covers
        self.box_size = 40  # size of box height & width in pixels
        self.gap_size = 10  # size of gap between boxes in pixels
        self.board_width = 10  # number of columns of icons
        self.board_height = 7  # number of rows of icons
        assert (self.board_width * self.board_height) % 2 == 0, 'Board needs to have an even number of boxes for pairs of matches.'
        assert len(ALLCOLORS) * len(ALLSHAPES) * 2 >= self.board_width * self.board_height, "Board is too big for the number of shapes/colors defined."
        self.x_margin = int((self.window_width - (self.board_width * (self.box_size + self.gap_size))) / 2)
        self.y_margin = int((self.window_height - (self.board_height * (self.box_size + self.gap_size))) / 2)

        self.background_color = NAVYBLUE
        self.light_background_color = GRAY
        self.box_color = WHITE
        self.highlight_color = BLUE

        pygame.init()
        self.fps_clock = pygame.time.Clock()
        self.display_surface = pygame.display.set_mode((self.window_width, self.window_height))

        self.mousex = 0  # used to store x coordinate of mouse event
        self.mousey = 0  # used to store y coordinate of mouse event
        pygame.display.set_caption('Memory Game')

        self.main_board = self.get_randomized_board()
        self.revealed_boxes = self.generate_revealed_boxes_data(False)

        self.first_selection = None  # stores the (x, y) of the first box clicked.

    def run(self):
        self.display_surface.fill(self.background_color)
        self.start_game_animation(self.main_board)

        while True:  # main game loop
            mouse_clicked = False

            self.display_surface.fill(self.background_color)  # drawing the window
            self.draw_board(self.main_board, self.revealed_boxes)

            for event in pygame.event.get():  # event handling loop
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEMOTION:
                    mouse_x, mouse_y = event.pos
                elif event.type == MOUSEBUTTONUP:
                    mouse_x, mouse_y = event.pos
                    mouse_clicked = True

            boxx, boxy = self.get_box_at_pixel(mouse_x, mouse_y)
            if boxx is not None and boxy is not None:
                # The mouse is currently over a box.
                if not self.revealed_boxes[boxx][boxy]:
                    self.draw_highlight_box(boxx, boxy)
                if not self.revealed_boxes[boxx][boxy] and mouse_clicked:
                    self.reveal_boxes_animation(self.main_board, [(boxx, boxy)])
                    self.revealed_boxes[boxx][boxy] = True  # set the box as "revealed"
                    if self.first_selection is None:  # the current box was the first box clicked
                        self.first_selection = (boxx, boxy)
                    else:  # the current box was the second box clicked
                        # Check if there is a match between the two icons.
                        icon1shape, icon1color = self.get_shape_and_color(self.main_board, self.first_selection[0], self.first_selection[1])
                        icon2shape, icon2color = self.get_shape_and_color(self.main_board, boxx, boxy)

                        if icon1shape != icon2shape or icon1color != icon2color:
                            # Icons don't match. Re-cover up both selections.
                            pygame.time.wait(1000)  # 1000 milliseconds = 1 sec
                            self.cover_boxes_animation(self.main_board, [(self.first_selection[0], self.first_selection[1]), (boxx, boxy)])
                            self.revealed_boxes[self.first_selection[0]][self.first_selection[1]] = False
                            self.revealed_boxes[boxx][boxy] = False
                        elif self.has_won(self.revealed_boxes):  # check if all pairs found
                            self.game_won_animation(self.main_board)
                            pygame.time.wait(2000)

                            # Reset the board
                            self.main_board = self.get_randomized_board()
                            self.revealed_boxes = self.generate_revealed_boxes_data(False)

                            # Show the fully unrevealed board for a second.
                            self.draw_board(self.main_board, self.revealed_boxes)
                            pygame.display.update()
                            pygame.time.wait(1000)

                            # Replay the start game animation.
                            self.start_game_animation(self.main_board)
                        self.first_selection = None  # reset firstSelection variable

            # Redraw the screen and wait a clock tick.
            pygame.display.update()
            self.fps_clock.tick(self.fps)

    def generate_revealed_boxes_data(self, val):
        revealed_boxes = []
        for i in range(self.board_width):
            revealed_boxes.append([val] * self.board_height)
        return revealed_boxes

    def get_randomized_board(self):
        # Get a list of every possible shape in every possible color.
        icons = []
        for color in ALLCOLORS:
            for shape in ALLSHAPES:
                icons.append((shape, color))

        random.shuffle(icons)  # randomize the order of the icons list
        num_icons_used = int(self.board_width * self.board_height / 2)  # calculate how many icons are needed
        icons = icons[:num_icons_used] * 2  # make two of each
        random.shuffle(icons)

        # Create the board data structure, with randomly placed icons.
        board = []
        for x in range(self.board_width):
            column = []
            for y in range(self.board_height):
                column.append(icons[0])
                del icons[0]  # remove the icons as we assign them
            board.append(column)
        return board

    @staticmethod
    def split_into_groups_of(group_size, the_list):
        # splits a list into a list of lists, where the inner lists have at
        # most groupSize number of items.
        result = []
        for i in range(0, len(the_list), group_size):
            result.append(the_list[i:i + group_size])
        return result

    def left_top_coords_of_box(self, boxx, boxy):
        # Convert board coordinates to pixel coordinates
        left = boxx * (self.box_size + self.gap_size) + self.x_margin
        top = boxy * (self.box_size + self.gap_size) + self.y_margin
        return left, top

    def get_box_at_pixel(self, x, y):
        for boxx in range(self.board_width):
            for boxy in range(self.board_height):
                left, top = self.left_top_coords_of_box(boxx, boxy)
                box_rect = pygame.Rect(left, top, self.box_size, self.box_size)
                if box_rect.collidepoint(x, y):
                    return boxx, boxy
        return None, None

    def draw_icon(self, shape, color, boxx, boxy):
        quarter = int(self.box_size * 0.25)  # syntactic sugar
        half = int(self.box_size * 0.5)  # syntactic sugar

        left, top = self.left_top_coords_of_box(boxx, boxy)  # get pixel coords from board coords
        # Draw the shapes
        if shape == DONUT:
            pygame.draw.circle(self.display_surface, color, (left + half, top + half), half - 5)
            pygame.draw.circle(self.display_surface, self.background_color, (left + half, top + half), quarter - 5)
        elif shape == SQUARE:
            pygame.draw.rect(self.display_surface, color, (left + quarter, top + quarter, self.box_size - half, self.box_size - half))
        elif shape == DIAMOND:
            pygame.draw.polygon(self.display_surface, color, (
                (left + half, top), (left + self.box_size - 1, top + half), (left + half, top + self.box_size - 1), (left, top + half)))
        elif shape == LINES:
            for i in range(0, self.box_size, 4):
                pygame.draw.line(self.display_surface, color, (left, top + i), (left + i, top))
                pygame.draw.line(self.display_surface, color, (left + i, top + self.box_size - 1), (left + self.box_size - 1, top + i))
        elif shape == OVAL:
            pygame.draw.ellipse(self.display_surface, color, (left, top + quarter, self.box_size, half))

    @staticmethod
    def get_shape_and_color(board, boxx, boxy):
        # shape value for x, y spot is stored in board[x][y][0]
        # color value for x, y spot is stored in board[x][y][1]
        return board[boxx][boxy][0], board[boxx][boxy][1]

    def draw_box_covers(self, board, boxes, coverage):
        # Draws boxes being covered/revealed. "boxes" is a list
        # of two-item lists, which have the x & y spot of the box.
        for box in boxes:
            left, top = self.left_top_coords_of_box(box[0], box[1])
            pygame.draw.rect(self.display_surface, self.background_color, (left, top, self.box_size, self.box_size))
            shape, color = self.get_shape_and_color(board, box[0], box[1])
            self.draw_icon(shape, color, box[0], box[1])
            if coverage > 0:  # only draw the cover if there is an coverage
                pygame.draw.rect(self.display_surface, self.box_color, (left, top, coverage, self.box_size))
        pygame.display.update()
        self.fps_clock.tick(self.fps)

    def reveal_boxes_animation(self, board, boxes_to_reveal):
        # Do the "box reveal" animation.
        for coverage in range(self.box_size, (-self.reveal_speed) - 1, -self.reveal_speed):
            self.draw_box_covers(board, boxes_to_reveal, coverage)

    def cover_boxes_animation(self, board, boxes_to_cover):
        # Do the "box cover" animation.
        for coverage in range(0, self.box_size + self.reveal_speed, self.reveal_speed):
            self.draw_box_covers(board, boxes_to_cover, coverage)

    def draw_board(self, board, revealed):
        # Draws all of the boxes in their covered or revealed state.
        for boxx in range(self.board_width):
            for boxy in range(self.board_height):
                left, top = self.left_top_coords_of_box(boxx, boxy)
                if not revealed[boxx][boxy]:
                    # Draw a covered box.
                    pygame.draw.rect(self.display_surface, self.box_color, (left, top, self.box_size, self.box_size))
                else:
                    # Draw the (revealed) icon.
                    shape, color = self.get_shape_and_color(board, boxx, boxy)
                    self.draw_icon(shape, color, boxx, boxy)

    def draw_highlight_box(self, boxx, boxy):
        left, top = self.left_top_coords_of_box(boxx, boxy)
        pygame.draw.rect(self.display_surface, self.highlight_color, (left - 5, top - 5, self.box_size + 10, self.box_size + 10), 4)

    def start_game_animation(self, board):
        # Randomly reveal the boxes 8 at a time.
        covered_boxes = self.generate_revealed_boxes_data(False)
        boxes = []
        for x in range(self.board_width):
            for y in range(self.board_height):
                boxes.append((x, y))
        random.shuffle(boxes)
        box_groups = self.split_into_groups_of(8, boxes)

        self.draw_board(board, covered_boxes)
        for boxGroup in box_groups:
            self.reveal_boxes_animation(board, boxGroup)
            self.cover_boxes_animation(board, boxGroup)

    def game_won_animation(self, board):
        # flash the background color when the player has won
        covered_boxes = self.generate_revealed_boxes_data(True)
        color1 = self.light_background_color
        color2 = self.background_color

        for i in range(13):
            color1, color2 = color2, color1  # swap colors
            self.display_surface.fill(color1)
            self.draw_board(board, covered_boxes)
            pygame.display.update()
            pygame.time.wait(300)

    @staticmethod
    def has_won(revealed_boxes):
        # Returns True if all the boxes have been revealed, otherwise False
        for i in revealed_boxes:
            if False in i:
                return False  # return False if any boxes are covered.
        return True
