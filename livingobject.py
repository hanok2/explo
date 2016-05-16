import gameobject
import helpers
import particle
import math


class LivingObject(gameobject.PhysicsObject):
    def __init__(self, x, y, width, height, path, health=1):
        super().__init__(x, y, width, height, 0, 0, path)
        self.health = health
        self.alive = True
        self.gibs = []

    def update(self, room):
        last_x = self.x
        last_y = self.y

        super().update(room)

        if abs(self.x - last_x) > 0.5 * self.collider.width:
            self.x = last_x
            self.collider.x = self.x
            self.die()
        if abs(self.y - last_y) > 0.5 * self.collider.height:
            self.y = last_y
            self.collider.y = self.y
            self.die()

        for g in self.gibs:
            g.update(room)
            if not g.alive:
                self.gibs.remove(g)

    def draw(self, screen, img_hand):
        super().draw(screen, img_hand)

        for g in self.gibs:
            g.draw(screen, img_hand)

    def damage(self, amount, dx=0, dy=0):
        self.dx += dx
        self.dy += dy
        self.health -= amount
        if self.health <= 0:
            self.die()

    def die(self):
        self.alive = False
        self.base_dx = 0
        self.base_dy = 0
        self.dx = 0
        self.dy = 0

    def add_gib(self, x, y, dx, dy, path, part):
        x = self.collider.centerx + x * helpers.SCALE
        y = self.collider.centery + y * helpers.SCALE
        dx *= helpers.SCALE
        dy *= helpers.SCALE
        self.gibs.append(Gib(x, y, dx, dy, part, path))


class Gib(gameobject.PhysicsObject):
    def __init__(self, x, y, dx, dy, part, path):
        super().__init__(x, y, 0.5 * helpers.TILE_SIZE,
                         0.5 * helpers.TILE_SIZE, dx, dy, [path])

        self.alive = True
        self.dx = dx
        self.dy = dy
        for s in self.sprites:
            s.play(part, 0)
        self.collision_enabled = False
        self.bounce = 0.5
        self.friction = 0.75 * helpers.SCALE
        self.trail = []

    def update(self, room):
        super().update(room)
        if helpers.outside_screen(self.collider):
            if not self.trail:
                self.alive = False
        else:
            if math.hypot(self.dx, self.dy) > 0.5 * helpers.SCALE:
                p = particle.Particle(self.x, self.y, 0, 0, 'blood', False)
                self.trail.append(p)
                for s in self.sprites:
                    s.animate()

        for t in self.trail:
            t.update(room)
            if not t.alive:
                self.trail.remove(t)

    def draw(self, screen, img_hand):
        for t in self.trail:
            t.draw(screen, img_hand)
        super().draw(screen, img_hand)
