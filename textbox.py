import pygame
import animatedsprite
import helpers

UPPER_CASE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
LOWER_CASE = 'abcdefghijklmnopqrstuvwxyz'


class Textbox:
    def __init__(self, string, x=0.5*helpers.SCREEN_WIDTH, y=0.5*helpers.SCREEN_HEIGHT):
        self.x = x
        self.y = y
        self.chars = pygame.sprite.Group()
        self.time = -1
        self.string = string
        self.set_string(string)

    def set_string(self, string):
        self.string = string
        strings = string.split('\\')
        self.chars = pygame.sprite.Group()

        for j, string in enumerate(strings):
            string = string.upper()
            x = self.x - (0.5 * len(string) * 4) * helpers.SCALE
            y = self.y + 0.5 * 4 * helpers.SCALE

            for i, char in enumerate(list(string)):
                sprite = animatedsprite.AnimatedSprite('chars')
                try:
                    index = int(char)
                    sprite.show_frame('numbers', index)
                except ValueError:
                    if char.isupper():
                        index = UPPER_CASE.find(char)
                        sprite.show_frame('upper_case', index)
                    else:
                        index = LOWER_CASE.find(char)
                        sprite.show_frame('lower_case', index)

                    if index == -1:
                        continue

                sprite.set_position(x + i * 4 * helpers.SCALE, y + j * 5 * helpers.SCALE)
                self.chars.add(sprite)

    def update(self):
        if self.time == -1:
            return

        if self.time > 0:
            self.time -= 1
        else:
            self.set_string('')

    def draw(self, screen, img_hand):
        for char in self.chars:
            char.draw(screen, img_hand)