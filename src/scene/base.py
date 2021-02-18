from .. import constants as c

#defaul_update_delay = 1. / c.DefaultUpdateFrameRate
#defaul_render_delay = 1. / c.DefaultRenderFrameRate


class Scene:

    def __init__(self, name):
        self.name = name
        self._shift_msg_ = {}

    def start(self, pre_scene):
        '''
            从 pre_scene 转来，由Game类调用
        '''
        self._finished = False

    def finish(self, next_scene_name):
        self._finished = True
        self.next_scene_name = next_scene_name

    def quit(self):
        pass

    def event_handle(self, event):
        pass

    def update(self):
        pass

    def render(self, screen):
        pass

    def is_finished(self):
        return self._finished

    def get_shift_msg(self):
        return self._shift_msg_


'''

class __Scene:
    
    def __init__(self, name):
        super().__init__(name)

    def start(self, pre_scene):
        super().start(pre_scene)

    def event_handle(self, event):
        pass

    def update(self):
        pass

    def render(self, screen):
        pass


'''