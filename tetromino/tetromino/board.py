from .piece import Piece
from .piece_templates import piece_templates


class Board:
    blank = '.'

    def __init__(self, width, height):
        # create and return a new blank board data structure
        self.width = width
        self.height = height

        self.board = []
        for i in range(width):
            self.board.append([self.blank] * height)

    def add_piece(self, piece):
        # fill in the board based on piece's location, shape, and rotation
        for x in range(Piece.template_width):
            for y in range(Piece.template_height):
                if piece_templates[piece.shape][piece.rotation][y][x] != self.blank:
                    self.board[x + piece.x][y + piece.y] = piece.color

    def is_on_board(self, x, y):
        return 0 <= x < self.width and y < self.height

    def is_valid_position(self, piece, adjX=0, adjY=0):
        # Return True if the piece is within the board and not colliding
        for x in range(Piece.template_width):
            for y in range(Piece.template_height):
                is_above_board = y + piece.y + adjY < 0
                if is_above_board or piece_templates[piece.shape][piece.rotation][y][x] == self.blank:
                    continue
                if not self.is_on_board(x + piece.x + adjX, y + piece.y + adjY):
                    return False
                if self.board[x + piece.x + adjX][y + piece.y + adjY] != self.blank:
                    return False
        return True

    def is_complete_line(self, y):
        # Return True if the line filled with boxes with no gaps.
        for x in range(self.width):
            if self.board[x][y] == self.blank:
                return False
        return True

    def remove_complete_lines(self):
        # Remove any completed lines on the board, move everything above them down,
        # and return the number of complete lines.
        num_lines_removed = 0
        y = self.height - 1  # start y at the bottom of the board
        while y >= 0:
            if self.is_complete_line(y):
                # Remove the line and pull boxes down by one line.
                for pullDownY in range(y, 0, -1):
                    for x in range(self.width):
                        self.board[x][pullDownY] = self.board[x][pullDownY - 1]
                # Set very top line to blank.
                for x in range(self.width):
                    self.board[x][0] = self.blank
                num_lines_removed += 1
                # Note on the next iteration of the loop, y is the same.
                # This is so that if the line that was pulled down is also
                # complete, it will be removed.
            else:
                y -= 1  # move on to check next row up
        return num_lines_removed
