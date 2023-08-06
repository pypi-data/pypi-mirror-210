from os import error
from SEAS.Engine.Core.core import SEAS


class HitboxPoly:
    def __init__(self, points:[]=[], moveHitbox:bool=True)-> None:
        self.inpPoints = points
        self.inpMoveHitbox = moveHitbox

    def start(self) -> None:
        self.points = self.inpPoints
        if self.points == []:
            self.points = SEAS.getScene().getComponent('TransformPoly').points

        self.moveHitbox = self.inpMoveHitbox


    def update(self) -> None:
        if self.moveHitbox:
            self.points = SEAS.getScene().getComponent('TransformPoly').points
