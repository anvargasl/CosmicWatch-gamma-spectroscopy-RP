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

integration = ""
spectra_folder = "spectra/"
data_folder = "october-13-2023-high-energies/"+integration

config = 	{"october-13-2023-high-energies/": "teflon-side-",
		  "2024-04-30/": "test_600s_",
		  "2024-05-22/": "1800s_",
		  "2024-05-24/"+integration: ""}
config_bkgd = 	{"october-13-2023-high-energies/": "teflon-",
		  		"2024-04-30/": "test_600s_",
				"2024-05-22/": "1800s_",
		  		"2024-05-24/"+integration: ""}
data_type = {"october-13-2023-high-energies/": "RTO6",
		  	"2024-04-30/": "NIM",
			"2024-05-22/": "NIM",
		  	"2024-05-24/"+integration: "NIM"}

with open("../data/"+data_folder+spectra_folder+"calibration.json", "r") as infile:
    calibration = json.load(infile)

if data_type[data_folder] == "RTO6":
	a1_units = r") [keV/nVs] $\cdot$Area"
	s1_units = r") [keV$^{1/2}$] $\sqrt{E}$"

	calib_title = "Rohde\&Schwarz RTO6 oscilloscope"
	calib_x_units = r"SiPM pulse Area [nVs]"

	major_dE = 100
	minor_dE = 25

	if calibration["peak_dict"]["Cs137"]["31 keV"]["fit?"]:
		calib_title = "Rohde\&Schwarz RTO6 oscilloscope"
		E_lims = [-100, 1500]
	else:
		calib_title = r"RTO6, No backscatter and x-ray peaks of $^{137}$Cs"
		E_lims = [-100, 1500]

elif data_type[data_folder] == "NIM":

	a1_units = r") [keV/ch] $\cdot$channel"
	s1_units = r") [keV$^{1/2}$] $\sqrt{E}$"

	calib_x_units = r'channel [ch]'

	if data_folder in ["2024-04-30/", "2024-05-22/"]:
		calib_title = ""
		E_lims = [0, 2000]
		major_dE = 100
		minor_dE = 25
	elif data_folder == "2024-05-24/"+integration:
		if integration == "outD/":
			calib_title = r"Integration time = 4 ns, differentiation time = 160 $\mu$s"
		else:
			calib_title = "differentiate time = "+integration[:-2]+" ns"
		E_lims = [0, 1650]
		major_dE = 100
		minor_dE = 25		

#list of isotopes
prefixes = calibration["prefixes"]
#"name" of background file
prefix_bkgd = calibration["prefix_bkgd"]

#plotting colors
colors = calibration["colors"]
fit_colors = calibration["fit_colors"]

color_bkgd = calibration["color_bkgd"]

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

#----------fitting E vs channel----------#
import fitting

params = calibration["E_chan_transform"]["fit_init"] #y = a0+a1*x
result = fitting.Fit_Line(x=mu, y=energies, parameters=params)

a0 = result.params['a0'].value
a1 = result.params['a1'].value
a0_err = result.params['a0'].stderr
a1_err = result.params['a1'].stderr

calibration["E_chan_transform"]["fit_init"] = params #save calibration data
calibration["E_chan_transform"]["a0"] = [a0, a0_err]
calibration["E_chan_transform"]["a1"] = [a1, a1_err]
calibration["E_chan_transform"]["chi2"] = result.chisqr

print(result.fit_report())

#---------------plot calibration-----------#
plt.figure(0)

#data
plt.errorbar(mu, energies, xerr=mu_err, fmt='o', ms=3)

#fit
Xplot = np.arange(min(mu), max(mu), 0.1)
Yplot = a0 + a1*Xplot

a0_inc = my_uncertainty(a0, a0_err)
a0_str = r'$E=~$'+a0_inc[0]+"("+a0_inc[1]+") [keV]"
a1_inc = my_uncertainty(a1, a1_err)
a1_str = r' $+$ '+a1_inc[0]+"("+a1_inc[1]+a1_units
plt.plot(Xplot, Yplot, '-', label=a0_str+a1_str)

plt.title(calib_title)
plt.xlabel(calib_x_units)
plt.ylabel(r'$E$ [keV]')

plt.grid()
plt.legend()
if data_type[data_folder] == "RTO6":
	if calibration["peak_dict"]["Cs137"]["31 keV"]["fit?"]:
		plt.savefig("../figures/"+data_folder+"LYSO_calibration_low_peaks.pdf", bbox_inches="tight")
	else:
		plt.savefig("../figures/"+data_folder+"LYSO_calibration.pdf", bbox_inches="tight")
else:
	plt.savefig("../figures/"+data_folder+"LYSO_calibration.pdf", bbox_inches="tight")

plt.clf()

#---------------plot calibrated spectra-----------#
plt.figure(1)

#plot background
spectrum_bkgd = hmc.Histogram(f_name='../data/'+data_folder+spectra_folder+prefix_bkgd+'_spectrum.txt')

#Energy domain
X = np.array([a0 + a1*x for x in spectrum_bkgd.bin_centers])
plt.step(X, spectrum_bkgd.norm_freq, where='mid', label=prefix_bkgd, color=color_bkgd)
#error bars in event count
#plt.fill_between(X, spectrum_bkgd.norm_freq-spectrum_bkgd.norm_freq_err, spectrum_bkgd.norm_freq+spectrum_bkgd.norm_freq_err, step='mid', alpha=0.5, color=color_bkgd)
plt.axvline(290, color=color_bkgd, alpha=0.7, ymin=0.0, ymax=1.0, ls=':', label='290 keV')
plt.axvline(597, color=color_bkgd, alpha=0.7, ymin=0.0, ymax=1.0, ls=':', label='597 keV')

