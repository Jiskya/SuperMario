import pygame.rect as rt
class Rect:
    def __init__(self, left, top, width, height):
        self.x, self.y, self.width, self.height = float(left), float(top), float(width), float(height)

    def from_image(image):
        r1 = image.get_rect()
        r = Rect(float(r1.x), float(r1.y), r1.width, r1.height)
        return r

    def to_int_rect(self):
        return rt.Rect(self.x, self.y, self.width, self.height)

    def copy(self):
        return Rect(self.x, self.y, self.width, self.height)

    def __getattribute__(self, name):
        if name == 'right':
            return self.x + self.width
        elif name == 'bottom':
            return self.y + self.height
        elif name == 'left':
            return self.x
        elif name == 'up':
            return self.y
        elif name == 'center_x':
            return (self.x + self.right) / 2
        elif name == 'center_y':
            return (self.y + self.bottom) / 2
        else:
            return super().__getattribute__(name)

    def __setattr__(self, name , value):
        if name == 'right':
            self.x = value - self.width
        elif name == 'bottom':
            self.y = value - self.height
        elif name == 'left':
            self.x = value
        elif name == 'up':
            self.y = value
        elif name == 'center_x':
            self.x = 2 * value - self.right
        elif name == 'center_y':
            self.y = 2 * value - self.bottom
        else:
            super().__setattr__(name, value)

    def __str__(self):
        return '({},{},{},{})'.format(self.x, self.y, self.width, self.height)

    def __repr__(self):
        return 'Rect' + self.__str__()