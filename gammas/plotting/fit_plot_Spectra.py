import matplotlib as mpl

fsize = 12
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
import numpy as np
import json

#file where the Histogram class is defined
import histogram_class as hmc

folder = 'october-13-2023-high-energies/'
with open("../data/"+folder+"calibration.json", "r") as infile:
    calibration = json.load(infile)

#list of isotopes
prefixes = calibration["prefixes"]
#"name" of background file
prefix_bkgd = calibration["prefix_bkgd"]

material = "teflon"
config = material+"-side"

#list of matplotlib colors
color_list = list(mpl.colors.TABLEAU_COLORS.keys())
color_tab = {p:c for (p,c) in zip(prefixes,color_list[0:len(prefixes)])}
fit_tab = {p:c for (p,c) in zip(prefixes,color_list[len(prefixes):2*len(prefixes)])}

#----------fitting/plotting area----------#
from fitting import Fit_Gauss_plus_bkgd

fig, ax = plt.subplots()

fit = input("fit? [y,n]")
for prefix in prefixes:
	fname = '../data/'+folder+'spectra/'+config+'-'+prefix+'-spectrum.txt'
	spectrum = hmc.Histogram(f_name=fname)

	#normalized histogram
	plt.step(spectrum.bin_centers, spectrum.norm_freq, where='mid', label=prefix, color=color_tab[prefix])
	#error bars in event count
	plt.fill_between(spectrum.bin_centers, spectrum.norm_freq-spectrum.norm_freq_err, spectrum.norm_freq+spectrum.norm_freq_err, step='mid', alpha=0.5, color=color_tab[prefix])

	#----------fitting----------#
	if fit == "y":
		for peak in list(calibration["peak_dict"][prefix].keys()):

			idxmin = int((calibration["peak_dict"][prefix][peak]["range"][0]-spectrum.bin_centers[0])/(spectrum.bin_size))
			idxmax = int((calibration["peak_dict"][prefix][peak]["range"][1]-spectrum.bin_centers[0])/(spectrum.bin_size))+1

			xFit = spectrum.bin_centers[idxmin:idxmax]
			yFit = spectrum.norm_freq[idxmin:idxmax]

			result = Fit_Gauss_plus_bkgd(x=xFit, y=yFit, parameters=list(calibration["peak_dict"][prefix][peak]["fit_init"].values()))

			mu = result.params['mu'].value
			mu_err = result.params['mu'].stderr

			print('\n'+fname)
			print(prefix, peak, calibration["peak_dict"][prefix][peak]["range"])

			print(result.fit_report())

			#fit
			if len(prefixes)==1:
				label = r'$\mu=$'+str(round(mu,2))+'$\pm$'+str(round(mu_err,2))
			else:
				label = None
			plt.plot(xFit, result.best_fit, '-', label=label, color=fit_tab[prefix])
			#if peak == '662 keV' or peak == 'extra':
			#	plt.axvline(mu, color=fit_tab[prefix], ymin=0.0, ymax=1.0, ls='--')
		
			result_list = json.loads(result.params.dumps())["params"]
			total_params = len(result_list)
			names = [result_list[i][0] for i in range(total_params)]
			values = [result_list[i][1] for i in range(total_params)]
			stderrs = [result_list[i][7] for i in range(total_params)]

			calibration["peak_dict"][prefix][peak]["fit_results"] = {n:[v, s] for n, v, s in zip(names, values, stderrs)}
	elif fit == "n":
		continue
	else:
		print("valid options are \"y\" or \"n\", not fitting.")

#plot background
spectrum_bkgd = hmc.Histogram(f_name='../data/'+folder+'spectra/'+material+'-bkgd-spectrum.txt')

color_bkgd = color_list[len(prefixes)]
plt.step(spectrum_bkgd.bin_centers, spectrum_bkgd.norm_freq, where='mid', label=prefix_bkgd, color=color_bkgd)
plt.fill_between(spectrum_bkgd.bin_centers, spectrum_bkgd.norm_freq-spectrum_bkgd.norm_freq_err, spectrum_bkgd.norm_freq+spectrum_bkgd.norm_freq_err, step='mid', alpha=0.5, color=color_bkgd)

with open("../data/"+folder+"calibration.json", "w") as outfile: 
    json.dump(calibration, outfile, indent=4)

major_x = np.arange(0, 101, 50)
minor_x = np.arange(0, 101, 10)
ax.set_xticks(major_x)
ax.set_xticks(minor_x, minor=True)

#ax.set_xlim(right=50)

ax.grid(which='both', axis='both')
ax.grid(which='minor', axis='both', alpha=0.3)

plt.xlabel(r'SiPM pulse area [nV$/$s]')
plt.ylabel(r'$I/I_{max}$')

plt.legend()

if len(prefixes)==1:
	plt.savefig('../figures/Waveform_histograms/'+folder+config+'-'+prefix+'-areas.pdf', bbox_inches="tight")
else:
	plt.yscale(value="log")
	plt.savefig('../figures/Waveform_histograms/'+folder+config+'-areas.pdf', bbox_inches="tight")
