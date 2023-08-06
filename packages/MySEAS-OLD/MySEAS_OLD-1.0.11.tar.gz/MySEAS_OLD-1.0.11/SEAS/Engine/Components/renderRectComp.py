from SEAS.Engine.Setup import *
from SEAS.Engine.Core import *


class RenderRect:
    def start(self):
        self.transformComp = SEAS.getScene().getComponent('TransformRect')

    def update(self):
        if self.transformComp.isVisible:
            self.objectColor = SEAS.getMaterial()
            lX, lY, w, h = self.transformComp.xLT, self.transformComp.yLT, self.transformComp.width, self.transformComp.height
            pygame.draw.rect(SEAS.coreModules['Screen'].wn, self.objectColor, pygame.Rect((lX, lY), (w, h)))
