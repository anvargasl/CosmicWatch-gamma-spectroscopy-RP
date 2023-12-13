from matplotlib import pyplot as plt
import numpy as np

cols = 12

dV = 20 #mV
iterations = len(range(30, 231, dV))
#iterations = len([30, 60,250])

repetitions = 10

tot_events = iterations*repetitions
print(tot_events)

data = np.array([[None]*cols]*tot_events)
with open("../data/calibration.txt", "r") as file:
    for i, line in enumerate(file):
        if i == 0: continue
        line = line.strip().split("\t")
        data[i-1] = np.array([int(j) for j in line])

#print(data[0][1])
#data_T = data.transpose(1, 0)
print(data)

color = plt.cm.rainbow(np.linspace(0, 1, iterations))
#colors = ["b", "orange", "g"]
for i in range(0, iterations):
    print(i*repetitions)
    for r in range(0,repetitions):
        t0 = data[i*repetitions+r][2]
        times = [0]+[t for t in data[i*repetitions+r][3:7]]
        plt.plot(times, data[i*repetitions+r][7:], color=color[i])
    
    plt.text(x=160, y=data[i*repetitions][-1], s=str(data[i*repetitions][0]), color=color[i])

plt.yscale(value="log")
plt.show()