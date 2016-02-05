import animatedsprite
import helpers
import physicsobject


class Tile(animatedsprite.AnimatedSprite):
    def __init__(self, x, y, path):
        animatedsprite.AnimatedSprite.__init__(self, path)

        self.rect.x = x
        self.rect.y = y


class Wall(Tile):
    def __init__(self, x, y, path):
        Tile.__init__(self, x, y, path)
        self.index = 0
        self.show_frame('idle', self.index)
        self.path = path
        self.destroyed = False
        self.friction = 0.125 * helpers.SCALE
        self.slide_speed = 0.25 * helpers.SCALE
        if self.path == 'ice':
            self.friction = 0.01 * helpers.SCALE
            self.slide_speed = helpers.TERMINAL_VELOCITY

    def update(self, room):
        up = right = down = left = 0
        for w in room.walls:
            if self.path != 'spike':
                if w.path != self.path:
                    continue

            if w.rect.x == self.rect.x:
                if w.rect.y == self.rect.y - helpers.TILE_SIZE:
                    up = 1
                if w.rect.y == self.rect.y + helpers.TILE_SIZE:
                    down = 1

            if w.rect.y == self.rect.y:
                if w.rect.x == self.rect.x + helpers.TILE_SIZE:
                    right = 1
                if w.rect.x == self.rect.x - helpers.TILE_SIZE:
                    left = 1

        if self.rect.y - helpers.TILE_SIZE < 0:
            up = 1
        elif self.rect.y + helpers.TILE_SIZE >= helpers.SCREEN_HEIGHT:
            down = 1

        if self.rect.x + helpers.TILE_SIZE >= helpers.SCREEN_WIDTH:
            right = 1
        elif self.rect.x - helpers.TILE_SIZE < 0:
            left = 1

        self.index = int(str(up) + str(right) + str(down) + str(left), 2)
        self.show_frame('idle', self.index)


class Ladder(Tile):
    def __init__(self, x, y):
        Tile.__init__(self, x, y, 'ladder')
        self.top = True
        self.destroyed = False

    def update(self, room):
        self.top = True
        if self.rect.y > 0:
            for l in room.ladders:
                if l.rect.x == self.rect.x and l.rect.y == self.rect.y - helpers.TILE_SIZE:
                    self.top = False
                    break


class Spike(Wall):
    def __init__(self, x, y, index):
        Tile.__init__(self, x, y, 'thorns')
        self.show_frame('idle', index)
        self.path = 'spike'


class Checkpoint(Tile):
    def __init__(self, x, y):
        Tile.__init__(self, x, y, 'checkpoint')
        self.show_frame('idle', 0)

        self.active = False

    def update(self, room):
        if self.active:
            self.show_frame('idle', 0)
        else:
            self.show_frame('idle', 0)


class Water(Tile):
    def __init__(self, x, y, surface):
        Tile.__init__(self, x, y, 'water')
        self.surface = surface

        if self.surface:
            self.play('surface')
        else:
            self.play('idle')


class Destroyable(Wall):
    def __init__(self, x, y):
        Wall.__init__(self, x, y, 'destroyable')
        self.destroyed = False
        self.debris = animatedsprite.Group()

    def update(self, room):
        if not self.destroyed:
            self.play('idle')
        else:
            self.play('explode')
            self.debris.update(room)

    def destroy(self):
        self.debris.add(physicsobject.Debris(self.rect.x, self.rect.y, 5, 5, 'idle', 'destroyable_debris'))
        self.debris.add(physicsobject.Debris(self.rect.x, self.rect.y, 5, -5, 'idle', 'destroyable_debris'))
        self.debris.add(physicsobject.Debris(self.rect.x, self.rect.y, -5, 5, 'idle', 'destroyable_debris'))
        self.debris.add(physicsobject.Debris(self.rect.x, self.rect.y, -5, -5, 'idle', 'destroyable_debris'))
        self.destroyed = True

    def reset(self):
        self.destroyed = False
        self.debris.empty()

    def draw(self, screen, img_hand):
        Wall.draw(self, screen, img_hand)
        self.debris.draw(screen, img_hand)


class Platform(physicsobject.PhysicsObject):
    def __init__(self, x, y, vertical=False):
        physicsobject.PhysicsObject.__init__(self, x, y, 'platform')
        self.destroyed = False
        self.gravity = 0
        self.bounce = 1
        self.vertical = vertical
        self.slide_speed = 0.25 * helpers.SCALE
        if self.vertical:
            self.dy = 0.5 * helpers.SCALE
        else:
            self.dx = 0.5 * helpers.SCALE
        self.spawn_x = x
        self.spawn_y = y

    def update(self, room):
        physicsobject.PhysicsObject.update(self, room)

    def reset(self):
        self.x = self.spawn_x
        self.y = self.spawn_y
        if self.vertical:
            self.dy = 0.5 * helpers.SCALE
        else:
            self.dx = 0.5 * helpers.SCALE
