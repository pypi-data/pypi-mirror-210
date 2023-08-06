from SEAS.Engine.Setup import *


class Input:
    def start(self):
        self.dependencies = {
            'Keys': pygame.key.get_pressed(),
        }
        self.functions = {}

    def updateBefore(self):
        self.dependencies['Keys'] = pygame.key.get_pressed()
