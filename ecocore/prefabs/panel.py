from ecocore import *
from ecocore.prefabs.button import Button
from ecocore.models.procedural.quad import Quad

class Panel(Entity):

    def __init__(self, **kwargs):
        super().__init__()
        self.parent = camera.ui
        self.model = Quad()
        self.color = Button.color

        for key, value in kwargs.items():
            setattr(self, key, value)

if __name__ == '__main__':
    app = Ecocore()
    p = Panel()
    app.run()
