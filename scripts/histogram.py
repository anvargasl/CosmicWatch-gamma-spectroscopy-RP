from matplotlib import pyplot as plt
import numpy as np

color = plt.cm.rainbow(np.linspace(0, 1, 10))

cols = 12

dV = 20 #mV
iterations = len(range(30, 231, dV))
#iterations = len([30, 60,250])

repetitions = 10

tot_events = iterations*repetitions
print(tot_events)

data = np.array([[None]*cols]*tot_events)

data = np.genfromtxt('../data/test100000.txt', names=True, skip_header=2, dtype=("|S10", "|S10", int, int, int, int, int, int, int))

print(data["ADC_value"][0])

bins = np.arange(0, 65535, 20)

freq, _ = np.histogram(data["ADC_value"], bins=bins, density=None, weights=None)
plt.step(bins[:-1], freq, where='mid', color=color[0])
plt.show()

'''with open("../data/test01.txt", "r") as file:
    for i, line in enumerate(file):
        if i in [0, 1]: continue
        line = line.strip().split("\t")
        data[i-2] = np.array([int(j) for j in line])

#print(data[0][1])
#data_T = data.transpose(1, 0)
print(data)


#colors = ["b", "orange", "g"]
for i in range(0, iterations):
    print(i*repetitions)
    for r in range(0,repetitions):
        t0 = data[i*repetitions+r][2]
        times = [0]+[t for t in data[i*repetitions+r][3:7]]
        plt.plot(times, data[i*repetitions+r][7:], color=color[i])
    
    plt.text(x=160, y=data[i*repetitions][-1], s=str(data[i*repetitions][0]), color=color[i])

plt.yscale(value="log")
plt.show()'''