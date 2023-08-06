import bioumlsim

sim = bioumlsim.BioUMLSim()
model = sim.load("C:/Users/Damag/BioUML_Scripts/models_selected/BIOMD0000000003.xml")
result = model.simulate(100, 10)

result.toFile("C:/Users/Damag/result2.txt", precision=4)
print(result)
print()
print(result.getTimes())
print()
print(result.getNames())
print()
print(result.getValues())
print()
print(result.getValues('X'))
