from typing import Any
from SEAS.Engine.Setup import *


class Font:
    def start(self):
        self.dependencies = {
                'Fonts': {}
        }
        self.functions = {
            'createFont': self.createFont,
            'getFont': self.getFont,
        }

    def updateBefore(self): pass
    def update(self): pass

    def createFont(self, fontName:str, fontType:str='freesansbold.ttf', fontSize:int=20) -> None:
        self.dependencies['Fonts'][fontName] = pygame.font.Font(fontType, fontSize)
        return self.dependencies['Fonts'][fontName]

    def getFont(self, fontName:str) -> Any:
        return self.dependencies['Fonts'][fontName]
