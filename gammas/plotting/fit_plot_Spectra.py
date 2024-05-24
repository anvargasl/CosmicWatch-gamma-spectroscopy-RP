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
import json

#file where the Histogram class is defined
import histogram_class as hmc
from uncertainty import my_uncertainty

spectra_folder = "spectra/"
data_folder = "october-13-2023-high-energies/"

with open("../data/"+data_folder+spectra_folder+"calibration.json", "r") as infile:
    calibration = json.load(infile)

#list of isotopes
prefixes = calibration["prefixes"]
#"name" of background file
prefix_bkgd = calibration["prefix_bkgd"]

#plotting colors
colors = calibration["colors"]
fit_colors = calibration["fit_colors"]

color_bkgd = calibration["color_bkgd"]

config = "teflon-side-" #Ba133-october-12-2023
config_bkgd = "teflon-" #Ba133-october-12-2023

#config = "" #2024-04-30, 2024-05-22
#config_bkgd = "" #2024-04-30, 2024-05-22

#read background data
spectrum_bkgd = hmc.Histogram(f_name='../data/'+data_folder+spectra_folder+config_bkgd+prefix_bkgd+'_spectrum.txt')

#----------fitting/plotting area----------#
from fitting import Fit_Gauss_plus_bkgd

#fig_dict = {prefix:plt.figure(p) for p, prefix in enumerate(prefixes)}
#print(fig_dict["Co60"])
#fig, ax = plt.subplots()

#fit = input("fit? [y,n]")
fit = "y"
for p, prefix in enumerate(prefixes):
	plt.figure(p)
	fname = '../data/'+data_folder+spectra_folder+config+prefix+'_spectrum.txt'
	spectrum = hmc.Histogram(f_name=fname)

	#background
	plt.step(spectrum_bkgd.bin_centers, spectrum_bkgd.norm_freq, where='mid', label=prefix_bkgd, color=color_bkgd)
	#plt.fill_between(spectrum_bkgd.bin_centers, spectrum_bkgd.norm_freq-spectrum_bkgd.norm_freq_err, spectrum_bkgd.norm_freq+spectrum_bkgd.norm_freq_err, step='mid', alpha=0.5, color=color_bkgd)
	#normalized histogram
	plt.step(spectrum.bin_centers, spectrum.norm_freq, where='mid', label=r"{}".format(calibration["names"][prefix]), color=colors[prefix])
	#error bars in event count
	#plt.fill_between(spectrum.bin_centers, spectrum.norm_freq-spectrum.norm_freq_err, spectrum.norm_freq+spectrum.norm_freq_err, step='mid', alpha=0.5, color=colors[prefix])

	#----------fitting----------#
	if fit == "y":
		for peak in list(calibration["peak_dict"][prefix].keys()):

			if calibration["peak_dict"][prefix][peak]["fit?"]:

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
				mu_inc = my_uncertainty(mu, mu_err)
				#mu_str = r'$\mu=$'+mu_inc[0]+"("+mu_inc[1]+") "+calibration["x_unit"]
				mu_str = r'$\mu=$'+mu_inc[0]+"("+mu_inc[1]+") "
				plt.plot(xFit, result.best_fit, '-', label=mu_str, color=fit_colors[prefix])
			
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
	
	xmin = spectrum_bkgd.bin_centers[0]-(spectrum_bkgd.bin_size/2)
	xmax = spectrum_bkgd.bin_centers[-1]-(spectrum_bkgd.bin_size/2)
	grid_size = 100#(spectrum_bkgd.bin_centers[-1]-spectrum_bkgd.bin_centers[0])/10

	major_x = np.arange(xmin, xmax, int(grid_size))
	#minor_x = np.arange(xmin, xmax, 10)
	ax = plt.gca()
	ax.set_xticks(major_x)
	#ax.set_xticks(minor_x, minor=True)

	#ax.set_xlim(right=50)

	ax.grid(which='both', axis='both')
	#ax.grid(which='minor', axis='both', alpha=0.3)

	#plt.xlabel(r'SiPM pulse area ['+calibration["x_unit"]+']')
	plt.xlabel(r'channel')
	plt.ylabel(r'$I/I_{max}$')
	plt.yscale(value="log")

	plt.legend(loc="lower left")

	plt.savefig('../figures/'+data_folder+config+prefix+'.pdf', bbox_inches="tight")

#save calibration data
with open("../data/"+data_folder+spectra_folder+"calibration.json", "w") as outfile: 
    json.dump(calibration, outfile, indent=4)

#plot background
plt.figure(len(prefixes))
plt.step(spectrum_bkgd.bin_centers, spectrum_bkgd.norm_freq, where='mid', label=prefix_bkgd, color=color_bkgd)
#plt.fill_between(spectrum_bkgd.bin_centers, spectrum_bkgd.norm_freq-spectrum_bkgd.norm_freq_err, spectrum_bkgd.norm_freq+spectrum_bkgd.norm_freq_err, step='mid', alpha=0.5, color=color_bkgd)

xmin = spectrum_bkgd.bin_centers[0]-(spectrum_bkgd.bin_size/2)
xmax = spectrum_bkgd.bin_centers[-1]-(spectrum_bkgd.bin_size/2)
grid_size = 100#(spectrum_bkgd.bin_centers[-1]-spectrum_bkgd.bin_centers[0])/10

major_x = np.arange(xmin, xmax, int(grid_size))
#minor_x = np.arange(xmin, xmax, 10)
ax = plt.gca()
ax.set_xticks(major_x)
#ax.set_xticks(minor_x, minor=True)

#ax.set_xlim(right=50)

ax.grid(which='both', axis='both')
#ax.grid(which='minor', axis='both', alpha=0.3)

#plt.xlabel(r'SiPM pulse area ['+calibration["x_unit"]+']')
plt.xlabel(r'channel')
plt.ylabel(r'$I/I_{max}$')
plt.yscale(value="log")

plt.legend(loc="lower left")

plt.savefig('../figures/'+data_folder+config_bkgd+prefix_bkgd+'.pdf', bbox_inches="tight")