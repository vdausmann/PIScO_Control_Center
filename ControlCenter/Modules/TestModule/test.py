import numpy as np
import matplotlib.pyplot as plt
import sys

args = sys.argv[1:]
keys = args[::2]
values = args[1::2]

settings = {keys[i][2:]: values[i] for i in range(len(keys))}
print(settings)
x = np.linspace(float(settings["x0"]), float(settings["x1"]), int(settings["nPoints"]))
plt.plot(x, x**2)
plt.show()
