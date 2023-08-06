from SEAS.Engine.Core import *


def run():
    SEAS.startCoreObjects()

    run = True
    while run:
        SEAS.updateCore()

        if SEAS.event('type', 'QUIT'):
            run = False



# Start engine when importing
SEAS.startCoreModules()


if __name__ == "__main__":
    run()
