from SEAS.Engine.Setup import *
from SEAS.Engine.Core import *


class RenderPoly:
    def start(self):
        self.transformComp = SEAS.getScene().getComponent('TransformPoly')

    def update(self):
        if self.transformComp.isVisible:
            objectColor = SEAS.getMaterial()
            points = self.transformComp.points
            pygame.draw.polygon(SEAS.coreModules['Screen'].wn, objectColor, points)
