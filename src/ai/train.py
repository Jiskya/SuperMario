import pygame
from src import constants as c

import _thread
import time, random
AI_TURNUP = False


sleep_time_1 = 0.28641353934834535
sleep_time_2 = 0.02
jump_epoach = 0.4170129497387854 #4270129497387854
to_end = False
#successed = False



class Train:

    def run():
        global to_end
        if not AI_TURNUP: return

        to_end = False
        _thread.start_new_thread(Train.ai_run)

    def end():
        global to_end
        if not AI_TURNUP: return

        to_end = True

    def success():
        global sleep_time_1, sleep_time_2, successed, jump_epoach
        if not AI_TURNUP: return

        #successed = True

        print('\nsuccess !!!')
        print('sleep_time_1 ', sleep_time_1)
        print('sleep_time_2 ', sleep_time_2)
        print('jump_epoach ', jump_epoach)

    def ai_run():
        global to_end, sleep_time_1, sleep_time_2, successed

        Train.i += 1
        i = Train.i
        run_timer = 0
        print('thread', i)

        # if not successed:
        #     t1 = random.random() / 2
        #     t2 = random.random() / 2
        #     sleep_time_1 = max(t1, t2) + 0.14
        #     sleep_time_2 = max(0.02, min(t1, t2) - 0.14)
        #     jump_epoach = random.random() + 0.2
        #     print(sleep_time_1, sleep_time_2, jump_epoach, '\n')

        jump_time = time.time()
        while True:
            if to_end: return

            run_timer += 1

            if run_timer == 2:
                e = pygame.event.Event(pygame.KEYDOWN, key=c.K_RUN[0], unicode=u'')
                pygame.event.post(e)
            elif run_timer == 8:
                run_timer = 0
                e = pygame.event.Event(pygame.KEYUP, key=c.K_RUN[0], unicode=u'')
                pygame.event.post(e)


            e = pygame.event.Event(pygame.KEYDOWN, key=c.K_RIGHT[0], unicode=u'')
            pygame.event.post(e)

            time.sleep(sleep_time_1)

            tm = time.time()
            if (tm - jump_time) > jump_epoach:
                jump_time = tm
                e = pygame.event.Event(pygame.KEYUP, key=c.K_RIGHT[0], unicode=u'')
                pygame.event.post(e)



            e = pygame.event.Event(pygame.KEYDOWN, key=c.K_UP[0], unicode=u'')
            pygame.event.post(e)
            e = pygame.event.Event(pygame.KEYDOWN, key=c.K_LEFT[0], unicode=u'')
            pygame.event.post(e)

            time.sleep(sleep_time_2)

            e = pygame.event.Event(pygame.KEYUP, key=c.K_LEFT[0], unicode=u'')
            pygame.event.post(e)

Train.i = 0