for prefix in prefixes:
	#read spectra
	spectrum = hmc.Histogram(f_name='../data/'+data_folder+spectra_folder+prefix+'_spectrum.txt')

	plt.step(X, spectrum.norm_freq, where='mid', label=prefix, color=colors[prefix])
	#error bars in event count
	#plt.fill_between(X, spectrum.norm_freq-spectrum.norm_freq_err, spectrum.norm_freq+spectrum.norm_freq_err, step='mid', alpha=0.5, color=color_tab[prefix])

#plot vertical lines at calibrated peaks
FWHM_values = list()
FWHM_errs = list()
FWHM = None
FWHM_err = None

B = 2*np.sqrt(2*np.log(2))

for prefix in prefixes:
	for peak in list(calibration["peak_dict"][prefix].keys()):

		if calibration["peak_dict"][prefix][peak]["fit?"]:
			mu = calibration["peak_dict"][prefix][peak]["fit_results"]["mu"][0]
			energy = a0 + a1*mu
			plt.axvline(energy, ymin=0.0, ymax=1.0, color=colors[prefix], alpha=0.7, ls='--', lw=1, label=str(round(energy,2))+" keV")

			sigma = calibration["peak_dict"][prefix][peak]["fit_results"]["sigma"][0]
			sigma_err = calibration["peak_dict"][prefix][peak]["fit_results"]["sigma"][1]

			FWHM = B*sigma*a1 #keV
			FWHM_err = B*np.sqrt((a1*sigma_err)**2+(sigma*a1_err)**2)
			calibration["peak_dict"][prefix][peak]["FWHM [keV]"] = [FWHM, FWHM_err]

			FWHM_values.append(FWHM)
			FWHM_errs.append(FWHM_err)

major_x = np.arange(E_lims[0], E_lims[1]+minor_dE, major_dE)
minor_x = np.arange(E_lims[0], E_lims[1], minor_dE)
plt.xticks(major_x)
plt.xticks(minor_x, minor=True)
plt.grid(which='both', axis='both')
plt.grid(which='minor', axis='both', alpha=0.3)
if data_type == "RTO6":
	E_lims[0] = min(X)
plt.xlim(left=E_lims[0], right=E_lims[1])

plt.title(calib_title)
plt.xlabel(r'$E$ [keV]')
plt.ylabel(r'$I/I_{max}$')

plt.yscale(value='log')
plt.legend(loc="lower left", ncols=2)
if data_type[data_folder] == "RTO6":
	if calibration["peak_dict"]["Cs137"]["31 keV"]["fit?"]:
		plt.savefig("../figures/"+data_folder+"Calibrated_spectrum_low_peaks.pdf", bbox_inches="tight")
	else:
		plt.savefig("../figures/"+data_folder+"Calibrated_spectrum.pdf", bbox_inches="tight")
else:
	plt.savefig("../figures/"+data_folder+"Calibrated_spectrum.pdf", bbox_inches="tight")

#----------fitting FWHM vs E----------#

params = calibration["FWHM_vs_E"]["fit_init"] #y = s0+s1*sqrt(x)
result = fitting.Fit_sqrt(x=energies, y=FWHM_values, parameters=params)

s0 = result.params['s0'].value
s1 = result.params['s1'].value
s0_err = result.params['s0'].stderr
s1_err = result.params['s1'].stderr

calibration["FWHM_vs_E"]["fit_init"] = params #save calibration data
calibration["FWHM_vs_E"]["s0"] = [s0, s0_err]
calibration["FWHM_vs_E"]["s1"] = [s1, s1_err]
calibration["FWHM_vs_E"]["chi2"] = result.chisqr

print(result.fit_report())

#---------------plot calibration-----------#

plt.figure(2)

#Energy domain
Xplot = np.arange(0, max(energies), 1)
Yplot = np.array([s0 + s1*np.sqrt(x) for x in Xplot])

#data
plt.errorbar(energies, FWHM_values, yerr=FWHM_errs, fmt='o', ms=3)

#fit
s0_inc = my_uncertainty(s0, s0_err)
s0_str = r'FWHM $=~$'+s0_inc[0]+"("+s0_inc[1]+") [keV]"
s1_inc = my_uncertainty(s1, s1_err)
s1_str = r' $+$ '+s1_inc[0]+"("+s1_inc[1]+s1_units
plt.plot(Xplot, Yplot, '-', label=s0_str+s1_str)

plt.scatter(energies, FWHM_values)

plt.title(calib_title)
plt.xlabel(r'$E$ [keV]')
plt.ylabel(r'FWHM [keV]')

plt.grid()

plt.legend(loc="upper left")
if data_type[data_folder] == "RTO6":
	if calibration["peak_dict"]["Cs137"]["31 keV"]["fit?"]:
		plt.savefig("../figures/"+data_folder+"FWHM_low_peaks.pdf", bbox_inches="tight")
	else:
		plt.savefig("../figures/"+data_folder+"FWHM.pdf", bbox_inches="tight")
else:
	plt.savefig("../figures/"+data_folder+"FWHM.pdf", bbox_inches="tight")

#save calibration data
with open("../data/"+data_folder+spectra_folder+"calibration.json", "w") as outfile: 
    json.dump(calibration, outfile, indent=4)