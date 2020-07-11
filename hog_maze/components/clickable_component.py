from hog_maze.components.component import HogMazeComponent


class ClickableComponent(HogMazeComponent):

    def __init__(self, shape, callback, **kwargs):
        super(ClickableComponent, self).__init__('CLICKABLE')
        self.shape = shape
        self.callback = callback
        self.kwargs = kwargs
        self.mouseover = False
        self.pressed = False

    def update(self, **kwargs):
        if self.owner.component_dict['ANIMATION']:
            self.owner.component_dict['ANIMATION'].is_animating = False
        mousex = kwargs['mousex']
        mousey = kwargs['mousey']
        event_type = kwargs['event_type']
        if self.shape == "rectangle":
            cond = lambda x, y: self.owner.rect.collidepoint(x, y)
        elif self.shape == "circle":
            cond = lambda x, y: ((x - self.owner.rect.centerx)**2 +
                                  (y - self.owner.rect.centery)**2)\
                    <= (self.owner.width/2)**2
        if cond(mousex, mousey):
            if not self.mouseover:
                if self.owner.component_dict['ANIMATION']:
                    self.owner.component_dict['ANIMATION'].is_animating = True
            self.mouseover = True
        else:
            if self.mouseover:
                if self.owner.component_dict['ANIMATION']:
                    self.owner.component_dict['ANIMATION'].is_animating = True
            self.mouseover = False
        if event_type == "MOUSEBUTTONUP":
            self.pressed = True
        else:
            self.pressed = False
        if self.mouseover and self.pressed:
            self.callback(**self.kwargs)
