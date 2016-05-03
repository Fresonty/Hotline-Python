# Hotline Python

import pygame as pg
import random
import math
from settings import *
from sprites import *
import os


class Game:
    def __init__(self):
        # initialize game, pg and create window
        self.running = True
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.playing = True

        # using ordered updates so player will rendered last (on top)
        self.all_sprites = pg.sprite.OrderedUpdates()
        self.map_tiles = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.spritesheet = Spritesheet(os.path.join(img_folder, "spritesheet.png"))
        self.player = None

    def new(self):
        # start new game
        # SPRITE GROUPS
        self.all_sprites = pg.sprite.OrderedUpdates()
        # using ordered updates so player will rendered last (on top)
        self.map_tiles = pg.sprite.Group()
        self.walls = pg.sprite.Group()

        # OBJECTS
        l = Level(self, "level.txt")
        l.build()
        self.player = Player(self, 0, 0, 12, 12)

        # ADD TO SPRITE GROUP IN RIGHT ORDER
        self.all_sprites.add(self.player)
        # run game AFTER everything is set up
        self.run()

    def run(self):
        # game loop
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        # game loop - update
        self.all_sprites.update()
        # collision detected by sprites

    def events(self):
        # game loop - events
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

    def draw(self):
        # game loop - draw/ render
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)

        # *after* drawing everything, flip the display
        pg.display.flip()

    def show_start_screen(self):
        # show splash/ start screen
        pass

    def show_go_screen(self):
        # show game over screen
        pass

g = Game()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()
