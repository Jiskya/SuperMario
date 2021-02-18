from ..text import Txt
from ..core import *
from ..tools import dstr_b0
from .items import Coin
from .. import constants as c, res


StartLevel = ['0-1', 'level_1']

level_info_dict = {
    'level_1':{
        'brick': 0,
        'box': 0,
        'next_level':['0-2', 'level_2']
    },
    'level_2':{
        'brick': 1,
        'box': 1,
        'next_level':['0-3', 'level_3']
    },
    'level_3':{
        'brick': 3,
        'box': 3,
        'next_level':['0-4', 'level_4']
    },
    'level_4':{
        'brick': 2,
        'box': 2,
        'next_level':['0-1', 'level_1']
    }
}

class InfoBoard:
    cfg_info_spcing = 78
    cfg_info_row_spcing = 2

    cfg_mid_spacing_rate = 1.5
    cfg_coin_scale = 1.32


    # ................
    def __load_data():
        pass

    def __save_data():
        pass

    #cfg_coin_flash_speed = 200  # ms

    def tpl(self, _img, is_render=True):
        ret = [_img, _img.get_rect()]
        if is_render:
            self.images.append(ret)
        return ret

    def __init_ui__(self):
        C = LineLayout.C
        self.images = []

        self.layout = layout = HLineLayout(mode=C.TYPESET_CENTER
                                           | C.ORIENT_RIGHT
                                           | C.ALIGN_DOWN,
                                           spacing=self.cfg_info_spcing)
        self.lay_list = []
        self.vlay_mark = vlay_mark = VLineLayout(
            mode=C.ALIGN_LEFT
            | C.ORIENT_DOWN,
            spacing=self.cfg_info_row_spcing)

        self.hlay_coin = hlay_coin = HLineLayout(mode=C.ALIGN_DOWN
                                                 | C.ORIENT_RIGHT,
                                                 spacing=1)

        self.vlay_world = vlay_world = VLineLayout(
            mode=C.ALIGN_CENTER
            | C.ORIENT_DOWN,
            spacing=self.cfg_info_row_spcing)

        self.vlay_time = vlay_time = VLineLayout(
            mode=C.ALIGN_RIGHT
            | C.ORIENT_DOWN,
            spacing=self.cfg_info_row_spcing)

        self.lay_list.append(vlay_mark)
        self.lay_list.append(hlay_coin)
        self.lay_list.append(vlay_world)
        self.lay_list.append(vlay_time)

        self.img_mario = self.tpl(Txt.mario)
        mark = Txt.simple_label(dstr_b0(0, 6))
        self.img_mark = self.tpl(mark)
        vlay_mark.push(self.img_mario[1])
        vlay_mark.push(self.img_mark[1])
        vlay_mark.expand()

        r = Txt.simple_label(' ').get_rect()
        w2 = int(r.width * self.cfg_coin_scale)
        h2 = int(r.height * self.cfg_coin_scale)
        #r.y -= w2 - r.width
        ##r.x -= h2 - r.height

        self.coin = Coin(0, 0, dect_size=(w2, h2))
        hlay_coin.push(self.coin.rect)
        self.img_multi = self.tpl(Txt.multi)
        coin_num = Txt.simple_label(dstr_b0(0, 2))
        self.img_coin_num = self.tpl(coin_num)


        hlay_coin.push(self.img_multi[1])
        hlay_coin.push(self.img_coin_num[1])
        hlay_coin.expand()

        self.img_world = self.tpl(Txt.world)
        self.img_level = self.tpl(Txt.lv_0_1)
        vlay_world.push(self.img_world[1])
        vlay_world.push(self.img_level[1])
        vlay_world.expand()

        self.img_time = self.tpl(Txt.time)
        lefttime = Txt.simple_label(' ')
        self.img_lefttime = self.tpl(lefttime)
        vlay_time.push(self.img_time[1])
        vlay_time.push(self.img_lefttime[1])
        vlay_time.expand()

        layout.push(vlay_mark.rect)
        layout.push(hlay_coin.rect)
        layout.next_spacing(
            int(self.cfg_info_spcing * self.cfg_mid_spacing_rate))
        layout.push(vlay_world.rect)
        layout.push(vlay_time.rect)
        layout.expand()



    def __init__(self):
        global StartLevel
        self.n_mark = 0
        self.n_coin = 0
        self.n_level = StartLevel[0]
        self.levelname = StartLevel[1]
        self.n_lefttime = -1
        self.n_life = c.BeginingLifeNum
        self.n_player = 1
        self.current_level = None
        self.n_player2_life = c.BeginingLifeNum

        self.__init_ui__()

    def update_layout(self):
        self.layout.update()
        for lay in self.lay_list:
            lay.update()

    def set_mark(self, n):
        self.n_mark = n
        self.img_mark[0] = Txt.simple_label(dstr_b0(n, 6))

    def add_mark(self, n):
        self.set_mark(self.n_mark + n)

    def set_n_coin(self, n):
        self.n_coin = n
        self.img_coin_num[0] = Txt.simple_label(dstr_b0(n, 2))

    def add_coin(self, n=1):
        self.set_n_coin(self.n_coin + n)

    def set_level(self, n):
        self.n_level = n
        self.img_level[0] = Txt.simple_label(n)

    def set_lefttime(self, n):
        self.n_lefttime = n
        if n < 0:
            self.img_lefttime[0] = Txt.simple_label(' ')
        else:
            self.img_lefttime[0] = Txt.simple_label(str(n))
            _y = self.img_lefttime[1].y
            self.img_lefttime[1] = self.img_lefttime[0].get_rect()
            self.img_lefttime[1].right = self.img_time[1].right
            self.img_lefttime[1].y = _y

    def render(self, screen, dt_ms):
        if self.n_coin >= c.ONE_UP_NEDD_COIN:
            self.set_n_coin(0)
            self.n_life += 1
            res.sounds['one_up'].play()
        self.coin.update(dt_ms/1000)
        self.coin.render_abs(screen)
        for (img, rect) in self.images:
            screen.blit(img, rect)



def level_info():
    global level_info_dict
    return level_info_dict[board.levelname]

def setup():
    global board
    board = InfoBoard()
