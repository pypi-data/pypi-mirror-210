class CoreModule:
    def __init__(self, start, updateBefore, dependencies, functions) -> None:
        self.start = start
        self.updateBefore = updateBefore
        self.dependencies = dependencies
        self.functions = functions

    def getFunction(self, name):
        return self.functions[name]

    def runFunction(self, name):
        self.functions[name]()

    def getVariable(self, name):
        self.dependencies[name]
