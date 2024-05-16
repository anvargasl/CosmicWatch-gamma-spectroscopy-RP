import matplotlib as mpl

fsize = 12
mpl.rcParams['legend.fontsize'] = fsize-2
mpl.rcParams["figure.figsize"] = (10,5)
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

#material = 'teflon'
#config = material+'-side'
config = "teflon-side-"
config_bkgd = "teflon-"

#list of matplotlib colors
color_list = list(mpl.colors.TABLEAU_COLORS.keys())
color_tab = {p:c for (p,c) in zip(prefixes,color_list[0:len(prefixes)])}
color_bkgd = color_list[-1]

energies = list()
mu = list()
mu_err = list()

#read Gaussian fit results
for prefix in prefixes:
	for peak in list(calibration["peak_dict"][prefix].keys()):

		if calibration["peak_dict"][prefix][peak]["fit?"]:
			energies.append(calibration["peak_dict"][prefix][peak]["energy"])
			mu.append(calibration["peak_dict"][prefix][peak]["fit_results"]["mu"][0])
			mu_err.append(calibration["peak_dict"][prefix][peak]["fit_results"]["mu"][1])

#----------fitting----------#
from fitting import Fit_Line

params = [-9, 3] #y = a0+a1*x
result1 = Fit_Line(x=mu, y=energies, parameters=params)

#---------------plot calibration-----------#
fig, ax = plt.subplots()

a0 = [0,0]
a1 = [0,0]
a0_err = [0,0]
a1_err = [0,0]

for i, result in enumerate([result1]):

	a0[i] = result.params['a0'].value
	a1[i] = result.params['a1'].value
	a0_err[i] = result.params['a0'].stderr
	a1_err[i] = result.params['a1'].stderr

	#data
	plt.errorbar(mu, energies, xerr=mu_err, fmt='o', ms=3)

	#fit
	Xplot = np.arange(min(mu), max(mu), 0.1)
	Yplot = a0[i] + a1[i]*Xplot

	a0_inc = my_uncertainty(a0[i], a0_err[i])
	a0_str = r'$E=~$'+a0_inc[0]+"("+a0_inc[1]+")"
	a1_inc = my_uncertainty(a1[i], a1_err[i])
	a1_str = r' $+$ '+a1_inc[0]+"("+a1_inc[1]+r")$\cdot$ Area"
	plt.plot(Xplot, Yplot, '-', label=a0_str+a1_str)
	print(result.fit_report())

plt.grid()
#plt.ylim(20,60)

#plt.title("Nim "+data_folder[:-1])
plt.title("Rohde\&Schwarz RTO6 oscilloscope")
plt.xlabel(r'SiPM pulse area ['+calibration["x_unit"]+']')
plt.ylabel(r'$E$ [keV]')

plt.legend()
plt.savefig("../figures/"+data_folder+"LYSO_calibration.pdf", bbox_inches="tight")

plt.clf()

#---------------plot calibrated spectra-----------#
fig, ax = plt.subplots()

#plot background
spectrum_bkgd = hmc.Histogram(f_name='../data/'+data_folder+spectra_folder+config_bkgd+prefix_bkgd+'_spectrum.txt')

#Energy domain
X = [a0[0] + a1[0]*x for x in spectrum_bkgd.bin_centers]
plt.step(X, spectrum_bkgd.norm_freq, where='mid', label=prefix_bkgd, color=color_bkgd)
#error bars in event count
#plt.fill_between(X, spectrum_bkgd.norm_freq-spectrum_bkgd.norm_freq_err, spectrum_bkgd.norm_freq+spectrum_bkgd.norm_freq_err, step='mid', alpha=0.5, color=color_bkgd)
plt.axvline(290, color=color_bkgd, alpha=0.7, ymin=0.0, ymax=1.0, ls='-', label='290 keV')
plt.axvline(597, color=color_bkgd, alpha=0.7, ymin=0.0, ymax=1.0, ls='-', label='597 keV')

for prefix in prefixes:
	#read spectra
	spectrum = hmc.Histogram(f_name='../data/'+data_folder+spectra_folder+config+prefix+'_spectrum.txt')

	plt.step(X, spectrum.norm_freq, where='mid', label=prefix, color=color_tab[prefix])
	#error bars in event count
	#plt.fill_between(X, spectrum.norm_freq-spectrum.norm_freq_err, spectrum.norm_freq+spectrum.norm_freq_err, step='mid', alpha=0.5, color=color_tab[prefix])

#plot vertical lines at calibrated peaks
for prefix in prefixes:
	for peak in list(calibration["peak_dict"][prefix].keys()):
		if calibration["peak_dict"][prefix][peak]["fit?"]:
			mu = calibration["peak_dict"][prefix][peak]["fit_results"]["mu"][0]
			energy = a0[0] + a1[0]*mu
			plt.axvline(energy, ymin=0.0, ymax=1.0, color=color_tab[prefix], alpha=0.7, ls='--', lw=1, label=str(round(energy,2))+" keV")

major_x = np.arange(0, X[-1], 500)
minor_x = np.arange(0, X[-1], 250)
ax.set_xticks(major_x)
ax.set_xticks(minor_x, minor=True)
ax.grid(which='both', axis='both')
ax.grid(which='minor', axis='both', alpha=0.3)
#ax.set_xlim(left=0, right=1500)

#plt.title(prefixes[0]+' Areas Histogram, '+str(bins)+' bins')
#plt.title("Nim "+data_folder[:-1])
plt.title("Rohde\&Schwarz RTO6 oscilloscope")

plt.xlabel(r'$E$ [keV]')
plt.ylabel(r'$I/I_{max}$')

plt.yscale(value='log')
plt.legend(loc="lower left", ncols=2)
plt.savefig("../figures/"+data_folder+"Calibrated_spectrum.pdf", bbox_inches="tight")