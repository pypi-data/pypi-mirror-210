import pandas as pd

def testingHombre(numberNames=1):

    name = pd.read_csv("hombres.csv")
    if numberNames >= 2:
        result_array = []
        for i in range(numberNames):
            temporal_return = name.sample()["nombre"].to_string(index=False).strip()
            result_array.append(temporal_return)
        return result_array
    else:
        result_string = name.sample()["nombre"].to_string(index=False).strip()
        return result_string

print(testingHombre(100))

def testingmujer(numberNames=1):

    name = pd.read_csv("mujeres.csv")
    if numberNames >= 2:
        result_array = []
        for i in range(numberNames):
            temporal_return = name.sample()["nombre"].to_string(index=False).strip()
            result_array.append(temporal_return)
        return result_array
    else:
        result_string = name.sample()["nombre"].to_string(index=False).strip()
        return result_string

print(testingmujer(10))