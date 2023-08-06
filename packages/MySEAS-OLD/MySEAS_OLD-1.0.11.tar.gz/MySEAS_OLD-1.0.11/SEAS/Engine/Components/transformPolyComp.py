from SEAS.Engine.Core.core import SEAS


class TransformPoly:
    def __init__(self, point, angle=0):
        # Make so points are relavant to other points

        # We do this because the currentObj is not updated yet. This wont do a diff here but its good practise (look at hitboxPoly)
        self.inpPoint = point
        self.inpAngle = angle

    def start(self):
        self.points = self.inpPoint
        self.angle = self.inpAngle
        
        self.isVisible = False
        for p in self.points:
            if (0 < p[0] < SEAS.getCoreModule('Screen').wW) and (0 < p[1] < SEAS.getCoreModule('Screen').wH):
                self.isVisible = True
                break

    def update(self):
        self.isVisible = False
        for p in self.points:
            if (0 < p[0] < SEAS.getCoreModule('Screen').wW) and (0 < p[1] < SEAS.getCoreModule('Screen').wH):
                self.isVisible = True
                break
