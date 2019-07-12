import enum
import random
import pygame
import animatedsprite
import gameloop
import helpers
import textbox
import os


class ButtonType(enum.Enum):
    play = 1
    options = 3
    quit = 4
    resume = 5
    menu = 6
    level = 7
    edit = 8
    new = 9
    editor = 10
    create = 11
    save = 12
    test = 13


class SliderType(enum.Enum):
    sound = 1
    music = 2


class Menu:
    def __init__(self, state):
        self.state = state
        self.buttons = []

    def add_button(self, x, y, button_type, text=''):
        self.buttons.append(Button(x, y, button_type, text))

    def draw(self, screen, img_hand):
        for b in self.buttons:
            b.draw(screen, img_hand)

    def input(self, input_hand):
        for b in self.buttons:
            if b.rect.collidepoint(input_hand.mouse_x, input_hand.mouse_y):
                if input_hand.mouse_released[1]:
                    return b.press()

        return self.state


class MainMenu(Menu):
    def __init__(self):
        super().__init__(gameloop.State.menu)
        self.add_button(0, 4, ButtonType.play)
        self.add_button(0, 6, ButtonType.editor)
        self.add_button(0, 8, ButtonType.options)
        self.add_button(0, 10, ButtonType.quit)

        self.bg_sprite = animatedsprite.AnimatedSprite('image')
        self.bg_sprite.play('menu')

    def draw(self, screen, img_hand):
        self.bg_sprite.draw(screen, img_hand)
        super().draw(screen, img_hand)


class PauseMenu(Menu):
    def __init__(self):
        super().__init__(gameloop.State.paused)
        self.add_button(0, 6, ButtonType.resume)
        self.add_button(0, 8, ButtonType.menu)


class LevelSelectMenu(Menu):
    def __init__(self):
        super().__init__(gameloop.State.level_select)

        dy = 4
        for filename in os.listdir('data/lvl'):
            self.add_button(0, dy, ButtonType.level, filename.replace('.txt', ''))
            dy += 2
        self.add_button(0, dy, ButtonType.menu)

        self.bg_sprite = animatedsprite.AnimatedSprite('image')
        self.bg_sprite.play('menu')
        self.level_name = ''

    def update(self):
        self.buttons = []
        dy = 4
        for filename in os.listdir('data/lvl'):
            self.add_button(0, dy, ButtonType.level, filename.replace('.txt', ''))
            dy += 2
        self.add_button(0, dy, ButtonType.menu)

    def draw(self, screen, img_hand):
        self.bg_sprite.draw(screen, img_hand)
        super().draw(screen, img_hand)

    def input(self, input_hand):
        for b in self.buttons:
            if b.rect.collidepoint(input_hand.mouse_x, input_hand.mouse_y):
                if input_hand.mouse_released[1]:
                    if b.type is ButtonType.level:
                        self.level_name = b.txtbox.string
                    return b.press()

        return self.state


class EditorSelectMenu(Menu):
    def __init__(self):
        super().__init__(gameloop.State.editor_select)
        self.add_button(0, 10, ButtonType.menu)
        dy = 2
        for filename in os.listdir('data/lvl'):
            self.add_button(0, 2 * dy, ButtonType.edit, filename.replace('.txt', ''))
            dy += 1

        self.add_button(0, 2 * dy, ButtonType.new)

        self.bg_sprite = animatedsprite.AnimatedSprite('image')
        self.bg_sprite.play('menu')
        self.level_name = ''

    def update(self):
        self.buttons = []
        self.add_button(0, 10, ButtonType.menu)
        dy = 2
        for filename in os.listdir('data/lvl'):
            self.add_button(0, 2 * dy, ButtonType.edit, filename.replace('.txt', ''))
            dy += 1
        self.add_button(0, 2 * dy, ButtonType.new)

    def draw(self, screen, img_hand):
        self.bg_sprite.draw(screen, img_hand)
        super().draw(screen, img_hand)

    def input(self, input_hand):
        for b in self.buttons:
            if b.rect.collidepoint(input_hand.mouse_x, input_hand.mouse_y):
                if input_hand.mouse_released[1]:
                    if b.type is ButtonType.edit:
                        self.level_name = b.txtbox.string
                    return b.press()

        self.level_name = ''
        return self.state


class LevelCreationMenu(Menu):
    def __init__(self):
        super().__init__(gameloop.State.level_creation)
        self.input_name = TextInput(0, 6)
        self.add_button(0, 8, ButtonType.create)
        self.add_button(0, 10, ButtonType.editor, 'BACK')
        self.bg_sprite = animatedsprite.AnimatedSprite('image')
        self.bg_sprite.play('menu')

    def draw(self, screen, img_hand):
        self.bg_sprite.draw(screen, img_hand)
        self.input_name.draw(screen, img_hand)
        super().draw(screen, img_hand)

    def input(self, input_hand):
        self.input_name.input(input_hand)
        return super().input(input_hand)


