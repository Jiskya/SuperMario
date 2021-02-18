from abc import ABCMeta, abstractmethod
from . import bitt
from .rect import Rect


class Layout(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, selfrect):
        if selfrect is None:
            self.rect = Rect(0, 0, 1, 1)
        else:
            self.rect = selfrect

    @abstractmethod
    def push(self, rect):
        pass


class ModeError(Exception):
    def __init__(self, mode):
        self.mode = mode

    def __str__(self):
        return '不支持的格式:{}'.format(self.mode)


class LineLayout(Layout):
    def __init__(self, selfrect, spacing=0, margin=(0, 0)):
        super().__init__(selfrect)
        self.expanded_rect = self.rect.copy()
        self.spacing = spacing
        self.marginX = margin[0]
        self.marginY = margin[1]

    def expand(self, x=0, y=0):
        self.rect.x = x
        self.rect.y = y
        self.rect.width = self.expanded_rect.width
        self.rect.height = self.expanded_rect.height
        
        self.update()
    
    def push(self, rect):
        pass

    def next_spacing(self, spaceing):
        pass

    def push_space(self, spaceing):
        self.next_spacing(spaceing + self.spacing)

    def update(self):
        pass

    def set_spacing(self, sz):
        self.spacing = sz

    def set_marginX(self, sz):
        self.marginX = sz

    def set_marginY(self, sz):
        self.marginY = sz

    class C:
        def setup():
            C = LineLayout.C
            bt = bitt.BitTool()
            C.ALIGN_BITS,   C.ALIGN_CARRY, C.ALIGN_MASK =  \
                bt.bits_carry_mask(3)
            C.TYPESET_BITS, C.TYPESET_CARRY, C.TYPESET_MASK =  \
                bt.bits_carry_mask(2)

            C.ORIENT_BITS, C.ORIENT_CARRY, C.ORIENT_MASK =  \
                bt.bits_carry_mask(2)

            (C.ALIGN_CENTER, C.ALIGN_LEFT, C.ALIGN_RIGHT, C.ALIGN_UP,
             C.ALIGN_DOWN) = bitt.make(C.ALIGN_CARRY, 5)
            (C.TYPESET_PILE, C.TYPESET_CENTER) \
                = bitt.make(C.TYPESET_CARRY, 2)
            (C.ORIENT_LEFT, C.ORIENT_RIGHT, C.ORIENT_UP,
             C.ORIENT_DOWN) = bitt.make(C.ORIENT_CARRY, 4)


LineLayout.C.setup()





