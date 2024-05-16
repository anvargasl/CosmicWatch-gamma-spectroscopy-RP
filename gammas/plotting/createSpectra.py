import matplotlib.pyplot as plt
import numpy as np
import json

#file where the Histogram class is defined
import histogram_class as hmc

spectra_folder = "spectra/"
data_folder = "october-13-2023-high-energies/"

erase_bkgd = 0 #0: do not erase, 1: erase

with open("../data/"+data_folder+spectra_folder+"calibration.json", "r") as infile:
    calibration = json.load(infile)

#list of isotopes
prefixes = calibration["prefixes"]
#"name" of background file
prefix_bkgd = calibration["prefix_bkgd"]

#----------read data----------#
data_bkgd = np.genfromtxt('../data/'+data_folder+'2024-04-30_'+prefix_bkgd+'_test_600s.txt', dtype=(int, int), usecols=[0,2], skip_header=1).T

data = {prefix: np.array([0]) for prefix in prefixes}

max_freq = 0
idx_max_freq = None
min_freq = 0

for prefix in prefixes:
	data[prefix] = np.genfromtxt('../data/'+data_folder+'2024-04-30_'+prefix+'_test_600s.txt', dtype=(int, int), usecols=[0,2], skip_header=1).T

	temp = data[prefix][1].max()
	if max_freq < temp:
		max_freq = temp
		idx_max_freq = np.argmax(data[prefix][1])
	temp = data[prefix][1].min()
	if min_freq > temp:
		min_freq = temp

if erase_bkgd:
	max_freq = max_freq-data_bkgd[1][idx_max_freq]

print(data['22Na'])

#----------crate histogram----------#
#dx = (max_freq-min_freq)/300
dx = 1
#bins = np.arange(min_area, max_area+(dx/2), dx)

bin_edges = data[prefixes[0]][0]-dx
bin_edges = np.append(bin_edges, bin_edges[-1]+dx)

spectrum_bkgd = hmc.Histogram(prefix_bkgd, dx, bin_edges, data_bkgd[1])
spectrum_bkgd.normalize(max_freq, np.sqrt(max_freq))

spectrum_bkgd.getErrors()
spectrum_bkgd.print_hist(f_name='../data/'+data_folder+spectra_folder+prefix_bkgd+'_spectrum.txt')

plt.plot(spectrum_bkgd.bin_centers, spectrum_bkgd.norm_freq, label=prefix_bkgd)

spectrums = {p:None for p in prefixes}

for prefix in prefixes:
	spectrums[prefix] = hmc.Histogram(prefix, dx, bin_edges, data[prefix][1]-erase_bkgd*data_bkgd[1])
	
	#----------statistics----------#
	spectrums[prefix].normalize(max_freq, np.sqrt(max_freq))

	spectrums[prefix].getErrors()
	spectrums[prefix].print_hist(f_name='../data/'+data_folder+spectra_folder+prefix+'_spectrum.txt')

	plt.plot(spectrums[prefix].bin_centers, spectrums[prefix].norm_freq, label=prefix)

plt.legend()

plt.yscale(value='log')
plt.show()