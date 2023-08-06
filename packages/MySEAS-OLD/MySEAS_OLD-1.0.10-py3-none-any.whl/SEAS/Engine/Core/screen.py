from SEAS.Engine.Setup import *


class Screen:
    def start(self):
        # 160 	× 	120
        self.dependencies = {
            'wW': 1000,
            'wH': 1000,
            'wn': pygame.display.set_mode((self.dependencies['wW'], self.dependencies['wH'])),
            'clock': pygame.time.Clock(),
            'frameLimit': 60,
            'frameRate': self.dependencies['clock'].get_fps(),
            'color': "#ffffff",
        }
        self.functions = {
            'setColor': self.setColor
        }

    def updateBefore(self): # Before updating objects
        self.dependencies['wn'].fill(self.dependencies['color'])

        # Clock
        self.dependencies['clock'].tick(self.dependencies['frameLimit'])
        self.dependencies['frameRate'] = self.dependencies['clock'].get_fps()

    def setColor(self, clr):
        self.dependencies['color'] = clr
