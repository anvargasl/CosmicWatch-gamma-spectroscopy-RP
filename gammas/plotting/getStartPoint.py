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

#bkgd: 43239/3=14413
#10005-151=9854
#Na22: 9854/13=758
#Na22-1: 83885/5=16777
#Cs137: 83885/5=16777
#Co60: 83885/5=16777
#bgkd1: 83885/5=16777
#Na22-live: 112378/7=16054
#Cs137-live: 199410/10=19941
#Co60-live: 82580/5=16516
#Ba133-live: (217111-1)/10=21711
#Mn54-live:	29547/3=9849
#bgkd-live: 27270/2=13635
#full-live: 209378/13=16106
#test: 406

#read setup.txt
with open('setup.txt', 'r') as fsetup:
	lines = fsetup.readlines()
	for line in lines:
		line.strip()

	#file to be read
	prefix = lines[0][lines[0].find(':')+1:].strip()
	#number of acquisitions to read per iteration
	dw = int(lines[1][lines[1].find(':')+1:])
	#number of times to read dw Acquisitions
	tot_iterations = int(lines[2][lines[2].find(':')+1:])

print('reading:', prefix)

tot_data = dw*tot_iterations #final number of Acquisitions to be read

first = 0 #first acquisition to read
last = first+dw+1 #last acquisition to read

starts = np.zeros(tot_data, dtype=int)
averages = np.zeros(tot_data, dtype=float)

#random Acquisition id to use for ploting later
plot_id = rand.randint(0, tot_data-1)
plot_data = list()

for i in range(tot_iterations):

	y, x, S, nNofAvailableAcq = RTxReadBin('../data/Waveform_histories/'+prefix+'-history.Wfm.bin', acquisitions=[first,last])

	#print('Available Acquisitions =', nNofAvailableAcq)

	x = x #time measuted in micro seconds

	resolution = S['Resolution']

	idxmin = int(((-0.2e-6)-x[0])/resolution)
	idxmid = int(((-0.1e-6)-x[0])/resolution)
	idxmax = int(((0.1e-6)-x[0])/resolution)

	tot_Aq = len(y[0]) #number of Acquisitions read
	dataLen = len(x) #number of points per Acquisition

	if i == 0:
		print(dataLen, 'points per Acquisition')
		print(resolution, '[s] resolution')

	print(tot_Aq*(i+1), 'Acquisition(s) read')

	#rearrange data
	'''for wdx in range(tot_Aq):
		for idx in range(idxmin, idxmax):
			dataY[wdx][idx-idxmin] = y[idx][wdx][0]'''
	dataY = np.swapaxes(y,0,2)[0]

	avrg_range = idxmid-idxmin

	for wdx, waveform in enumerate(dataY):
		#Acquisiton number
		Aq_id = (i*tot_Aq)+wdx

		#Get offset average
		averages[Aq_id] = sum(waveform[idxmin:idxmid])/avrg_range
		avrg = averages[Aq_id]

		#Find pulse start
		for idx in range(idxmid, idxmax, 5):
			#dataLen/100 seems to be a good resolution to find the pulse start
			dx = int(dataLen/100)

			if all(v > avrg for v in waveform[idx:idx+dx]):
				starts[Aq_id] = idx
				if Aq_id == plot_id:
					plot_data = waveform
				break

	first = last-1
	last = first+dw+1

np.savetxt('../data/Waveform_data/'+prefix+'-startPoints.txt', starts, fmt='%d', header='index')
np.savetxt('../data/Waveform_data/'+prefix+'-averages.txt', averages, fmt='%f', header='V')

#np.savetxt('../data/Waveform_data/'+prefix+'-raw.txt', plot_data, header='V')

#plot one random waveform
plt.plot(x[idxmin:]*1e6, plot_data[idxmin:]*1e3)
plt.axvline(x=x[starts[plot_id]]*1e6, linestyle='--', label='Pulse Start')
plt.axhline(y=averages[plot_id]*1e3, linestyle='--', label='Offset average', color='orange')

plt.grid()
plt.title('Pulse Start for Acquisition No '+str(plot_id))
plt.xlabel(r'Time [$\mu$s]')
plt.ylabel(r'SiPM Voltage [mV]')

plt.legend()
plt.savefig('../figures/Random_Signals/'+prefix+'-RandomSignal.pdf', bbox_inches="tight")
