from SEAS.Engine.Core import *
from SEAS.Engine.Setup import *

import math


class CharacterPolyController:
    def start(self): 
        self.trns = SEAS.getScene().getComponent('TransformPoly')
        self.hitb = SEAS.getScene().getComponent('HitboxPoly')
        
    def update(self): 
        pass

    def move(self, vel, angle='default'):
        if angle == 'default':
            nAngle = self.trns.angle
        else:
            nAngle = angle

        mX = math.cos(math.radians(nAngle)) * vel
        mY = math.sin(math.radians(nAngle)) * vel

        self.moveX(mX)
        self.moveY(mY)

    # make so that points move in the future
    def rawRotate(self, points, angle, angleChange, _axis='centroid'):
        if angleChange == 0: return [points, angle]
        angle += angleChange

        if _axis == 'centroid': axis = self.__axis(points)
        else: axis = _axis

        newPoints = []
        for p in points: newPoints.append(self.rotatePoint(axis[0], axis[1], angleChange, p))
        for p, i in zip(newPoints, range(len(points))): points[i] = p

        return [points, angle]
        
    def rotate(self, angle, _axis='centroid'):
        if angle == 0: return None
        self.trns.angle += angle

        if _axis == 'centroid': axis = self.__axis(self.trns.points)
        else: axis = _axis

        newPoints = []
        for p in self.trns.points: newPoints.append(self.rotatePoint(axis[0], axis[1], angle, p))
        for p, i in zip(newPoints, range(len(self.trns.points))): self.trns.points[i] = p

    def __sin(self, angle): return (math.sin(math.radians(angle)))
    def __cos(self, angle): return (math.cos(math.radians(angle)))

    def rotatePoint(self, cx, cy, angle, p):
        return [self.__cos(angle) * (p[0] - cx) - self.__sin(angle) * (p[1] - cy) + cx,
                  self.__sin(angle) * (p[0] - cx) + self.__cos(angle) * (p[1] - cy) + cy]

    def __axis(self, points):
        xPoints = []
        for p in points:
            xPoints.append(p[0])
        yPoints = []
        for p in points:
            yPoints.append(p[1])
        cX = sum(xPoints)/len(xPoints)
        cY = sum(yPoints)/len(yPoints)
        axis = [cX, cY]
        return axis
    
    def drawDirection(self):
        len = 50
        lenK1 = math.cos(math.radians(self.trns.angle))*len
        lenK2 = math.sin(math.radians(self.trns.angle))*len

        
        pygame.draw.line(SEAS.coreModules['Screen'].wn,
                (0, 255, 0), 
                (self.trns.points[0][0], self.trns.points[0][1]), 
                (lenK1+self.trns.points[0][0], lenK2+self.trns.points[0][1]) )

    def moveX(self, vel):
        for point in self.trns.points:
            point[0] += vel

    def moveY(self, vel):
        for point in self.trns.points:
            point[1] += vel
