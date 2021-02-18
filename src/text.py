from pygame import Surface
import pygame
from . import constants as c, res, tools
from .tools import cfg
from .core import *
import json


class MarioText:
    def setup():
        with open(c.text_img_info_path) as f:
            info = json.loads(f.read())
            image_name = info['image_name']
            text = info['text']
            colorkey = tuple(text['colorkey'])
            alpha = text['alpha']
            MarioText.alpha_rect = Rect(*alpha)
            alpha_row_num = text['alpha_row_num']
            alpha_rows = text['alpha_rows']
            alpha_lastrow_num = text['alpha_lastrow_num']
            alpha_span = text['alpha_span']
            copy_right = tuple(text['copy_right'])
            dash = tuple(text['dash'])
            multi = tuple(text['multi'])
            exclam = tuple(text['exclam'])

        char_dict = {}
        alpha_list = []
        fimg = res.images[image_name]
        x_begin = alpha[0]
        for row in range(alpha_rows):
            row_num = alpha_row_num if row < alpha_rows - 1 else alpha_lastrow_num
            for i in range(row_num):
                img = res.trim_image(fimg, *tuple(alpha), 1, colorkey)
                alpha_list.append(img)
                alpha[0] += alpha[2] + alpha_span[0]
            alpha[0] = x_begin
            alpha[1] += alpha[3] + alpha_span[1]
        ord_0, ord_A = ord('0'), ord('A')
        for i in range(10):
            char_dict[chr(ord_0 + i)] = alpha_list[i]
        for i in range(10, len(alpha_list)):
            char_dict[chr(ord_A + i - 10)] = alpha_list[i]

        char_dict['copy_right'] = res.trim_image(fimg, *copy_right, 1,
                                                 colorkey)
        char_dict['-'] = res.trim_image(fimg, *dash, 1, colorkey)
        char_dict['×'] = res.trim_image(fimg, *multi, 1, colorkey)
        char_dict['!'] = res.trim_image(fimg, *exclam, 1, colorkey)

        img = Surface((alpha[2], alpha[3]))
        img.fill((0, 0, 0))
        img.set_colorkey((0, 0, 0))
        char_dict[' '] = img

        MarioText.char_dict = char_dict
        MarioText.C.setup()

    class C:
        def setup():
            C = MarioText.C
            maker = cfg.CfgMaker()

            ah = C.alignH = maker.make(3)
            av = C.alignV = maker.make(3)

            ah.left, ah.center, ah.right = ah.add(3)
            av.down, av.center, av.up = av.add(3)

    wrong_char = 'X'

    def label(content,
              line_max=-1,
              spacing=(0, 0),
              margin=(0, 0),
              scale=1,
              config1=LineLayout.C.ALIGN_LEFT,
              config2=LineLayout.C.ALIGN_DOWN,
              arg2_is_max_width=False):

        if len(content) == 0: return Surface((0, 0))
        content = content.upper()
        C = LineLayout.C
        mode1 = C.ORIENT_DOWN | C.TYPESET_PILE | config1
        mode2 = C.ORIENT_RIGHT | C.TYPESET_PILE | config2

        if line_max != -1 and not arg2_is_max_width:
            line_max = MarioText.alpha_rect.width * line_max + \
                (line_max - 1) * spacing[0]

        def create_ly2():
            ly2 = HLineLayout(Rect(0, 0, 1, 1), mode2)
            ly2.set_spacing(spacing[0])
            ly2.set_marginY(margin[0])
            return ly2

        index = 0
        imgs_row = []
        imgs_one_row = []
        ly2 = create_ly2()
        n = len(content)
        while True:
            is_final = index == n
            if not is_final:
                char = content[index]
                if char not in MarioText.char_dict:
                    char = MarioText.wrong_char
                cimg = MarioText.char_dict[char]
                imrect = cimg.get_rect()
            if is_final or (line_max != -1 and
                            imrect.width + spacing[0] + ly2.expanded_rect.width
                            > line_max - margin[0] * 2):

                ly2.expand()
                imgrow = Surface((ly2.rect.width, ly2.rect.height))
                imgrow.fill((255, 0, 0))
                for img, rect in imgs_one_row:
                    imgrow.blit(img, rect)
                imgrow.set_colorkey((255, 0, 0))
                imgs_row.append((imgrow, imgrow.get_rect()))
                imgs_one_row.clear()
                ly2 = create_ly2()
                if is_final: break
            else:
                ly2.push(imrect)
                imgs_one_row.append((cimg, imrect))
                index += 1

        ly1 = VLineLayout(Rect(0, 0, 1, 1), mode1)
        ly1.set_spacing(spacing[1])
        ly1.set_marginY(margin[1])
        for _, rect in imgs_row:
            ly1.push(rect)
        ly1.expand()
        retimg = Surface((ly1.rect.width, ly1.rect.height))
        retimg.fill((255, 0, 0))
        for img, rect in imgs_row:
            retimg.blit(img, rect)
        retimg.set_colorkey((255, 0, 0))
        if scale != 1:
            retimg = tools.image_scale(retimg, scale)
        return retimg


class Txt:

    cfg_txt_scale = c.TEXT_SCALE
    cfg_spacing = c.TEXT_SPACING

    def setup():
        Txt.mario = Txt.simple_label('mario')
        Txt.multi = Txt.simple_label('×')
        Txt.world = Txt.simple_label('world')
        Txt.time = Txt.simple_label('time')
        Txt.time_up = Txt.simple_label('time up')
        Txt.game_over = Txt.simple_label('game over')

        Txt.lv_0_1 = Txt.simple_label('0-1')
        Txt.lv_0_2 = Txt.simple_label('0-2')
        Txt.lv_0_3 = Txt.simple_label('0-3')
        Txt.lv_0_4 = Txt.simple_label('0-4')

    def simple_label(content):
        return MarioText.label(content,
                               spacing=Txt.cfg_spacing,
                               scale=Txt.cfg_txt_scale)


def setup():
    MarioText.setup()
    Txt.setup()
