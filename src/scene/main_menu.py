import pygame
import json

from .. import res, setup as s, constants as c
from .base import Scene
from ..components import info, player, items
from ..text import Txt
from ..core import *
from ..tools import dstr_b0, image_scale


class MainMenuScene(Scene):

    cfg_top_margin = c.Board_Top_Margin
    cfg_spcingV = 22
    cfg_titleband_scale = 2.8

    #暂时
    cfg_mario_x = 80
    ground_y = 536

    cfg_mushroom_spacing = 42
    cfg_mushroom_scale = 0.8

    cfg_fadout  = 1200

    def __init__(self, name):
        super().__init__(name)

        self.load_data()
        self._1p = True
        self.setup_ui()
        #self.setup_sound()

    def start(self, pre_scene):
        super().start(pre_scene)
        self.setup_background(pre_scene)
        self.timer_update = pygame.time.Clock()
        self.timer_render = pygame.time.Clock()
        res.musics['main_theme'].play(-1, 0)


    def finish(self, next_scene_name):
        super().finish(next_scene_name)
        res.musics['main_theme'].fadeout(self.cfg_fadout)


    def load_data(self):

        board = info.board

        self.top_mark = 0
        self.level_imgname = board.levelname

        board.n_life = board.n_player2_life = c.BeginingLifeNum

    def save_data(self):
        pass

    def setup_background(self, pre_scene):
        # ...
        bgpic = res.images[self.level_imgname]
        self.bgpic = image_scale(bgpic, c.IMAGE_SCALE)
        self.viewport = s.game.screen.get_rect()

    def tpl(self, _img, is_show=True):
        combin = [_img, _img.get_rect(), is_show]
        self.images.append(combin)
        return combin
        
    def setup_ui(self):

        self.images = []

        # 资源
        with open(c.title_info_path) as f:
            title_info = json.loads(f.read())
            image_name = title_info['image_name']
            titleband_rect = title_info['titleband_rect']
            colorkey = title_info['colorkey']
        titleband = res.trim_image(res.images[image_name],
                                   *tuple(titleband_rect),
                                   self.cfg_titleband_scale,
                                   colorkey=tuple(colorkey))
        self.titleband = self.tpl(titleband)
        self.screen = (s.game.screen, s.game.screen.get_rect())

        # 布局
        C = LineLayout.C
        self.layout = layout = VLineLayout(self.screen[1],
                                           mode=C.ALIGN_CENTER | C.ORIENT_DOWN)
        layout.set_marginY(self.cfg_top_margin)
        layout.set_spacing(self.cfg_spcingV)

        board = info.board
        layout.push(board.layout.rect)
        board.update_layout()

        layout.push(self.titleband[1])

        txt_1p = Txt.simple_label('1 player game')
        txt_2p = Txt.simple_label('2 player game')
        txt_top = Txt.simple_label('top - ' + dstr_b0(self.top_mark, 6))

        self.img_1p = img_1p = self.tpl(txt_1p)
        self.img_2p = img_2p = self.tpl(txt_2p)
        img_top = self.tpl(txt_top)

        layout.push(img_1p[1])
        layout.push(img_2p[1])
        layout.push_space(8)
        layout.push(img_top[1])

        mario_img = player.mario.right_small_normal[player.STAND]
        luigi_img = player.luigi.right_small_normal[player.STAND]
        self.mario = mario = self.tpl(mario_img)
        self.luigi = luigi = self.tpl(luigi_img)
        mario[1].x = self.cfg_mario_x
        luigi[1].y = mario[1].y = self.ground_y - self.mario[1].height
        luigi[1].x = self.cfg_mario_x + self.mario[1].width + 20


        mash_room_img = items.MushRoom.get_image()
        mash_room_img = image_scale(mash_room_img, self.cfg_mushroom_scale)
        self.mash_room = self.tpl(mash_room_img)
        self.mash_room[1].x = img_1p[1].x - self.cfg_mushroom_spacing
        self._set_mushroom_pos()

    def change_play_mode(self):
        self._1p = not self._1p
        self._set_mushroom_pos()

    def _set_mushroom_pos(self):
        if self._1p:
            _ooo_ = self.img_1p
            self.luigi[2] = False
        else:
            _ooo_ = self.img_2p
            self.luigi[2] = True
        dh = self.mash_room[1].height / 2 - _ooo_[1].height / 2
        self.mash_room[1].y = _ooo_[1].y - dh

    _is_mode_keydown_ = False

    def event_handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == c.K_UP[0] or event.key == c.K_DOWN[0]:
                self.change_play_mode()
                self.timer_choose = 0
                self._is_mode_keydown_ = True
                res.sounds['fireball'].play()
            elif event.key == c.K_ENTER:
                info.board.n_player = 1 if self._1p else 2
                res.musics['flagpole'].play()
                self.finish('load screen')
        elif event.type == pygame.KEYUP:
            if event.key == c.K_UP[0] or event.key == c.K_DOWN[0]:
                self._is_mode_keydown_ = False
    cfg_choose_speed = 500  # ms
    timer_choose = 0

    def update(self):
        d_ms = self.timer_update.tick(c.UpdateFPS)

        if self._is_mode_keydown_:
            self.timer_choose += d_ms
            if self.timer_choose > self.cfg_choose_speed:
                self.change_play_mode()
                self.timer_choose = 0

    def render(self, screen):
        d_ms = self.timer_render.tick(c.RenderFPS)

        screen.blit(self.bgpic, self.viewport)

        for (img, rect, is_show) in self.images:
            if is_show:
                screen.blit(img, rect)

        info.board.render(screen, d_ms)
