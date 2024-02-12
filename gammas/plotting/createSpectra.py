import numpy as np

#file where the Histogram class is defined
import histogram_class as hmc

prefixes = ['Na22-live', 'Cs137-live']
prefix_bkgd = 'bkgd-live'

#read background
maxvalues_bkgd = np.genfromtxt('../data/Waveform_histories/Waveform_data/'+prefix_bkgd+'-amplitudes.txt', dtype=float, skip_header=1)
areas_bkgd= np.genfromtxt('../data/Waveform_histories/Waveform_data/'+prefix_bkgd+'-areas.txt', dtype=float, skip_header=1)

#read data
maxvalues = {prefix: np.array([0]) for prefix in prefixes}
areas = {prefix: np.array([0]) for prefix in prefixes}

#erasing 0 areas and maxvalues.
maxvalues_bkgd[maxvalues_bkgd == 0] = np.nan
maxvalues_bkgd = maxvalues_bkgd[~np.isnan(maxvalues_bkgd)]
areas_bkgd[areas_bkgd == 0] = np.nan
areas_bkgd = areas_bkgd[~np.isnan(areas_bkgd)]

max_maxvalue = 0
max_area = 0

min_maxvalue = 0
min_area = 0

#----------read data----------#
for prefix in prefixes:
	maxvalues[prefix] = np.genfromtxt('../data/Waveform_histories/Waveform_data/'+prefix+'-amplitudes.txt', dtype=float, skip_header=1)
	areas[prefix] = np.genfromtxt('../data/Waveform_histories/Waveform_data/'+prefix+'-areas.txt', dtype=float, skip_header=1)
	#areas = np.concatenate((areas, temp))

	#erasing 0 areas and maxvalues.
	maxvalues[prefix][maxvalues[prefix] == 0] = np.nan
	maxvalues[prefix] = maxvalues[prefix][~np.isnan(maxvalues[prefix])]
	areas[prefix][areas[prefix] == 0] = np.nan
	areas[prefix] = areas[prefix][~np.isnan(areas[prefix])]
	#areas[areas == 0] = np.nan
	#areas = areas[~np.isnan(areas)]

	temp = maxvalues[prefix].max()
	if max_maxvalue < temp:
		max_maxvalue = temp
	temp = areas[prefix].max()
	if max_area < temp:
		max_area = temp
	temp = maxvalues[prefix].min()
	if min_maxvalue > temp:
		min_maxvalue = temp
	temp = areas[prefix].min()
	if min_area > temp:
		min_area = temp

print(min_area)
print(max_area)

#----------crate histogram----------#
dx = (max_area-min_area)/300
print('resolution =', dx*1e9, 'nV/s')
bins = np.arange(min_area, max_area+(dx/2), dx)

bin_edges = bins*1e9

spectrums = {p:None for p in prefixes}
max_freq_area = 0

freq_bkgd, _ = np.histogram(areas_bkgd, bins=bins, density=None, weights=None)

for prefix in prefixes:
	freq, _ = np.histogram(areas[prefix], bins=bins, density=None, weights=None)

	spectrums[prefix] = hmc.Histogram(prefix, dx*1e9, bin_edges, freq-freq_bkgd)
	
	#find maximum frequency to normalize
	temp = spectrums[prefix].freq.max()
	if max_freq_area < temp:
		max_freq_area = temp

spectrum_bkgd = hmc.Histogram(prefix_bkgd, dx*1e9, bin_edges, freq_bkgd)
spectrum_bkgd.normalize(max_freq_area, np.sqrt(max_freq_area))

spectrum_bkgd.getErrors()
spectrum_bkgd.print_hist(f_name='../data/Waveform_histories/spectra/'+prefix_bkgd+'-spectrum.txt')

for prefix in prefixes:
	#----------statistics----------#
	spectrums[prefix].normalize(max_freq_area, np.sqrt(max_freq_area))

	#spectrums[prefix].getMean()
	#spectrums[prefix].getSigma()
	spectrums[prefix].getErrors()
	spectrums[prefix].print_hist(f_name='../data/Waveform_histories/spectra/'+prefix+'-spectrum.txt')