class VLineLayout(LineLayout):
    def __init__(self,self_rect = None,
        mode=LineLayout.C.ALIGN_CENTER| \
        LineLayout.C.TYPESET_PILE|    \
        LineLayout.C.ORIENT_DOWN, spacing=0, margin=(0, 0)):
        super().__init__(self_rect, spacing, margin)
        self.mode = mode
        self.rects = []
        self.h_all = 0

    def push(self, rect):
        C = VLineLayout.C
        if (self.mode & C.TYPESET_MASK) == C.TYPESET_PILE:
            self.__typeset_pile__(rect)
        elif (self.mode & C.TYPESET_MASK) == C.TYPESET_CENTER:
            self.rects.append(rect)
            if self.h_all == 0:
                self.h_all = rect.height
            else:
                self.h_all += rect.height + self.spacing
            self.__typeset_center__()
        else:
            raise ModeError(self.mode)
        self.__align__(rect)

    def next_spacing(self, spaceing):
        self.push(Rect(0, 0, 0, spaceing - 2 * self.spacing))

    def update(self):
        if len(self.rects) == 0: return
        C = VLineLayout.C
        if (self.mode & C.TYPESET_MASK) == C.TYPESET_PILE:
            self.__typeset_pile_all__()
        elif (self.mode & C.TYPESET_MASK) == C.TYPESET_CENTER:
            self.h_all = self.rects[0].height
            for i in range(1, len(self.rects)):
                self.h_all += self.rects[i].height + self.spacing
            self.__typeset_center__()
        else:
            raise ModeError(self.mode)
        self.__align_all__()

    def __align__(self, rect):
        C = VLineLayout.C

        wwww = rect.width + 2 * self.marginX
        if (self.mode & C.ALIGN_MASK) == C.ALIGN_CENTER:
            rect.x = self.rect.x + (self.rect.width - rect.width) / 2
            if self.expanded_rect.width < wwww:
                w0 = (wwww - self.expanded_rect.width) / 2
                self.expanded_rect.width = wwww
                self.expanded_rect.x -= w0

        elif (self.mode & C.ALIGN_MASK) == C.ALIGN_LEFT:
            rect.x = self.rect.x + self.marginX
            self.expanded_rect.width = max(self.expanded_rect.width, wwww)

        elif (self.mode & C.ALIGN_MASK) == C.ALIGN_RIGHT:
            rect.x = self.rect.x + self.rect.width - \
                self.marginX - rect.width
            if self.expanded_rect.width < wwww:
                w0 = (wwww - self.expanded_rect.width)
                self.expanded_rect.width = wwww
                self.expanded_rect.x -= w0
        else:
            raise ModeError(self.mode)

    def __align_all__(self):
        C = VLineLayout.C

        if (self.mode & C.ALIGN_MASK) == C.ALIGN_CENTER:
            for i in range(len(self.rects)):
                rect = self.rects[i]
                w = (self.rect.width - rect.width) / 2
                self.rects[i].x = self.rect.x + w

                wwww = rect.width + 2 * self.marginX
                if self.expanded_rect.width < wwww:
                    w0 = (wwww - self.expanded_rect.width) / 2
                    self.expanded_rect.width = wwww
                    self.expanded_rect.x -= w0

        elif (self.mode & C.ALIGN_MASK) == C.ALIGN_LEFT:
            for i in range(len(self.rects)):
                self.rects[i].x = self.rect.x + self.marginX

                wwww = self.rects[i].width + 2 * self.marginX
                self.expanded_rect.width = max(self.expanded_rect.width, wwww)

        elif (self.mode & C.ALIGN_MASK) == C.ALIGN_RIGHT:
            for i in range(len(self.rects)):
                rect = self.rects[i]
                rect.x = self.rect.x + self.rect.width - \
                    self.marginX - rect.width

                wwww = rect.width + 2 * self.marginX
                if self.expanded_rect.width < wwww:
                    w0 = (wwww - self.expanded_rect.width)
                    self.expanded_rect.width = wwww
                    self.expanded_rect.x -= w0

        else:
            raise ModeError(self.mode)

    def __typeset_pile__(self, rect):

        is_orient_up = ((self.mode & VLineLayout.C.ORIENT_MASK) \
            == VLineLayout.C.ORIENT_UP)

        if is_orient_up:
            if len(self.rects) == 0:
                rect.y = self.rect.y + self.rect.height \
                    - self.marginY - rect.height
            else:
                rect.y = self._last_rect.y - rect.height \
                    - self.spacing
            hhhh = rect.y - self.marginY
            if self.expanded_rect.y < hhhh:
                xxxx = hhhh - self.expanded_rect.y
                self.expanded_rect.y -= xxxx
                self.expanded_rect.height += xxxx
        else:
            if len(self.rects) == 0:
                rect.y = self.rect.y + self.marginY
            else:
                rect.y = self._last_rect.y + \
                    self._last_rect.height + self.spacing
            self.expanded_rect.height = max(self.expanded_rect.height,\
                rect.y + rect.height + self.marginY - \
                    self.expanded_rect.y)
        self._last_rect = rect
        self.rects.append(rect)

    def __typeset_pile_all__(self):
        n = len(self.rects)
        if (n == 0): return
        is_orient_up = ((self.mode & VLineLayout.C.ORIENT_MASK) \
            == VLineLayout.C.ORIENT_UP)
        if is_orient_up:
            self.rects[0].y = self.rect.y + self.rect.height \
                - self.marginY - self.rects[0].height
            for i in range(1, len(self.rects)):
                self.rects[i].y = self.rects[i-1].y \
                    - self.rects[i].height \
                    - self.spacing
            hhhh = self.rects[n - 1].y - self.marginY
            if self.expanded_rect.y < hhhh:
                xxxx = hhhh - self.expanded_rect.y
                self.expanded_rect.y -= xxxx
                self.expanded_rect.height += xxxx
        else:
            self.rects[0].y = self.rect.y + self.marginY
            for i in range(1, len(self.rects)):
                self.rects[i].y = self.rects[i-1].y + \
                    self.rects[i-1].height + \
                    self.spacing

            self.expanded_rect.height = max(self.expanded_rect.height,\
                self.rects[n-1].y + self.rects[n-1].height + self.marginY - \
                    self.expanded_rect.y)

    def __typeset_center__(self):
        count = len(self.rects)
        h1 = (self.rect.height - self.h_all) / 2
        y1 = self.rect.y + h1

        is_orient_up = ((self.mode & VLineLayout.C.ORIENT_MASK) \
            == VLineLayout.C.ORIENT_UP)
        for i in range(count):
            if is_orient_up: i = count - 1 - i
            self.rects[i].y = y1
            y1 += self.rects[i].height + self.spacing
        h__all2 = self.h_all + 2 * self.marginY
        if self.expanded_rect.height < h__all2:
            h0 = (h__all2 - self.expanded_rect.height) / 2
            self.expanded_rect.height = h__all2
            self.expanded_rect.y -= h0


