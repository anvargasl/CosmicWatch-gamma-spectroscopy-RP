import numpy as np
import json

import re

#file where the Histogram class is defined
import histogram_class as hmc

folder = 'october-13-2023-high-energies/'
with open("../data/"+folder+"calibration.json", "r") as infile:
    calibration = json.load(infile)

#list of isotopes
prefixes = calibration["prefixes"]
print(prefixes)
#"name" of background file
prefix_bkgd = calibration["prefix_bkgd"]

material = 'teflon'
config = material+'-side'

setup_file = '../data/'+folder+material+'-'+prefix_bkgd+'-20min-october-13-2023.csv'

XStart = None
XStop = None
Resolution = None
NBins = None

with open(setup_file, 'r', encoding="utf-8") as fhandle:
	for line in fhandle:
		#X axis data in nV*s
		read_in = re.search('(?<=XStart:)(.*?)(?=:)', line)
		if read_in:
			XStart = float(read_in.group(0))*1e9
			continue

		read_in = re.search('(?<=XStop:)(.*?)(?=:)', line)
		if read_in:
			XStop = float(read_in.group(0))*1e9
			continue

		read_in = re.search('(?<=Resolution:)(.*?)(?=:)', line)
		if read_in:
			Resolution = float(read_in.group(0))*1e9
			continue

		read_in = re.search('(?<=NumberOfBins:)(.*?)(?=:)', line)
		if read_in:
			NBins = int(read_in.group(0))

bin_edges = np.array([XStart+i*Resolution for i in range(NBins+1)])

dFrames = list()

#----------read data----------#
spectrums = {p:None for p in prefixes}
max_freq_area = 0

freq_bkgd = np.genfromtxt('../data/'+folder+material+'-'+prefix_bkgd+'-20min-october-13-2023.Wfm.csv', dtype=int)
print(len(freq_bkgd))

for prefix in prefixes:
	freq = np.genfromtxt('../data/'+folder+config+'-'+prefix+'-20min-october-13-2023.Wfm.csv', dtype=int)
	print("not substracting background")
	spectrums[prefix] = hmc.Histogram(prefix, Resolution, bin_edges, freq)

	#find maximum frequency to normalize
	temp = spectrums[prefix].freq.max()
	if max_freq_area < temp:
		max_freq_area = temp

spectrum_bkgd = hmc.Histogram(prefix_bkgd, Resolution, bin_edges, freq_bkgd)
spectrum_bkgd.normalize(max_freq_area, np.sqrt(max_freq_area))

spectrum_bkgd.getErrors()
spectrum_bkgd.print_hist(f_name='../data/'+folder+'spectra/'+material+'-'+prefix_bkgd+'-spectrum.txt')

for prefix in prefixes:
	#----------statistics----------#
	spectrums[prefix].normalize(max_freq_area, np.sqrt(max_freq_area))

	#spectrums[prefix].getMean()
	#spectrums[prefix].getSigma()
	spectrums[prefix].getErrors()
	spectrums[prefix].print_hist(f_name='../data/'+folder+'spectra/'+config+'-'+prefix+'-spectrum.txt')