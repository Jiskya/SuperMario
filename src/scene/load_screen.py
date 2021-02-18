import pygame
from .. import res, setup as s, constants as c
from .base import Scene
from ..core import *
from ..tools import Ims, image_scale
from ..text import Txt
from ..components import info, player


class LoadScreen(Scene):

    cfg_top_margin = c.Board_Top_Margin

    cfg_center_spcing = 40
    cfg_center_spcing2 = 62

    player_scale = 0.8

    def __init__(self, name):
        super().__init__(name)
        self.setup_ui()

    def setup_ui(self):
        self.ims = Ims()
        #布局
        C = LineLayout.C
        layout = VLineLayout(pygame.display.get_surface().get_rect(),
                             mode=C.ALIGN_CENTER | C.ORIENT_DOWN)
        layout.set_marginY(self.cfg_top_margin)

        layout.push(info.board.layout.rect)
        info.board.update_layout()

        level = info.board.n_level
        life = info.board.n_life
        p2life = info.board.n_player2_life
        self.imlevel = self.ims.add(Txt.simple_label('world ' + level))
        self.imlife = self.ims.add(Txt.simple_label('  X  %d' % life))
        self.imp2life = self.ims.add(Txt.simple_label('  X  %d' % p2life))

        marioimg = player.mario.right_small_normal[player.STAND]
        marioimg = image_scale(marioimg, self.player_scale)
        self.immario = self.ims.add(marioimg)
        luigiimg = player.luigi.right_small_normal[player.STAND]
        luigiimg = image_scale(luigiimg, self.player_scale)
        self.imluigi = self.ims.add(luigiimg)

    def setup_center(self):
        #布局
        C = LineLayout.C
        layout = VLineLayout(pygame.display.get_surface().get_rect(),
                             mode=C.ALIGN_CENTER | C.TYPESET_CENTER
                             | C.ORIENT_DOWN)

        layout.push(self.imlevel.rect)
        '''
        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        '''
        if info.board.n_player == 1:
            layout.next_spacing(self.cfg_center_spcing)
        else:
            pass
            #layout.next_spacing(self.cfg_center_spcing / 4)

        ly2 = HLineLayout()
        ly2.push(self.immario.rect)
        ly2.push(self.imlife.rect)
        ly2.expand()

        layout.push(ly2.rect)
        ly2.update()

        if info.board.n_player == 2:
            layout.next_spacing(self.cfg_center_spcing2)
            self.imluigi.is_show = True
            self.imp2life.is_show = True
            ly3 = HLineLayout()
            ly3.push(self.imluigi.rect)
            ly3.push(self.imp2life.rect)
            ly3.expand()
            layout.push(ly3.rect)
            ly3.update()
        else:
            self.imluigi.is_show = False
            self.imp2life.is_show = False

    def reset_info(self):
        self.imlevel.img = Txt.simple_label('world ' + info.board.n_level)
        self.imlife.img = Txt.simple_label('  X  %d' % info.board.n_life)
        self.imp2life.img = Txt.simple_label('  X  %d' %
                                             info.board.n_player2_life)

    def start(self, pre_scene):
        super().start(pre_scene)
        self.setup_center()
        self.timer_update = pygame.time.Clock()
        self.timer_render = pygame.time.Clock()
        self.load_adder = 0
        self.reset_info()

    def event_handle(self, event):
        pass

    def update(self):
        d_ms = self.timer_update.tick(c.UpdateFPS)

        self.load_adder += d_ms
        if self.load_adder > c.Load_Timeout * 1000:
            self.finish('level')

    def render(self, screen):
        d_ms = self.timer_render.tick(c.RenderFPS)
        screen.fill((0, 0, 0))
        self.ims.render(screen)
        info.board.render(screen, d_ms)
