import pygame
import _thread
import time
from threading import Semaphore

from .tools import RWMutex


class Game:
    def __init__(self):
        self.screen = pygame.display.get_surface()

    def run(self, scene_dict, first_scene_name):
        self.scene_dict = scene_dict
        self.scene = scene_dict[first_scene_name]
        self.scene.start(None)
        self.lock_scene = RWMutex()

        self._q_threads = 0
        self._subthread_count = 2

        self.update_thread_id = _thread.start_new_thread(
            Game.update_thread, (self, ))
        self.render_thread_id = _thread.start_new_thread(
            Game.render_thread, (self, ))
        self.event_thread()

    def event_thread(self):
        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                self.__on_quit__(event)
                return
            else:
                self.scene.event_handle(event)

    def update_thread(self):
        #self.pre_time_update = time.time()
        while True:
            if self.check_quit(): return
            #time1 = time.time() delay =
            self.scene.update()
            if self.scene.is_finished():
                scene2 = self.scene_dict[self.scene.next_scene_name]
                scene2.start(self.scene)
                self.scene = scene2
                continue
            #self.pre_time_update = time1
            #dt = delay - (time.time() - time1)
            #if dt > 0: time.sleep(dt)

    def render_thread(self):
        #self.pre_time_render = time.time()
        while True:
            if self.check_quit(): return
            #time1 = time.time() delay =
            self.scene.render(self.screen)
            pygame.display.update()
            #self.pre_time_render = time1
            #dt = delay - (time.time() - time1)
            #if dt > 0: time.sleep(dt)

    lock_quit = Semaphore()

    def _tell_threads_to_quit_(self):
        with self.lock_quit:
            self._q_threads = self._subthread_count

    def _quit_theads_num_(self):
        with self.lock_quit:
            n = self._q_threads
        return n

    def _quit_this_thread_(self):
        with self.lock_quit:
            self._q_threads -= 1

    def __on_quit__(self, event):
        self._tell_threads_to_quit_()
        while self._quit_theads_num_() > 0:
            time.sleep(0.1)

    def check_quit(self):
        if self._quit_theads_num_() > 0:
            if self._quit_theads_num_() == 1:
                self.scene.quit()
            self._quit_this_thread_()
            return True
        return False
    # def get_real_update_delay(self):
    #     '''
    #         update调用周期时间可能有误差
    #         此函数返回上次update调用的时间间隔
    #     '''
    #     return time.time() - self.pre_time_update

    # def get_real_render_delay(self):
    #     '''
    #         返回与上次render调用的时间间隔
    #     '''
    #     return time.time() - self.pre_time_render
