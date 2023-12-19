from matplotlib import pyplot as plt
import numpy as np

color = plt.cm.rainbow(np.linspace(0, 1, 10))

data = np.genfromtxt('../data/Cs137.txt', names=True, dtype=(int, int, int, int, int, int, int, int))

print(data["ADC0"])

bins = np.arange(0, 65535, 20)

freq, _ = np.histogram(data["ADC0"], bins=bins, density=None, weights=None)
plt.step(bins[:-1], freq, where='mid', color=color[0])
plt.show()