import matplotlib as mpl

fsize = 18
mpl.rcParams['legend.fontsize'] = fsize-2
mpl.rcParams["figure.figsize"] = (6,5)
mpl.rcParams['axes.labelsize'] = fsize
mpl.rcParams['xtick.labelsize'] = fsize
mpl.rcParams['ytick.labelsize'] = fsize
mpl.rcParams['text.usetex'] = True
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['mathtext.fontset'] = 'dejavusans'
mpl.rcParams.update({'font.size': fsize})

import matplotlib.pyplot as plt
import numpy as np

fnames = ["Cs137-100000.txt", "Cs137-10000.txt", "Na22-50000.txt", "Na22-10000.txt"]

colors = ["blue", "blue", "orange", "orange"]
names = ["Cs137-100000", "Cs137-10000", "Na22-50000", "Na22-10000"]

fig, ax = plt.subplots()
for n, name in enumerate(fnames):
	data = np.genfromtxt("sd_backup-1/"+name, dtype=int, skip_header=1).swapaxes(0, 1)[1]

	max_adc = data.max()
	min_adc = data.min()

	dx = (max_adc-min_adc)/100

	bins = np.arange(min_adc, max_adc+dx, dx)

	freq, _ = np.histogram(data, bins=bins)

	plt.step(bins[:-1], freq, where="mid", label=names[n], color=colors[n])

plt.ylabel("counts")
plt.xlabel("ADC channel")

plt.grid(which="both")
plt.legend()

plt.savefig("sd_backup-1/figures/first_spectra.pdf", bbox_inches="tight")