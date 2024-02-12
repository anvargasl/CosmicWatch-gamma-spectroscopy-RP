import matplotlib as mpl

fsize = 18
mpl.rcParams['legend.fontsize'] = fsize
mpl.rcParams["figure.figsize"] = (6,5)
mpl.rcParams['axes.labelsize'] = fsize
mpl.rcParams['xtick.labelsize'] = fsize
mpl.rcParams['ytick.labelsize'] = fsize
mpl.rcParams['text.usetex'] = True
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['mathtext.fontset'] = 'dejavusans'
mpl.rcParams.update({'font.size': fsize})

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import re
from pathlib import Path

#file where the Histogram class is defined
import histogram_class as hmc

#parameters
vmin = 13
vmax = 100
nbins = 50
dv = round((vmax-vmin)/nbins, 2)

#list of isotopes used
isotopes = ['Co60', 'Na22', 'Cs137']
isotope_labels = {'Co60': "$^{60}$Co", 'Cs137': "$^{137}$Cs", 'Na22': "$^{22}$Na"}
#list of source-detector distances used [cm]
distances = [15, 25]
#list of measuring times [min]
times = [10, 30, 60, 120, 180, 840]

'''#Isotope class
class Isotope(object):

    def __init__(self, name):
        self.name = name
        self.Idistances = list()
        self.Itimes = list()
        self.Ihistograms = dict()

    def addDistance(self, distance):
        self.Idistances.append(distance)

    def addTime(self, time):
        self.Itimes.append(time)

    def addHistogram(self, distance, time, histogram):
    	if distance not in self.Idistances:
    		self.addDistance(distance)
		if time not in self.Itimes:
			self.addTime(time)

    	self.Ihistograms[distance][time] = histogram'''

saved_histograms = dict()

#template of data file names
file_template = "../data/Co60-25cm-10min.txt"

#list of matplotlib colors
color_tab = list(mpl.colors.TABLEAU_COLORS.keys())

hist = None
for isotope in isotopes:

	#using regex to change isotope name
	file_template = re.sub("[/]+\w+\-+", "/"+isotope+"-", file_template)	

	for d in distances:

		fig, ax = plt.subplots()

		#using regex to change distance to source
		file_template = re.sub("\d+cm", str(d)+"cm", file_template)

		i = -1 #index to keep track of colors in plotting
		for t in times:

			#using regex to change measuring time
			file_template = re.sub("\d+min", str(t)+"min", file_template)

			#check file exists
			path = Path(file_template)
			if path.is_file():
				print("reading: "+file_template)
				i += 1 #increase color index if file exists
			else:
				print("No such file or directory: "+file_template)
				continue

			#----------extracting data----------#
			#read only lines that start and end with numbers
			pattern = re.compile(r'^\d.+\d$')
			events = list()

			with open(file_template, 'r', encoding="utf-8") as fhandle:
				#try:
				for line in fhandle:
					if re.match(pattern, line):
						line = line.strip('\n')
						events.append(list(map(float, line.split()[2:-1])))
				'''except:
					#utf-8 decoding problem in some files
					print(file_template, "could not be read")'''
			
			#turn data into dataframe
			data = pd.DataFrame(events, columns=['Event', 'Ardn_time[ms]', 'ADC[0-1023]', 'SiPM[mV]', 'Deadtime[ms]'])
			data = data.set_index(['Event'])

			#build the histogram
			freq, bin_edges = np.histogram(data['SiPM[mV]'], bins=nbins, range=(vmin, vmax), density=None, weights=None)

			hist = hmc.Histogram(bin_edges, freq)

			#----------statistics----------#

			hist.normalize()
			
			hist.getMean()

			hist.getSigma()

			hist.getErrors()

			if t==840 and d==15:
				saved_histograms[isotope] = hist

			#----------plotting----------#
			#normalized histogram
			plt.step(hist.bin_centers, hist.norm_freq, where='mid', label=str(t)+" min", color=color_tab[i])

			#error bars in event count
			plt.fill_between(hist.bin_centers, hist.norm_freq-hist.norm_freq_err, hist.norm_freq+hist.norm_freq_err, step='mid', alpha=0.5, color=color_tab[i])

			#vertical line at mean
			plt.axvline(x=hist.mean, linestyle=':', label="mean$=$"+str(hist.mean)+"$\pm$"+str(hist.mean_err), color=color_tab[i])

			#shaded area between mean standard errors
			ax.axvspan(hist.mean-hist.mean_err, hist.mean+hist.mean_err, alpha=0.2, color=color_tab[i])

		#----------ploting----------#
		plt.title(isotope_labels[isotope]+" "+str(d)+" cm")
		plt.xlabel("SiPM peak voltage [mV]")
		plt.ylabel("Events/"+str(dv)+" mV")

		plt.grid(zorder=-3)

		plt.legend()

		plt.savefig("../figures/pscint_"+isotope+"_"+str(d)+"cm.pdf", bbox_inches="tight")
		plt.clf()

#shared histograms
fig, ax = plt.subplots()

hist = None
for k, isotope in enumerate(isotopes):
	hist = saved_histograms[isotope]

	#normalized histogram
	plt.step(hist.bin_centers, hist.norm_freq, where='mid', label=isotope_labels[isotope], color=color_tab[k])

	#error bars in event count
	plt.fill_between(hist.bin_centers, hist.norm_freq-hist.norm_freq_err, hist.norm_freq+hist.norm_freq_err, step='mid', alpha=0.5, color=color_tab[k])

	#vertical line at mean
	plt.axvline(x=hist.mean, linestyle=':', label="mean$=$"+str(hist.mean)+"$\pm$"+str(hist.mean_err), color=color_tab[k])

	#shaded area between mean standard errors
	ax.axvspan(hist.mean-hist.mean_err, hist.mean+hist.mean_err, alpha=0.2, color=color_tab[k])

plt.title("840 min")
plt.xlabel("SiPM peak voltage [mV]")
plt.ylabel("Events/"+str(dv)+" mV")

plt.grid(zorder=-3)

plt.legend()

plt.savefig("../figures/pscint_shared_hist_"+str(d)+"cm.pdf", bbox_inches="tight")
plt.clf()