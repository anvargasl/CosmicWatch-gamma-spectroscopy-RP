import matplotlib.pyplot as plt
import numpy as np
import json

#file where the Histogram class is defined
import histogram_class as hmc

integration = ""
spectra_folder = "spectra/"
data_folder = "PICO/"+integration

config = 	{"october-13-2023-high-energies/": "teflon-side-",
		  	"2024-04-30/": "test_600s_",
		  	"2024-05-22/": "1800s_",
		  	"2024-05-24/"+integration: "",
		  	"PICO/": ""}
config_bkgd = 	{"october-13-2023-high-energies/": "teflon-",
		  		"2024-04-30/": "test_600s_",
				"2024-05-22/": "1800s_",
		  		"2024-05-24/"+integration: "",
				"PICO/": ""}
columns = {"october-13-2023-high-energies/": [0,2],
		  	"2024-04-30/": [0,2],
			"2024-05-22/": [0,2],
		  	"2024-05-24/"+integration: [0,2],
			"PICO/": [0,1]}
dtypes = {"october-13-2023-high-energies/": [("x", int), ("y", int)],
		"2024-04-30/": [("x", int), ("y", int)],
		"2024-05-22/": [("x", int), ("y", int)],
		"2024-05-24/"+integration: [("x", int), ("y", int)],
		"PICO/": [("x", int), ("y", int)]}

erase_bkgd = 1 #0: do not erase, 1: erase
normalize = 0 #0: do not normalize, 1: normalize

with open("../data/"+data_folder+spectra_folder+"calibration.json", "r") as infile:
    calibration = json.load(infile)

#list of isotopes
prefixes = calibration["prefixes"]
#"name" of background file
prefix_bkgd = calibration["prefix_bkgd"]

#----------read data----------#
data_bkgd = np.genfromtxt('../data/'+data_folder+calibration["config_bkgd"]+prefix_bkgd+'.txt', dtype=calibration["dtypes"], names=calibration["column_names"], usecols=calibration["columns"], skip_header=1).T
if calibration["make_histogram"]:
	#Erase corrupt data
	data_bkgd = data_bkgd[data_bkgd["y"] != 8177]
	#data_bkgd = data_bkgd[data_bkgd["y"] != 1120]
	#data_bkgd = data_bkgd[data_bkgd["y"] != 1152]

data = {prefix: np.array([0]) for prefix in prefixes}

max_bin = 0
min_bin = 5000

for prefix in prefixes:
	data[prefix] = np.genfromtxt('../data/'+data_folder+calibration["config"]+prefix+'.txt', dtype=calibration["dtypes"], names=calibration["column_names"], usecols=calibration["columns"], skip_header=1).T

	if calibration["make_histogram"]:
		#Erase corrupt data
		data[prefix] = data[prefix][data[prefix]["y"] != 8177]
		#data[prefix] = data[prefix][data[prefix]["y"] != 1120]
		#data[prefix] = data[prefix][data[prefix]["y"] != 1152]
		#Get maximum posible x value
		temp = data[prefix]["y"].max()
		if max_bin < temp:
			max_bin = temp
		temp = data[prefix]["y"].min()
		if min_bin > temp:
			min_bin = temp
	else:
		#Get maximum posible x value
		temp = data[prefix]["x"].max()
		if max_bin < temp:
			max_bin = temp
		temp = data[prefix]["x"].min()
		if min_bin > temp:
			min_bin = temp

#----------crate histogram----------#
print(min_bin, max_bin)
if calibration["make_histogram"]:
	dx = 1
	bins = np.arange(min_bin, max_bin+(dx/2), dx)
	bin_edges = np.append(bins, bins[-1]+dx)
	print(bin_edges)
else:
	#dx = (max_bin-min_bin)/300
	dx = 1
	bin_edges = data[prefixes[0]]["x"]-dx
	#bin_edges = bins-dx/2
	bin_edges = np.append(bin_edges, bin_edges[-1]+dx)

max_freq = 0
idx_max_freq = None
min_freq = 0

freq = {prefix: np.array([0]) for prefix in prefixes}
for prefix in prefixes:
	if calibration["make_histogram"]:
		#erase duplicates
		temp, indices = np.unique(data[prefix]["x"], return_index=True)
		duplicates = len(data[prefix]["x"])-len(indices)
		if duplicates: print(duplicates, "duplicates found in", prefix)
		#histogram y values
		freq[prefix], _ = np.histogram(data[prefix]["y"][indices], bins=bin_edges)
	else: freq[prefix] = data[prefix]["y"]

	temp = freq[prefix].max()
	idx_max_freq = np.argmax(freq[prefix])
	if max_freq < temp:
		max_freq = temp
		idx_max_freq = np.argmax(freq[prefix])
	temp = freq[prefix].min()
	if min_freq > temp:
		min_freq = temp

if calibration["make_histogram"]:
	#erase duplicates
	temp, indices = np.unique(data_bkgd["x"], return_index=True)
	duplicates = len(data_bkgd["x"])-len(indices)
	if duplicates: print(duplicates, "duplicates found in bkgd")
	#histogram y values
	freq_bkgd, _ = np.histogram(data_bkgd["y"][indices], bins=bin_edges)
else: freq_bkgd = data_bkgd["y"]

if erase_bkgd:
	max_freq = max_freq-freq_bkgd[idx_max_freq]

spectrum_bkgd = hmc.Histogram(prefix_bkgd, dx, bin_edges, freq_bkgd)
if normalize: spectrum_bkgd.normalize(max_freq, np.sqrt(max_freq))

spectrum_bkgd.getErrors()
spectrum_bkgd.print_hist(f_name='../data/'+data_folder+spectra_folder+prefix_bkgd+'_spectrum.txt')

spectrums = {p:None for p in prefixes}

spectrums = {prefix: np.array([0]) for prefix in prefixes}
for prefix in prefixes:
	spectrums[prefix] = hmc.Histogram(prefix, dx, bin_edges, freq[prefix]-erase_bkgd*freq_bkgd)
	
	#----------statistics----------#
	if normalize: spectrums[prefix].normalize(max_freq, np.sqrt(max_freq))

	spectrums[prefix].getErrors()
	spectrums[prefix].print_hist(f_name='../data/'+data_folder+spectra_folder+prefix+'_spectrum.txt')

	plt.plot(spectrums[prefix].bin_centers, spectrums[prefix].norm_freq, label=prefix, color=calibration["colors"][prefix])

#plt.plot(spectrum_bkgd.bin_centers, spectrum_bkgd.norm_freq, label=prefix_bkgd, alpha=0.3)

plt.legend()

#if not erase_bkgd: plt.yscale(value='log')
plt.show()