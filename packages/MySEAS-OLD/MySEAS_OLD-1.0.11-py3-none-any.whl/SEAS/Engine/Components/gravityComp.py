from SEAS.Engine.Core import *

class GravityComp:
    def start(self):
        self.velocity = -100
        self.isGround = False


    def update(self):
        transformComp = SEAS.getScene().getComponent('TransformRect')

        # Increasing the increase (accelerating)
        if self.isGround == False:
            self.velocity += 9.8
        else:
            self.velocity = 0

        
        transformComp.yLT += self.velocity * KEL.deltaTime # Deltatime provides us a frame independent game