class HLineLayout(LineLayout):
    def __init__(self,self_rect = None,
        mode=LineLayout.C.ALIGN_CENTER| \
        LineLayout.C.TYPESET_PILE|    \
        LineLayout.C.ORIENT_RIGHT, spacing=0, margin=(0, 0)):
        super().__init__(self_rect, spacing, margin)
        self.mode = mode
        self.rects = []
        self.w_all = 0

    def push(self, rect):
        C = HLineLayout.C
        if (self.mode & C.TYPESET_MASK) == C.TYPESET_PILE:
            self.__typeset_pile__(rect)
        elif (self.mode & C.TYPESET_MASK) == C.TYPESET_CENTER:
            self.rects.append(rect)
            if self.w_all == 0:
                self.w_all = rect.width
            else:
                self.w_all += rect.width + self.spacing
            self.__typeset_center__()
        else:
            raise ModeError(self.mode)
        self.__align__(rect)

    def update(self):
        if len(self.rects) == 0: return
        C = VLineLayout.C
        if (self.mode & C.TYPESET_MASK) == C.TYPESET_PILE:
            self.__typeset_pile_all__()
        elif (self.mode & C.TYPESET_MASK) == C.TYPESET_CENTER:
            self.w_all = self.rects[0].width
            for i in range(1, len(self.rects)):
                self.w_all += self.rects[i].width + self.spacing
            self.__typeset_center__()
        else:
            raise ModeError(self.mode)
        self.__align_all__()

    def next_spacing(self, spaceing):
        self.push(Rect(0, 0, spaceing - 2 * self.spacing, 0))

    def __align__(self, rect):
        C = HLineLayout.C

        hhhh = rect.height + 2 * self.marginY
        if (self.mode & C.ALIGN_MASK) == C.ALIGN_CENTER:
            rect.y = self.rect.y + (self.rect.height - rect.height) / 2
            if self.expanded_rect.height < hhhh:
                h0 = (hhhh - self.expanded_rect.height) / 2
                self.expanded_rect.height = hhhh
                self.expanded_rect.y -= h0

        elif (self.mode & C.ALIGN_MASK) == C.ALIGN_UP:
            rect.y = self.rect.y + self.marginY
            self.expanded_rect.height = max(self.expanded_rect.height, hhhh)

        elif (self.mode & C.ALIGN_MASK) == C.ALIGN_DOWN:
            rect.y = self.rect.y + self.rect.height - \
            self.marginY - rect.height
            if self.expanded_rect.height < hhhh:
                h0 = (hhhh - self.expanded_rect.height)
                self.expanded_rect.height = hhhh
                self.expanded_rect.y -= h0
        else:
            raise ModeError(self.mode)

    def __align_all__(self):
        C = HLineLayout.C
        #maxh_rect
        if (self.mode & C.ALIGN_MASK) == C.ALIGN_CENTER:
            for i in range(len(self.rects)):
                rect = self.rects[i]
                h = (self.rect.height - rect.height) / 2
                rect.y = self.rect.y + h

                hhhh = rect.height + 2 * self.marginY
                if self.expanded_rect.height < hhhh:
                    h0 = (hhhh - self.expanded_rect.height) / 2
                    self.expanded_rect.height = hhhh
                    self.expanded_rect.y -= h0

        elif (self.mode & C.ALIGN_MASK) == C.ALIGN_UP:
            for i in range(len(self.rects)):
                self.rects[i].y = self.rect.y + self.marginY

                hhhh = self.rects[i].height + 2 * self.marginY
                self.expanded_rect.height = max(self.expanded_rect.height,
                                                hhhh)

        elif (self.mode & C.ALIGN_MASK) == C.ALIGN_DOWN:
            for i in range(len(self.rects)):
                rect = self.rects[i]
                rect.y = self.rect.y + self.rect.height - \
                self.marginY - rect.height

                hhhh = rect.height + 2 * self.marginY
                if self.expanded_rect.height < hhhh:
                    h0 = (hhhh - self.expanded_rect.height)
                    self.expanded_rect.height = hhhh
                    self.expanded_rect.y -= h0

        else:
            raise ModeError(self.mode)

    def __typeset_pile__(self, rect):

        is_orient_left = ((self.mode & HLineLayout.C.ORIENT_MASK) == \
            HLineLayout.C.ORIENT_LEFT)

        if is_orient_left:
            if len(self.rects) == 0:
                rect.x = self.rect.x + self.rect.width \
                    - self.marginX - rect.width
            else:
                rect.x = self._last_rect.x - rect.width \
                    - self.spacing
            wwww = rect.x - self.marginX
            if self.expanded_rect.x < wwww:
                xxxx = wwww - self.expanded_rect.x
                self.expanded_rect.x -= xxxx
                self.expanded_rect.width += xxxx
        else:
            if len(self.rects) == 0:
                rect.x = self.rect.x + self.marginX
            else:
                rect.x = self._last_rect.x + \
                    self._last_rect.width + self.spacing
            self.expanded_rect.width = max(self.expanded_rect.width,\
                rect.x + rect.width + self.marginX - \
                    self.expanded_rect.x)
        self._last_rect = rect
        self.rects.append(rect)

    def __typeset_pile_all__(self):
        n = len(self.rects)
        if (n == 0): return
        is_orient_left = ((self.mode & HLineLayout.C.ORIENT_MASK) == \
            HLineLayout.C.ORIENT_LEFT)
        if is_orient_left:
            self.rects[0].x = self.rect.x + self.rect.width \
                - self.marginX - self.rects[0].width
            for i in range(1, len(self.rects)):
                self.rects[i].x = self.rects[i-1].x \
                    - self.rects[i].width \
                    - self.spacing
            wwww = self.rects[n - 1].x - self.marginX
            if self.expanded_rect.x < wwww:
                xxxx = wwww - self.expanded_rect.x
                self.expanded_rect.x -= xxxx
                self.expanded_rect.width += xxxx
        else:
            self.rects[0].x = self.rect.x + self.marginX
            for i in range(1, len(self.rects)):
                self.rects[i].x = self.rects[i - 1].x + \
                    self.rects[i - 1].width + \
                    self.spacing
            self.expanded_rect.width = max(self.expanded_rect.width,\
                self.rects[n-1].x + self.rects[n-1].width + self.marginX - \
                    self.expanded_rect.x)


    def __typeset_center__(self):
        count = len(self.rects)
        w1 = (self.rect.width - self.w_all) / 2
        x1 = self.rect.x + w1

        is_orient_left = ((self.mode & HLineLayout.C.ORIENT_MASK) \
            == HLineLayout.C.ORIENT_LEFT)
        for i in range(count):
            if is_orient_left: i = count - 1 - i
            self.rects[i].x = x1
            x1 += self.rects[i].width + self.spacing
        w__all2 = self.w_all + 2 * self.marginX
        if self.expanded_rect.width < w__all2:
            w0 = (w__all2 - self.expanded_rect.width) / 2
            self.expanded_rect.width = w__all2
            self.expanded_rect.x -= w0


