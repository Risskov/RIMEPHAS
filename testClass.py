

class TestClass():
    def __init__(self, obj):
        self.obj = obj
        
    def printout(self):
        print(self.obj.numberOfActivations)
        
    def setActivations(self, number):
        self.obj.numberOfActivations = number
        self.printout()