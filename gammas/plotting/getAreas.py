import matplotlib as mpl

fsize = 22
mpl.rcParams['legend.fontsize'] = fsize
mpl.rcParams["figure.figsize"] = (6,5)
mpl.rcParams['axes.labelsize'] = fsize
mpl.rcParams['xtick.labelsize'] = fsize
mpl.rcParams['ytick.labelsize'] = fsize
mpl.rcParams['text.usetex'] = True
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['mathtext.fontset'] = 'dejavusans'
mpl.rcParams.update({'font.size': fsize})

import random as rand
import numpy as np
import matplotlib.pyplot as plt

#add RTxReadBin installation path
import sys
sys.path.insert(0, r"/home/andres/.local/lib/python3.8/site-packages/src/")

from RTxReadBin import RTxReadBin

#read setup.txt
with open('setup.txt', 'r') as fsetup:
	lines = fsetup.readlines()
	for line in lines:
		line.strip()

	#file to be read
	prefix = lines[0][lines[0].find(':')+1:].strip()
	#number of acquisitions to read per iteration
	dw = int(lines[1][lines[1].find(':')+1:])
	#number of times to read dw acquisitions
	tot_iterations = int(lines[2][lines[2].find(':')+1:])

print('reading:', prefix)

tot_data = dw*tot_iterations #final number of Acquisitions to be read

first = 0 #first acquisition to read
last = first+dw+1 #last acquisition to read

amplitudes = None
areas = None

action = input('get [area/amplitude/both]?:')
if action=='amplitude' or action=='both':
	amplitudes = np.zeros(tot_data, dtype=float)
	#Acquisition id to use for ploting later
	plot_id = rand.randint(0, tot_data-1)
	plot_data = list()
	plot_amp = None
if action=='area' or action=='both':
	areas = np.zeros(tot_data)
	#plot_test_id = None
	#plot_test_data = list()
	#plot_test_area = None
	#plot_test_found = 0
else:
	print('valid options are: area, amplitude or both')
	quit()

#read saved signal start points and offset average
starts = np.genfromtxt('../data/Waveform_histories/Waveform_data/'+prefix+'-startPoints.txt', dtype=int, skip_header=1)
averages = np.genfromtxt('../data/Waveform_histories/Waveform_data/'+prefix+'-averages.txt', dtype=float, skip_header=1)

for i in range(tot_iterations):
	y, x, S, nNofAvailableAcq = RTxReadBin('../data/Waveform_histories/'+prefix+'-history.Wfm.bin', acquisitions=[first,last])

	x = x #time measuted in micro seconds

	resolution = S['Resolution']

	idxmin = int(((-0.2e-6)-x[0])/resolution)
	idxmax = int(((-0.1e-6)-x[0])/resolution)

	tot_Aq = len(y[0]) #number of Acquisitions read
	dataLen = len(y) #number of points per Acquisition

	if i == 0:
		print(dataLen, 'points per Acquisition')
		print(resolution, '[s] resolution')
		
	print(tot_Aq*(i+1), 'Acquisition(s) read')

	sample_size = dataLen-idxmin
	dataY = np.zeros((tot_Aq, sample_size))

	dataY = np.swapaxes(y,0,2)[0]

	
	for wdx, waveform in enumerate(dataY):
		Aq_id = (i*tot_Aq)+wdx
		start = starts[Aq_id]
		if start==0:
			continue
		avrg = averages[Aq_id]

		if action=='amplitude' or action=='both':
			amplitudes[Aq_id] = max(waveform[start:])

			if Aq_id == plot_id:
				plot_data = waveform
				plot_amp = amplitudes[Aq_id]

		if action=='area' or action=='both':
			heights_sum = sum(waveform[start:]-avrg)
			#areas[Aq_id] = resolution*(heights_sum-sample_size*avrg)
			area = resolution*heights_sum
			areas[Aq_id] = area
			'''if 0.49e-7 < area and area < 0.51e-7 and plot_test_found < 1000:
				plot_test_id = Aq_id
				plot_test_data.append(waveform[idxmin:])
				plot_test_area = area
				plot_test_found += 1'''
		else:
			print('?')

	first = last-1
	last = first+dw+1

if action=='amplitude' or action=='both':
	np.savetxt('../data/Waveform_histories/Waveform_data/'+prefix+'-amplitudes.txt', amplitudes, delimiter=',', header='V')

	#plot one random waveform
	plt.plot(x[idxmin:]*1e6, plot_data[idxmin:]*1e3)
	plt.axvline(x=x[starts[plot_id]]*1e6, linestyle='--', label='Pulse Start')
	plt.axhline(y=averages[plot_id]*1e3, linestyle='--', label='Offset average', color='orange')
	plt.axhline(y=plot_amp*1e3, linestyle='--', label='Pulse max', color='green')

	plt.grid()
	plt.title('Pulse Start for Acquisition No '+str(plot_id))
	plt.xlabel(r'Time [$\mu$s]')
	plt.ylabel(r'SiPM Voltage [mV]')

	plt.legend()
	plt.savefig('../figures/Random_Signals/'+prefix+'-RandomSignal.pdf', bbox_inches="tight")

if action=='area' or action=='both':
	np.savetxt('../data/Waveform_histories/Waveform_data/'+prefix+'-areas.txt', areas, delimiter=',', header='Vs')
	
	'''#plot one test waveform
	tot_tests = len(plot_test_data)
	print(tot_tests)

	plot_test_list = rand.sample(range(tot_tests), 10)
	print(plot_test_list)

	for test in plot_test_list:
		plt.plot(x[idxmin:]*1e6, plot_test_data[test]*1e3)
	#plt.axvline(x=x[starts[plot_test_id]]*1e6, linestyle='--', label='Pulse Start')
	#plt.axhline(y=averages[plot_test_id]*1e3, linestyle='--', label='Offset average', color='orange')
	#plt.axhline(y=amplitudes[plot_test_id]*1e3, linestyle='--', label='Pulse max', color='green')

	plt.grid()
	plt.title('Pulse test, Aq No '+str(plot_test_id)+', Area '+str(plot_test_area))
	plt.xlabel(r'Time [$\mu$s]')
	plt.ylabel(r'SiPM Voltage [mV]')

	plt.legend()
	plt.savefig('../figures/'+prefix+'-TestSignal.pdf', bbox_inches="tight")'''
else:
	print('??')
