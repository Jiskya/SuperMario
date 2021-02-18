import pygame
from pygame.sprite import spritecollideany
import time
import json
import sys

from .. import res, setup as s, constants as c
from .base import Scene
from ..core import *
from .. import tools
from ..text import Txt
from ..components import info, player, items, tile, enemy
from ..components.items import Item, Checkpoint, MarkNumber, Pipe

from ..ai.train import Train

def in_range(a, b):
    return a > b[0] and a < b[1]


class Level(Scene):

    free_range = (80, 300)
    ground_y = 532

    p1_type = player.Mario
    p2_type = player.Luigi
    p1_lv = None
    p2_lv = None

    def __init__(self, name):
        super().__init__(name)



    # ------------------ setup begin -----------------------

    def start(self, pre_scene):
        super().start(pre_scene)
        with open(c.maps_info_dir + '/' + info.board.levelname + '.json') as f:
            self.map_info = json.loads(f.read())
        self.setup_map()
        self.set_submap(0)
        self.setup_timers()

        res.musics['main_theme'].play(-1, 0)

        Train.run()
        #print(pygame.event.get())

    def setup_map(self):
        bgpic = res.images[info.board.levelname]
        self.bgpic = tools.image_scale(bgpic, c.IMAGE_SCALE)
        self.viewport = Rect.from_image(pygame.display.get_surface())

        self.maps_pos_info = self.map_info['maps']
        # info board
        self.allow_time = self.map_info['allow_time']
        info.board.set_lefttime(self.allow_time)
        info.board.current_level = self

        self.render_lists = LinkList()
        self.setup_player()
        self.setup_enemy()
        self.setup_ground()
        self.setup_tiles()
        self.setup_others()
        self.setup_checkpoint()

    def setup_player(self):
        self.players = LinkList()
        self.p1 = player.Player(0, self.p1_type)
        if self.p1_lv:
            self.p1.lv = self.p1_lv
        self.players.push(self.p1)
        self.n_player = info.board.n_player
        if self.n_player == 2:
            self.p2 = player.Player(1, self.p2_type)
            self.players.push(self.p2)
        #self.render_lists.push(self.players)

    def setup_enemy(self):
        self.enemy_list = LinkList()
        self.render_lists.push(self.enemy_list)
        self.enemy_info = self.map_info['enemy']

    def setup_ground(self):
        #self.ground_group = pygame.sprite.Group()
        self.ground_list = LinkList()
        for name in ['ground', 'step']:
            ground_info = self.map_info[name]
            for m in ground_info:
                i = Item(name, m['x'], m['y'], m['width'], m['height'])
                self.ground_list.push(i)
        if 'pipe' in self.map_info:
             for p in self.map_info['pipe']:
                 i = Pipe(p['x'], p['y'], p['width'], p['height'], p['type'])
                 self.ground_list.push(i)

    def setup_tiles(self):
        #self.tile_group = pygame.sprite.Group()
        self.tile_list = LinkList()
        brick_color = info.level_info()['brick']
        box_color = info.level_info()['box']

        if 'brick' in self.map_info:
            for b in self.map_info['brick']:
                x, y = b['x'], b['y']
                tp = b['type']
                if 'brick_num' in b:
                    pass
                else:
                    if 'top_coin' in b:
                        bk = tile.Brick(x, y, brick_color, tp, has_top_coin=True)
                    else:
                        bk = tile.Brick(x, y, brick_color, tp)
                    self.tile_list.push(bk)

        if 'box' in self.map_info:
            for b in self.map_info['box']:
                x, y = b['x'], b['y']
                tp = b['type']
                box = tile.create_box(x, y, box_color, tp)
                self.tile_list.push(box)
        self.render_lists.push(self.tile_list)

    def setup_checkpoint(self):
        self.checkpoint_list = LinkList()
        for ckp in self.map_info['checkpoint']:
            tp = ckp['type']
            ck = Checkpoint(ckp['x'], ckp['y'], ckp['width'], ckp['height'], ckp['type'])
            if tp == 0:
                ck.enemy_groupid = ckp['enemy_groupid']
                ck.triggered = False
            self.checkpoint_list.push(ck)


    def set_submap(self, index):
        self.map_index = index
        self.startx = self.maps_pos_info[index]['start_x']
        self.endx = self.maps_pos_info[index]['end_x']

        self.p1.rect.x = x0 = float(self.maps_pos_info[index]['player_x'])
        self.p1.rect.y = y0 = float(self.maps_pos_info[index]['player_y'])
        self.pre_mario_x = self.p1.rect.x
        self.mario_rel_rect = self.to_rel_rect(self.p1.rect)
        self.p1.fall()
        if self.n_player == 2:
            self.p2.rect.x = self.player_list[0].rect.right + 20
            self.p2.rect.y = y0
            self.p2.fall()
        #todo: !!!!!!!!!!!!!!!!!!!!!!!!!!
        

    def setup_timers(self):
        self.timer_update = pygame.time.Clock()
        self.timer_render = pygame.time.Clock()
        self.start_time = time.time()
        self.last_pdate_time = time.time()

    def setup_others(self):
        self.matter_list = LinkList()
        if 'coin' in self.map_info:
            for coin_info in self.map_info['coin']:
                self.matter_list.push(items.JumpCoin(coin_info['x'], coin_info['y'], jump=False))
        self.render_lists.push(self.matter_list)

        self.fire_list = LinkList()
        self.render_lists.push(self.fire_list)

        self.game_end = False
    # ------------------ setup end -----------------------






    #------------------- update begin --------------------

    def event_handle(self, event):
        self.p1.event_handle(event)
        if self.n_player == 2:
            self.p2.event_handle(event)

    def update(self):
        d_ms = self.timer_update.tick(c.UpdateFPS)
        tm = time.time()
        d_sec = tm - self.last_pdate_time
        self.last_pdate_time = tm
        self.update_player(d_sec)
        self.update_enemy(d_sec)
        self.update_fire(d_sec)
        self.update_others(d_sec)
        self.update_viewport()

    def render(self, screen):
        int_vp = self.viewport.to_int_rect()
        d_ms = self.timer_render.tick(c.RenderFPS)
        screen.blit(self.bgpic, int_vp)
        it1 = ListIter(self.render_lists)
        while it1.next():
            it2 = ListIter(it1.get())
            while it2.next():
                it2.get().render(screen, self.viewport)
        
        screen.blit(self.p1.image, self.mario_rel_rect)

        info.board.render(screen, d_ms)

    def update_player(self, d_sec):

        p1 = self.p1
        p1.update(d_sec)

        p1.rect.x += (p1.x_vel * d_sec)
        if p1.rect.x < self.startx:
            p1.rect.x = self.startx
        elif p1.rect.right > self.endx:
            p1.rect.right = self.endx

        p1.rect.y += (p1.y_vel * d_sec)

        if not p1.dead:
            self.ground_collide_detect(p1)
            self.player_collide_enemy_detect()
            self.player_collide_matter_detect()
            self.player_coliide_checkpoint_detect()

        self.player_check_will_die()

    def player_collide_enemy_detect(self):
        m = self.p1
        items = collide_detect_simple(m, self.enemy_list)
        for e, t in items: 
            if e.dead: continue
            if t == UP and not isinstance(e, enemy.PipeFlower):
                m.jump(False)
                res.sounds['stomp'].play()
                mc = (m.rect.x + m.rect.right)
                ec = (e.rect.x + e.rect.right)
                e.stamp(mc < ec)
                self.killenemy_mark(e)
            else:
                if isinstance(e, enemy.Koopa) and e.state == enemy.st_koopa_shell_static:
                    res.sounds['stomp'].play()
                    mc = (m.rect.x + m.rect.right)
                    ec = (e.rect.x + e.rect.right)
                    e.stamp(mc < ec)
                    self.killenemy_mark(e)
                else:
                    if self.p1.trancing: continue
                    if self.p1.on_attack_if_die():
                        self.player_go_die()

    def player_collide_matter_detect(self):
        p1 = self.p1
        xxx = collide_detect_simple(p1, self.matter_list)
        for i, t in xxx:
            if isinstance(i, items.JumpCoin) and not i.jumped:
                i.killed = True
                info.board.add_coin()
                self.gain_mark(c.Mark_COIN, i)
                res.sounds['coin'].play()
            elif isinstance(i, items.MushRoom):
                i.killed = True
                self.gain_mark(c.Mark_MushRoom, i)
                p1.powerup(player.LV_BIG)
            elif isinstance(i, items.Flower):
                i.killed = True
                self.gain_mark(c.Mark_Flower, i)
                p1.powerup(player.LV_FIRE)

    def player_coliide_checkpoint_detect(self):
        items = collide_detect_simple(self.p1, self.checkpoint_list)
        for ck, t in items:
            if ck.type == 0 and not ck.triggered:
                ck.triggered = True
                gid = ck.enemy_groupid
                group = self.enemy_info[str(gid)]
                for one in group:
                    es = enemy.create_enemy(one)
                    self.enemy_list.link(es)


    def update_fire(self, d_sec):
        it1 = ListIter(self.fire_list)
        while it1.next():
            fire = it1.get()
            if fire.killed:
                it1.remove_this()
            else:
                fire.update(d_sec)
                fire.rect.x += fire.x_vel * d_sec
                fire.rect.y += fire.y_vel * d_sec
                self.ground_collide_detect(fire)
                enemys = collide_detect_simple(fire, self.enemy_list)
                for e, t in enemys:
                    if e.dead: continue
                    self.killenemy_mark(e)
                    res.sounds['kick'].play()
                    e.go_die()
                    fire.killed = True
                    it1.remove_this()
                    break

    def update_enemy(self, d_sec):
        it1 = ListIter(self.enemy_list)
        while it1.next():
            e = it1.get()
            if e.killed:
                it1.remove_this()
            else:
                self.update_one_enemy(e, d_sec)

    def update_one_enemy(self, e, d_sec):
        e.update(d_sec)
        e.rect.x += e.x_vel * d_sec
        e.rect.y += e.y_vel * d_sec
        if e.collide:
            self.ground_collide_detect(e)
            self.enemy_collide_enemy_detect(e)

        self.enemy_check_will_die(e)

    def enemy_collide_enemy_detect(self, enem):
        if enem.dead: return
        enemys = collide_detect_simple(enem, self.enemy_list)
        for e, t in enemys:
            if e.dead or e == enem: continue
            if isinstance(e, enemy.Koopa) and e.state == enemy.st_koopa_shell_run:
                self.killenemy_mark(e)
                res.sounds['kick'].play()
                enem.go_die()

    def ground_collide_detect(self, m):

        if m.rect.x < self.startx:
            m.touch_x(None, False)
        elif m.rect.right > self.endx:
            m.touch_x(None, True)

        items = collide_detect_simple(m, self.ground_list)
        items += collide_detect_simple(m, self.tile_list)
        standing_bottom_empty = True
        for i,t in items:
            if t == UP:
                m.rect.bottom = i.rect.y
                m.touch_ground(i)
                standing_bottom_empty = False

            elif t == LEFT:
                m.rect.right = i.rect.x
                m.touch_x(i, False)

            elif t == RIGHT:
                m.rect.x = i.rect.right
                m.touch_x(i, True)

            elif t == DOWN:
                m.rect.y = i.rect.bottom
                m.touch_ceil(i)
            if i:
                pass

        if m.y_vel != 0 or m.y_acc != 0:
            standing_bottom_empty = False

        if standing_bottom_empty:
            m.fall()
    # def check_will_fall(self, m):
    #     #m = player.mario
    #     if m.y_vel == 0 and m.y_acc == 0:
    #         m.rect.y += 1
    #         is_fall = True
    #         items = collide_detect_simple(m, self.ground_group)
    #         items += collide_detect_simple(m, self.tile_group)
    #         for i,t in items:
    #             if t == UP:
    #                 is_fall = False
    #         m.rect.y -= 1
    #         if is_fall: m.fall()


    _pre_t = time.time()

    game_end = False
    game_end_time = 0
    def player_check_will_die(self):
        m = self.p1

        tm = time.time()
        if tm - self._pre_t > 1:
            self._pre_t = tm
            t2 = tm - self.start_time
            lefttime = int(self.allow_time - t2)
            info.board.set_lefttime(lefttime)
            if lefttime == 0:
                self.player_go_die()
        scr = pygame.display.get_surface().get_rect()
        if not m.dead and m.rect.y > scr.bottom:
            self.player_go_die()
        if m.dead and m.rect.y > scr.bottom + 100:
            self.finish('load screen')

        if not self.game_end and m.rect.right > self.endx - c.Level_End_X:
            self.game_end = True
            self.game_end_time = time.time()
            res.musics['main_theme'].stop()
            res.musics['stage_clear'].play()

        if self.game_end:
            if (time.time() - self.game_end_time) > 5:
                self.game_end = False
                Train.success()
                nxlevel = info.level_info()['next_level']
                info.board.set_level(nxlevel[0])
                info.board.levelname = nxlevel[1]
                self.p1.lv = self.p1.lv
                self.finish('load screen')


    def enemy_check_will_die(self, e):
        scr = pygame.display.get_surface().get_rect()
        if not e.dead and e.rect.y > scr.bottom + 100:
            e.killed = True

    def player_go_die(self):
        res.musics['main_theme'].stop()
        res.musics['death'].play()
        self.p1.go_die()
        info.board.n_life -= 1
        Train.end()

    mutikill_timeer = 0
    mutikill = 0
    
    def update_others(self, d_sec):
        self.mutikill_timeer += d_sec
        if self.mutikill_timeer > c.MutiKill_Timeout:
            self.mutikill = 0
            self.mutikill_timeer = 0

        it1 = ListIter(self.tile_list)
        while it1.next():
            t = it1.get()
            t.update(d_sec)
            t.rect.y += t.y_vel * d_sec
            if len(t.sub_sprites) != 0:
                for s in t.sub_sprites:
                    self.matter_list.push(s)
                t.sub_sprites.clear()

        it2 = ListIter(self.matter_list)
        while it2.next():
            m = it2.get()
            if m.killed:
                it2.remove_this()
            else:
                m.update(d_sec)
                m.rect.x += m.x_vel * d_sec
                m.rect.y += m.y_vel * d_sec
                if m.collide:
                    self.ground_collide_detect(m)

    def update_viewport(self):
        p1 = self.p1
        x_rel = self.to_relx(p1.rect.x)
        if (p1.rect.x >= self.startx + self.free_range[0]) and \
            (p1.rect.right <= self.endx - self.free_range[1]):
            dx = p1.rect.x - self.pre_mario_x
            self.pre_mario_x = p1.rect.x
            
            v = self.viewport
            nvx = v.x - dx
            if (nvx >= -self.startx or nvx <= v.width - self.endx) or in_range(x_rel, self.free_range):
                self.mario_rel_rect.x = int(x_rel)
            else:
                self.viewport.x = nvx
        else:
            self.mario_rel_rect.x = int(x_rel)
        
        self.mario_rel_rect.y = int(self.to_rely(p1.rect.y))

    def killenemy_mark(self, e):
        self.mutikill_timeer = 0
        self.mutikill += 1
        mark = self.mutikill * e.killmark
        self.matter_list.push(MarkNumber(mark, e))

    def gain_mark(self, mark, m):
        self.matter_list.push(MarkNumber(mark, m))

    def to_abs_pos(self, rel_pos):
        return [rel_pos[0] - self.viewport.x, rel_pos[1] - self.viewport.y]
    def to_rel_pos(self, abs_pos):
        return [abs_pos[0] + self.viewport.x, abs_pos[1] + self.viewport.y]
    def to_abs_rect(self, rel_rect):
        return pygame.rect.Rect(
            rel_rect.x - self.viewport.x, rel_rect.y - self.viewport.y,
            rel_rect.width, rel_rect.height
        )
    def to_rel_rect(self, abs_rect):
        return pygame.rect.Rect(
            abs_rect.x + self.viewport.x, abs_rect.y + self.viewport.y,
            abs_rect.width, abs_rect.height
        )
    def to_relx(self, i):
        return i + self.viewport.x
    def to_rely(self, i):
        return i + self.viewport.y
    def to_absx(self, i):
        return i - self.viewport.x