# if __name__ == '__main__':
#     layout = HLineLayout(
#         Rect(0, 0, 10, 10),
#         HLineLayout.C.ORIENT_LEFT | HLineLayout.C.TYPESET_CENTER)
#     r1 = Rect(0, 0, 2, 2)
#     layout.push(r1)
#     print('layout.expanded_rect', layout.expanded_rect)
#     print(r1, '\n')

#     r2 = Rect(0, 0, 12, 12)
#     layout.push(r2)
#     r2.height += 10
#     layout.update()
#     print('layout.expanded_rect', layout.expanded_rect)
#     print(r1)
#     print(r2, '\n')

#     r3 = Rect(0, 0, 2, 2)
#     layout.push(r3)
#     print('layout.expanded_rect', layout.expanded_rect)
#     print(r1)
#     print(r2)
#     print(r3, '\n')

#     print('--------------------------------------')

#     layout = VLineLayout(
#         Rect(0, 0, 10, 10),
#         HLineLayout.C.ORIENT_UP | HLineLayout.C.TYPESET_CENTER)
#     r1 = Rect(0, 0, 2, 2)
#     layout.push(r1)
#     print('layout.expanded_rect', layout.expanded_rect)
#     print(r1, '\n')

#     r2 = Rect(0, 0, 2, 2)
#     layout.push(r2)

#     layout.update()

#     print('layout.expanded_rect', layout.expanded_rect)
#     print(r1)
#     print(r2, '\n')

#     r3 = Rect(0, 0, 2, 2)
#     layout.push(r3)
#     print('layout.expanded_rect', layout.expanded_rect)
#     print(r1)
#     print(r2)
#     print(r3, '\n')