class EditorPauseMenu(Menu):
    def __init__(self):
        super().__init__(gameloop.State.editor_paused)
        self.add_button(0, 4, ButtonType.edit)
        self.add_button(0, 6, ButtonType.test)
        self.add_button(0, 8, ButtonType.save)
        self.add_button(0, 10, ButtonType.menu)


class OptionsMenu(Menu):
    def __init__(self):
        super().__init__(gameloop.State.options)
        self.bg_sprite = animatedsprite.AnimatedSprite('image')
        self.bg_sprite.play('menu')
        self.music_slider = VolumeSlider(0, 5, SliderType.music)
        self.sound_slider = VolumeSlider(0, 8, SliderType.sound)
        self.add_button(0, 10, ButtonType.menu)

    def draw(self, screen, img_hand):
        self.bg_sprite.draw(screen, img_hand)
        super().draw(screen, img_hand)
        self.music_slider.draw(screen, img_hand)
        self.sound_slider.draw(screen, img_hand)

    def input(self, input_hand, snd_hand):
        self.music_slider.input(input_hand, snd_hand)
        self.sound_slider.input(input_hand, snd_hand)
        return super().input(input_hand)


class VolumeSlider():
    def __init__(self, x, y, type):
        self.type = type
        self.button_up = Button(x + 4, y, ButtonType.options, '+')
        self.button_down = Button(x - 4, y, ButtonType.options, '-')
        self.volume = 100
        self.title = TextInput(x, y - 1, type.name)
        self.txtbox = TextInput(x, y, str(self.volume))

    def draw(self, screen, img_hand):
        self.button_up.draw(screen, img_hand)
        self.button_down.draw(screen, img_hand)
        self.title.draw(screen, img_hand)
        self.txtbox.draw(screen, img_hand)

    def input(self, input_hand, snd_hand):
        changed = False

        if self.button_up.rect.collidepoint(input_hand.mouse_x, input_hand.mouse_y):
            if input_hand.mouse_released[1]:
                if self.volume < 100:
                    self.volume += 10
                    changed = True
        if self.button_down.rect.collidepoint(input_hand.mouse_x, input_hand.mouse_y):
            if input_hand.mouse_released[1]:
                if self.volume > 0:
                    self.volume -= 10
                    changed = True

        if changed:
            if self.type is SliderType.music:
                pygame.mixer.music.set_volume(self.volume / 100)
            elif self.type is SliderType.sound:
                snd_hand.set_volume(self.volume / 100)
                sound = random.choice(list(snd_hand.sounds.keys()))
                snd_hand.sounds[sound].play()

            self.txtbox.txtbox.set_string(str(self.volume))


class Button(animatedsprite.AnimatedSprite):
    def __init__(self, x, y, button_type, text=''):
        super().__init__('menu')
        self.rect.x = x * helpers.TILE_SIZE + 0.5 * helpers.SCREEN_WIDTH - 16 * helpers.SCALE
        self.rect.y = y * helpers.TILE_SIZE
        if text == '':
            text = button_type.name
        self.txtbox = textbox.Textbox(text, self.rect.centerx, self.rect.y)
        self.txtbox.y = y
        self.type = button_type

        self.play('button')

    def draw(self, screen, img_hand):
        super().draw(screen, img_hand)
        self.txtbox.draw(screen, img_hand)

    def press(self):
        if self.type is ButtonType.play:
            return gameloop.State.level_select
        elif self.type is ButtonType.options:
            return gameloop.State.options
        elif self.type is ButtonType.resume:
            return gameloop.State.play
        elif self.type is ButtonType.quit:
            return gameloop.State.quit
        elif self.type is ButtonType.menu:
            return gameloop.State.menu
        elif self.type is ButtonType.level:
            return gameloop.State.play
        elif self.type is ButtonType.edit:
            return gameloop.State.editor
        elif self.type is ButtonType.editor:
            return gameloop.State.editor_select
        elif self.type is ButtonType.new:
            return gameloop.State.level_creation
        elif self.type is ButtonType.create:
            return gameloop.State.editor
        elif self.type is ButtonType.save:
            return gameloop.State.save
        elif self.type is ButtonType.test:
            return gameloop.State.editor_play


class TextInput(animatedsprite.AnimatedSprite):
    def __init__(self, x, y, text=''):
        super().__init__('menu')
        self.rect.x = x + 0.5 * helpers.SCREEN_WIDTH - 16 * helpers.SCALE
        self.rect.y = y * helpers.TILE_SIZE
        self.txtbox = textbox.Textbox(text, self.rect.centerx, self.rect.y)
        self.max_length = 7

        self.play('button')

    def draw(self, screen, img_hand):
        super().draw(screen, img_hand)
        self.txtbox.draw(screen, img_hand)

    def input(self, input_hand):
        for key in input_hand.keys_pressed:
            if input_hand.keys_pressed[key]:
                if key == pygame.K_BACKSPACE:
                    self.txtbox.remove_char()
                else:
                    if len(self.txtbox.string) < self.max_length:
                        self.txtbox.add_char(chr(key))