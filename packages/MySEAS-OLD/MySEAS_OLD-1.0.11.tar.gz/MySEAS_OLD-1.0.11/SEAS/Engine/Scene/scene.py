from SEAS.Engine.Setup import *
from SEAS.Engine.Core.event import *
from SEAS.Engine.Core.screen import *
from SEAS.Engine.Models import *

from typing import Any

import time

class Scene:
    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def __init__(self, frameLimit, wn):
        self.clock = pygame.time.Clock()
        self.frameLimit = frameLimit
        self.framerate = 0
        self.objects = {}
        self.running = False
        self.texts = {}
        self.wn = wn

    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def startObjects(self):
        for component in self.objects:
            self.currentObj = self.objects[component]
            self.objects[component].start()


    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def updateScene(self):
        self.running = True

        # Updating objects, thats really just updating the blueparint that then updates the components of the object
        try:
            for object in self.objects:
                if self.objects != {}:
                    self.currentObj = self.objects[object]
                    self.objects[object].update() 
            
            for text in self.texts:
                if self.texts != {}:
                    t = self.texts[text]
                    if t[1]:
                        self.wn.blit(t[0], t[2])

        except RuntimeError:
            # This just basicly means that if a object was created in the dic we are gonna start OVEERERRERERERERER
            pass

        self.clock.tick(self.frameLimit)


    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def addObject(self, objectName:str="emptyModel", hitbox:bool=True, objectModel:Any=EmptyModel, components:list=[], objectLocation:str='objects') -> None: # Dont use objLocation, hitbox will later be hitbox groups and i t will be in the transform group
        # First get the location by getting the of my self
        location = getattr(self, objectLocation)

        # Then adding it to the attribute
        i = 0
        run = True
        while run:
            i += 1
            if objectName not in self.objects:
                updatedObjectName = objectName
                run = False

            elif objectName + str(i) not in self.objects:
                updatedObjectName = objectName + str(i)
                run = False

        location[updatedObjectName] = objectModel()

        self.currentObj = self.objects[updatedObjectName]

        # Then adding the components we might want to add when we create the object
        self.objects[updatedObjectName].addComponent(components, self.running)


        # Adding a default white material
        self.objects[updatedObjectName].material = "#ffffff"

    def addText(self, font:Any, textName:str, text:str="Your forgor to put a text on the function (addText)", antialias:bool=True, color:str="#000000", backgroundColor:str=None, render:bool=True, position:Any=[0, 0], typePosition:str='center'):
        self.texts[textName] = [font.render(text, antialias, color, backgroundColor), render, None] # None i schanged on the second line
        self.texts[textName][2] = self.texts[textName][0].get_rect() # Make text surface
        if typePosition == 'center':
            self.texts[textName][2].center = position
        else:
            print("other positions not supported yet")

    def updateText(self, font:Any, textName:str, text:str, antialias:bool=True, color:str="#ffffff", backgroundColor=None):
        self.texts[textName][0] = font.render(
                                text,
                                antialias,
                                color,
                                backgroundColor)
        return self.texts[textName]

    def removeObject(self) -> None:
        for key, value in self.objects.items():
            if value == self.currentObj:
                del self.objects[key]

    def removeAllObject(self) -> None:
        self.objects = {}

    def removeRawNameObject(self, objectName) -> None:
        del self.objects[objectName]

    def removeRawInitObject(self, objectInit) -> None:
        for value, key in self.objects.items():
            if key == objectInit:
                del self.objects[value]

    def removeAllText(self) -> None:
        self.texts = {}

    def removeText(self, textName) -> None:
        del self.texts[textName]

    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def getComponent(self, attribute=''):
        # If nothing is specified return the object u r using
        if attribute == '':
            return self.currentObj
        

        # If it doesnt have the attribute just return the AttributeError 
        try:
            returnValue = self.currentObj.components[attribute]

            return returnValue  

        except AttributeError as err:
            raise err

    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def getRawComponent(self, object:str, attribute:str=''):
        # So were basicly doing getAttribute function but we specify the object and do not use the currentObj
        if attribute == '':
            return self.objects[object]
        try:
            returnValue = self.objects[object].components[attribute]

            return returnValue

        except AttributeError as err:
            raise err


    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def getObject(self):
        return self.currentObj

    def getRawObject(self, object:str):
        return self.objects[object]
    
    def getAllObject(self): # Will not return the obejct your calling from
        returnValue = []
        for obj in self.objects:
            if self.objects[obj] != self.currentObj:
                returnValue.append(self.objects[obj])

        return returnValue
    
    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def getAttribute(self, attribute):
        # Get the requested attribute of the current object

        try:
            returnValue = getattr(self.currentObj, attribute)
            return returnValue
        
        except AttributeError as err:
            raise err


    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def getRawAttribute(self, object, attribute):
        # Get the requested attribute of the object requested

        try:
            returnValue = getattr(self.objects[object], attribute)
            return returnValue

        except AttributeError as err:
            raise err

    def getObjectName(self):
        return list(self.objects.keys())[list(self.objects.values()).index(self.currentObj)]

    def getRawObjectName(self, name):
        return list(self.objects.keys())[list(self.objects.values()).index(name)]
