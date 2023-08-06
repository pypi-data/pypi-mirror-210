import jpype
import jpype.imports
import numpy
import os

class BioUMLSim:
    
    bioUMLPath = None
    atol = 1E-8
    rtol = 1E-8
    engine = None

    def __init__(self, path = 'C:/lib'):
        self.bioUMLPath = path
        print("JVM is starting up")
        jpype.startJVM(classpath=[path+'/*'], convertStrings=True)
        path = os.path.abspath(__file__)
        print(path)
        
    def load(self, file):
        """
        Loads SBML file and transforms it into object which represents mathematical model.
        Args:
            file (str): path to file
        Returns:
            model
        """
        print(f"SBML file is loading: {file}.")
        diagram = jpype.JClass("biouml.plugins.sbml.SbmlModelFactory").readDiagram(file, False)
        self.engine = jpype.JClass("biouml.plugins.simulation.java.JavaSimulationEngine")()
        self.engine.setDiagram(diagram)
        self.engine.setClassPath(self.bioUMLPath +'/src.jar')
        self.engine.disableLog()
        self.engine.setAbsTolerance(self.atol)
        self.engine.setRelTolerance(self.rtol)
        return Model(self.engine, self.engine.createModel())
    
class Model:
    
    def __init__(self, engine, model):
        self.engine = engine
        self.model = model
        
    def simulate(self, tend, numpoints):
        """
        Simulates SBML model and returns results.
        Args:
            tend: final time for simulation
            numpoints: number of time points
        Returns:
            simulation results
        """
        print(f"Simulating model: {self.engine.getDiagram().getName()}.")
        self.engine.setCompletionTime(tend)
        self.engine.setTimeIncrement(tend / numpoints)
        return Result(self.engine.simulateSimple(self.model), self.engine) 
    
class Result:
    
    def __init__(self, sr, engine):
        self.sr = sr
        self.engine = engine
        species = engine.getFloatingSpecies()
        self.values = numpy.array(sr.getValuesTransposed(species))
        self.names = numpy.array(species)
        self.times = numpy.array(sr.getTimes());
        
    def toFile(self, file, precision=3, separator ='\t'):
        f = open(file, 'w')
        f.write(numpy.array2string(self.names, separator=separator)[1:-1])
        f.write('\n')
        for row in self.values:
            f.write(numpy.array2string(row, precision=precision, separator=separator)[1:-1])
            f.write('\n')
        f.close()
    
    def __str__(self):
        return str(self.values)
    
    def getTimes(self):
        return self.times
    
    def getNames(self):
        return self.names
        
    def getValues(self, variable=None):
        if (variable!=None):
            return numpy.array(self.sr.getValues(variable))
        else:
            return self.values