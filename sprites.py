# Sprite classes for HP
from settings import *
import pygame as pg
import math
vec = pg.math.Vector2


# player class
class Player(pg.sprite.Sprite):
    def __init__(self, game, img_x, img_y, img_width, img_height):
        pg.sprite.Sprite.__init__(self)
        self.game = game

        self.player_spritesheet = Spritesheet(os.path.join(img_folder, "gunguy.png"))
        self.image_orig = self.player_spritesheet.get_image(img_x, img_y, img_width, img_height)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig

        self.rect = self.image.get_rect()
        self.hitbox = pg.rect.Rect(self.rect.x, self.rect.y, (img_width - 2) * PIXEL_MULT,
                                   (img_height - 2) * PIXEL_MULT)

        self.pos = vec(0, 0)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rot = 0
        self.mouse_offset = 0

        self.current_weapon = Weapon(self.game)

    def update(self):
        self.rotate()
        self.move()
        self.act()

    def move(self):
        # set acc to 0 when not pressing so it will stop accelerating
        self.acc = vec(0, 0)

        # move on buttonpress
        key_state = pg.key.get_pressed()
        if key_state[pg.K_w]:
            self.vel.y -= PLAYER_ACCELERATION
        if key_state[pg.K_a]:
            self.vel.x -= PLAYER_ACCELERATION
        if key_state[pg.K_s]:
            self.vel.y += PLAYER_ACCELERATION
        if key_state[pg.K_d]:
            self.vel.x += PLAYER_ACCELERATION

        # apply friction
        self.acc += self.vel * PLAYER_FRICTION
        # equations of motion
        self.vel += self.acc

        # first move x then y for better collision detection

        self.pos.x += self.vel.x + 0.5 * self.acc.x
        self.rect.center = self.pos
        self.hitbox.center = self.pos
        self.check_collision('x')

        self.pos.y += self.vel.y + 0.5 * self.acc.y
        self.rect.center = self.pos
        self.hitbox.center = self.pos
        self.check_collision('y')

        # constrain to screen
        if self.pos.x > WIDTH:
            self.pos.x = WIDTH
        if self.pos.x < 0:
            self.pos.x = 0
        if self.pos.y < 0:
            self.pos.y = 0
        if self.pos.y > HEIGHT:
            self.pos.y = HEIGHT

        # set rect to new calculated pos
        self.rect.center = self.pos
        self.hitbox.center = self.pos

    def check_collision(self, axis):
        for wall in self.game.walls:
            if self.hitbox.colliderect(wall):
                if axis == 'x':
                    if self.vel.x < 0:
                        self.hitbox.left = wall.rect.right
                    elif self.vel.x > 0:
                        self.hitbox.right = wall.rect.left
                    self.pos.x = self.hitbox.centerx
                    self.rect.centerx = self.hitbox.centerx
                else:
                    if self.vel.y < 0:
                        self.hitbox.top = wall.rect.bottom
                    elif self.vel.y > 0:
                        self.hitbox.bottom = wall.rect.top
                    self.pos.y = self.hitbox.centery
                    self.rect.centery = self.hitbox.centery

    def rotate(self):
        # turns sprite to face towards mouse
        mouse = pg.mouse.get_pos()
        # calculate relative offset from mouse and angle
        self.mouse_offset = (mouse[1] - self.rect.centery, mouse[0] - self.rect.centerx)
        self.rot = 180 + round(math.degrees(math.atan2(self.mouse_offset[1], self.mouse_offset[0])), 1)

        # make sure image keeps center
        old_center = self.rect.center
        self.image = pg.transform.rotate(self.image_orig, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = old_center

    def act(self):
        for event in self.game.all_events:
            if event.type == pg.MOUSEBUTTONDOWN:
                self.attack()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    self.current_weapon.reload()

    def attack(self):
        self.current_weapon.shoot(self.rect.centerx, self.rect.centery, self.rot)


class Spritesheet(object):
    # utility class for loading and parsing sprite sheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, img_x, img_y, img_width, img_height):
        # grab an image out of a larger spritesheet
        image = pg.Surface((img_width, img_height))
        image.blit(self.spritesheet, (0, 0), (img_x, img_y, img_width, img_height))
        image = pg.transform.scale(image, (img_width * PIXEL_MULT, img_height * PIXEL_MULT))
        return image


class Tile(pg.sprite.Sprite):
    def __init__(self, is_wall):
        pg.sprite.Sprite.__init__(self)
        self.is_wall = is_wall
        self.image = None


class Level(object):
    # loads a level and makes its tiles
    def __init__(self, game, level_file):
        self.level_file = level_file
        self.game = game

    # adds all level tiles to group as sprites
    def build(self):
        with open(self.level_file, 'r') as f:
            for ln, line in enumerate(f.readlines()):
                for cn, char in enumerate(line):
                    try:
                        pos = KEY[char][0]
                        wall = KEY[char][1]
                        t = Tile(wall)
                        t.image = self.game.spritesheet.get_image(pos[0], pos[1], TILESIZE, TILESIZE)
                        t.rect = t.image.get_rect()
                        t.rect.x = cn * TILESIZE * PIXEL_MULT
                        t.rect.y = ln * TILESIZE * PIXEL_MULT
                        self.game.map_tiles.add(t)
                        self.game.all_sprites.add(t)
                        if wall:
                            self.game.walls.add(t)
                    except KeyError:
                        pass


class Weapon(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.max_ammo = 10
        self.ammo = self.max_ammo
        self.delay = 100
        self.last_shot = pg.time.get_ticks()

    def shoot(self, x, y, rot):
        now = pg.time.get_ticks()
        if self.ammo > 0:
            if now - self.last_shot > self.delay:
                self.ammo -= 1
                self.last_shot = now
                Bullet(self.game, x, y, rot)

    def reload(self):
        self.ammo = self.max_ammo


class Bullet(pg.sprite.Sprite):
    def __init__(self, game, x, y, rot):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.image = pg.Surface((1 * PIXEL_MULT, 1 * PIXEL_MULT))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.game.all_sprites.add(self)
        self.game.bullets.add(self)

        self.speed = 8
        self.vel = vec(0, 0)
        self.pos = vec(self.rect.center)

        self.dir = math.radians(rot+90)
        # calculates speed for given direction
        self.vel = vec(self.speed * math.cos(self.dir), -(self.speed * math.sin(self.dir)))

    def update(self):
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y
        self.rect.center = self.pos
        if self.rect.x > WIDTH or self.rect.x < 0 or self.rect.y > HEIGHT or self.rect.y < 0:
            self.kill()
