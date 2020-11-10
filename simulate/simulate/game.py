import random
import sys
import time

import pygame
from pygame.locals import *

from .colors import *


class Game:
    def __init__(self):
        # Initialize some variables for a new game
        self.pattern = []  # stores the pattern of colors
        self.current_step = 0  # the color the player must push next
        self.last_click_time = 0  # timestamp of the player's last button push
        self.score = 0
        # when False, the pattern is playing. when True, waiting for the player to click a colored button:
        self.waiting_for_input = False

        self.background_color = BLACK

        self.fps = 30
        self.window_width = 640
        self.window_height = 480
        self.flash_speed = 500  # in milliseconds
        self.flash_delay = 200  # in milliseconds
        self.button_size = 200
        self.button_gap_size = 20
        self.timeout = 4  # seconds before game over if no button is pushed.

        self.x_margin = int((self.window_width - (2 * self.button_size) - self.button_gap_size) / 2)
        self.y_margin = int((self.window_height - (2 * self.button_size) - self.button_gap_size) / 2)

        # Rect objects for each of the four buttons
        self.yellow_rect = pygame.Rect(self.x_margin, self.y_margin, self.button_size, self.button_size)
        self.blue_rect = pygame.Rect(self.x_margin + self.button_size + self.button_gap_size, self.y_margin, self.button_size, self.button_size)
        self.red_rect = pygame.Rect(self.x_margin, self.y_margin + self.button_size + self.button_gap_size, self.button_size, self.button_size)
        self.green_rect = pygame.Rect(self.x_margin + self.button_size + self.button_gap_size, self.y_margin + self.button_size + self.button_gap_size, self.button_size, self.button_size)

        pygame.init()
        self.fps_clock = pygame.time.Clock()
        self.display_surface = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption('Simulate')

        self.basic_font = pygame.font.Font('freesansbold.ttf', 16)
        self.info_surface = self.basic_font.render('Match the pattern by clicking on the button or using the Q, W, A, S keys.', 1, DARKGRAY)
        self.info_rect = self.info_surface.get_rect()
        self.info_rect.topleft = (10, self.window_height - 25)

        # load the sound files
        self.beep1 = pygame.mixer.Sound('beep1.ogg')
        self.beep2 = pygame.mixer.Sound('beep2.ogg')
        self.beep3 = pygame.mixer.Sound('beep3.ogg')
        self.beep4 = pygame.mixer.Sound('beep4.ogg')

    def run(self):
        while True:  # main game loop
            clicked_button = None  # button that was clicked (set to YELLOW, RED, GREEN, or BLUE)
            self.display_surface.fill(self.background_color)
            self.draw_buttons()

            score_surf = self.basic_font.render('Score: ' + str(self.score), True, WHITE)
            score_rect = score_surf.get_rect()
            score_rect.topleft = (self.window_width - 100, 10)
            self.display_surface.blit(score_surf, score_rect)

            self.display_surface.blit(self.info_surface, self.info_rect)

            self.check_for_quit()
            for event in pygame.event.get():  # event handling loop
                if event.type == MOUSEBUTTONUP:
                    mouse_x, mouse_y = event.pos
                    clicked_button = self.get_button_clicked(mouse_x, mouse_y)
                elif event.type == KEYDOWN:
                    if event.key == K_q:
                        clicked_button = YELLOW
                    elif event.key == K_w:
                        clicked_button = BLUE
                    elif event.key == K_a:
                        clicked_button = RED
                    elif event.key == K_s:
                        clicked_button = GREEN

            if not self.waiting_for_input:
                # play the pattern
                pygame.display.update()
                pygame.time.wait(1000)
                self.pattern.append(random.choice((YELLOW, BLUE, RED, GREEN)))
                for button in self.pattern:
                    self.flash_button_animation(button)
                    pygame.time.wait(self.flash_delay)
                self.waiting_for_input = True
            else:
                # wait for the player to enter buttons
                if clicked_button and clicked_button == self.pattern[self.current_step]:
                    # pushed the correct button
                    self.flash_button_animation(clicked_button)
                    self.current_step += 1
                    self.last_click_time = time.time()

                    if self.current_step == len(self.pattern):
                        # pushed the last button in the pattern
                        self.change_background_animation()
                        self.score += 1
                        self.waiting_for_input = False
                        self.current_step = 0  # reset back to first step

                elif (clicked_button and clicked_button != self.pattern[self.current_step]) or (
                        self.current_step != 0 and time.time() - self.timeout > self.last_click_time):
                    # pushed the incorrect button, or has timed out
                    self.game_over_animation()
                    # reset the variables for a new game:
                    self.pattern = []
                    self.current_step = 0
                    self.waiting_for_input = False
                    self.score = 0
                    pygame.time.wait(1000)
                    self.change_background_animation()

            pygame.display.update()
            self.fps_clock.tick(self.fps)

    def terminate(self):
        pygame.quit()
        sys.exit()

    def check_for_quit(self):
        for event in pygame.event.get(QUIT):  # get all the QUIT events
            self.terminate()  # terminate if any QUIT events are present
        for event in pygame.event.get(KEYUP):  # get all the KEYUP events
            if event.key == K_ESCAPE:
                self.terminate()  # terminate if the KEYUP event was for the Esc key
            pygame.event.post(event)  # put the other KEYUP event objects back

    def flash_button_animation(self, color, animation_speed=50):
        if color == YELLOW:
            sound = self.beep1
            flash_color = BRIGHTYELLOW
            rectangle = self.yellow_rect
        elif color == BLUE:
            sound = self.beep2
            flash_color = BRIGHTBLUE
            rectangle = self.blue_rect
        elif color == RED:
            sound = self.beep3
            flash_color = BRIGHTRED
            rectangle = self.red_rect
        elif color == GREEN:
            sound = self.beep4
            flash_color = BRIGHTGREEN
            rectangle = self.green_rect

        orig_surf = self.display_surface.copy()
        flash_surf = pygame.Surface((self.button_size, self.button_size))
        flash_surf = flash_surf.convert_alpha()
        r, g, b = flash_color
        sound.play()
        for start, end, step in ((0, 255, 1), (255, 0, -1)):  # animation loop
            for alpha in range(start, end, animation_speed * step):
                self.check_for_quit()
                self.display_surface.blit(orig_surf, (0, 0))
                flash_surf.fill((r, g, b, alpha))
                self.display_surface.blit(flash_surf, rectangle.topleft)
                pygame.display.update()
                self.fps_clock.tick(self.fps)
        self.display_surface.blit(orig_surf, (0, 0))

    def draw_buttons(self):
        pygame.draw.rect(self.display_surface, YELLOW, self.yellow_rect)
        pygame.draw.rect(self.display_surface, BLUE, self.blue_rect)
        pygame.draw.rect(self.display_surface, RED, self.red_rect)
        pygame.draw.rect(self.display_surface, GREEN, self.green_rect)

    def change_background_animation(self, animation_speed=40):
        new_bg_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        new_bg_surf = pygame.Surface((self.window_width, self.window_height))
        new_bg_surf = new_bg_surf.convert_alpha()
        r, g, b = new_bg_color
        for alpha in range(0, 255, animation_speed):  # animation loop
            self.check_for_quit()
            self.display_surface.fill(self.background_color)

            new_bg_surf.fill((r, g, b, alpha))
            self.display_surface.blit(new_bg_surf, (0, 0))

            self.draw_buttons()  # redraw the buttons on top of the tint

            pygame.display.update()
            self.fps_clock.tick(self.fps)
        self.background_color = new_bg_color

    def game_over_animation(self, color=WHITE, animation_speed=50):
        # play all beeps at once, then flash the background
        orig_surf = self.display_surface.copy()
        flash_surf = pygame.Surface(self.display_surface.get_size())
        flash_surf = flash_surf.convert_alpha()
        self.beep1.play()  # play all four beeps at the same time, roughly.
        self.beep2.play()
        self.beep3.play()
        self.beep4.play()
        r, g, b = color
        for i in range(3):  # do the flash 3 times
            for start, end, step in ((0, 255, 1), (255, 0, -1)):
                # The first iteration in this loop sets the following for loop
                # to go from 0 to 255, the second from 255 to 0.
                for alpha in range(start, end, animation_speed * step):  # animation loop
                    # alpha means transparency. 255 is opaque, 0 is invisible
                    self.check_for_quit()
                    flash_surf.fill((r, g, b, alpha))
                    self.display_surface.blit(orig_surf, (0, 0))
                    self.display_surface.blit(flash_surf, (0, 0))
                    self.draw_buttons()
                    pygame.display.update()
                    self.fps_clock.tick(self.fps)

    def get_button_clicked(self, x, y):
        if self.yellow_rect.collidepoint((x, y)):
            return YELLOW
        elif self.blue_rect.collidepoint((x, y)):
            return BLUE
        elif self.red_rect.collidepoint((x, y)):
            return RED
        elif self.green_rect.collidepoint((x, y)):
            return GREEN
        return None