'''----------- old-----
        ground = self.map_info['ground']
        gg = self.ground_group = pygame.sprite.Group()
        for g in ground:
            #self.ground.append(rectangle(g['x'], g['y'], g['width'], g['height']))
            s = pygame.sprite.Sprite()
            s.rect = pygame.rect.Rect(g['x'], g['y'], g['width'], g['height'])
            gg.add(s)

        pipe = self.map_info['pipe']
        pg = self.pipe_group = pygame.sprite.Group()
        for g in pipe:
            s = pygame.sprite.Sprite()
            s.rect = pygame.rect.Rect(g['x'], g['y'], g['width'], g['height'])
            pg.add(s)

        step = self.map_info['step']
        sg = self.step_group = pygame.sprite.Group()
        for g in step:
            s = pygame.sprite.Sprite()
            s.rect = pygame.rect.Rect(g['x'], g['y'], g['width'], g['height'])
            sg.add(s)

'''
'''-----------  old update---------

        dx = (self.mario.x_vel * d_ms) / 1000.
        px = self.mario_pos[0] + dx

        sx = self.maps_pos_info[self.map_index]['start_x']
        ex = self.maps_pos_info[self.map_index]['end_x']




        if px < sx or px + self.immario.rect.width > ex:
            return

        self.mario_pos[0] = px

        # 修改 viewport
        rel_px = self.viewport.x + px

        vx = self.viewport.x - dx

        if (vx > sx or vx + ex < self.viewport.width) or in_range(rel_px, self.cfg_free_range):
            self.immario.rect.x = int(rel_px)
        else:
            self.viewport.x = vx
'''
