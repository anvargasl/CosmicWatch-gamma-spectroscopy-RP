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

folder = 'october-13-2023-high-energies/'
with open("../data/"+folder+"calibration.json", "r") as infile:
    calibration = json.load(infile)

#list of isotopes
prefixes = calibration["prefixes"]
#"name" of background file
prefix_bkgd = calibration["prefix_bkgd"]

material = 'teflon'
config = material+'-side'

energies = [31, 184, 511, 662, 1173.2, 1275, 1332.5]
mu = [1.405069992570683, 14.67690995851796, 37.290691505236666, 47.58509489979077, 79.12698406535378, 85.68114903249612, 88.94871447630919]
mu_err = [0.017049118266542616, 0.052918461845158256, 0.02676790223704887, 0.012339940915039342, 0.21604323503182687, 0.12589545305841973, 0.2279671720130705]

#----------fitting----------#
from fitting import Fit_Line

params = [-32, 24]

result1 = Fit_Line(x=mu, y=energies, parameters=params)

#----------plotting fit----------#
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

	plt.grid()
	#plt.ylim(20,60)
	plt.xlabel('channel')
	plt.ylabel('energy [keV]')

	#data
	plt.errorbar(mu, energies, xerr=mu_err, fmt='o', ms=5)

	#fit
	Xplot = np.arange(0, 100, 0.1)
	Yplot = a0[i] + a1[i]*Xplot

	lbl_str = str(round(a0[i],2))+'('+str(round(a0_err[i],2))+')'+' + '+str(round(a1[i],2))+'('+str(round(a1_err[i],2))+')'+r'$\cdot$ c'
	plt.plot(Xplot, Yplot, '-', label=lbl_str)
	print(result.fit_report())

plt.legend(fontsize=12)
plt.savefig("../figures/Waveform_histograms/"+folder+"LYSO_calibration.pdf", bbox_inches="tight")

plt.clf()

#list of matplotlib colors
color_list = list(mpl.colors.TABLEAU_COLORS.keys())
color_tab = {p:c for (p,c) in zip(prefixes,color_list[0:len(prefixes)])}

#file where the Histogram class is defined
import histogram_class as hmc

fig, ax = plt.subplots()

X = None
for prefix in prefixes:
	spectrum = hmc.Histogram(f_name='../data/'+folder+'spectra/'+config+'-'+prefix+'-spectrum.txt')

	X = [a0[0] + a1[0]*x for x in spectrum.bin_centers]

	plt.step(X, spectrum.norm_freq, where='mid', label=prefix, color=color_tab[prefix])
	#error bars in event count
	plt.fill_between(X, spectrum.norm_freq-spectrum.norm_freq_err, spectrum.norm_freq+spectrum.norm_freq_err, step='mid', alpha=0.5, color=color_tab[prefix])

#plot background
spectrum_bkgd = hmc.Histogram(f_name='../data/'+folder+'spectra/'+material+'-bkgd-spectrum.txt')

color_bkgd = color_list[len(prefixes)]
plt.step(X, spectrum_bkgd.norm_freq, where='mid', label=prefix_bkgd, color=color_bkgd)
plt.fill_between(X, spectrum_bkgd.norm_freq-spectrum_bkgd.norm_freq_err, spectrum_bkgd.norm_freq+spectrum_bkgd.norm_freq_err, step='mid', alpha=0.5, color=color_bkgd)

plt.axvline(290, color=color_bkgd, alpha=0.5, ymin=0.0, ymax=1.0, ls='--', label='E = 290 keV')
plt.axvline(597, color=color_bkgd, alpha=0.5, ymin=0.0, ymax=1.0, ls='--', label='E = 597 keV')
#plt.axvline(477, color='orange', alpha=0.5, ymin=0.0, ymax=1.0, ls='--', label='E = 662 keV Compton Edge')
#plt.axvline(1061, color='blue', alpha=0.5, ymin=0.0, ymax=1.0, ls='--', label='E = 1274 keV Compton Edge')

major_x = np.arange(0, 1500, 250)
#minor_x = np.arange(0, 101, 10)
ax.set_xticks(major_x)
#ax.set_xticks(minor_x, minor=True)

#ax.set_xlim(left=-100, right=1500)

ax.grid(which='both', axis='both')
ax.grid(which='minor', axis='both', alpha=0.3)

#plt.title(prefixes[0]+' Areas Histogram, '+str(bins)+' bins')

plt.xlabel(r'E [keV]')
plt.ylabel(r'$I/I_{max}$')

plt.yscale(value='log')

plt.legend()

plt.savefig('../figures/Waveform_histograms/'+folder+'Calibrated_spectrum.pdf', bbox_inches="tight")