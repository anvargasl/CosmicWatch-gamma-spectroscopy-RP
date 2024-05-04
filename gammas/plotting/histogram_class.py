import numpy as np

class Histogram(object):

	def __init__(self, name=None, bin_size=None, bin_edges=np.empty([1,1]), freq=np.empty([1,1]), f_name=None):
		if f_name == None:
			self.name = name
			self.bin_centers = 0.5*(bin_edges[:-1] + bin_edges[1:])
			self.nbins = len(self.bin_centers)
			self.bin_size = bin_size
			self.freq = freq
			self.norm_freq = None
			self.fmax = None
			#self.mean = None
			#self.sigma = None
			self.norm_value = None #value used to normalize the histogram

			#errors of each value
			self.freq_err = None
			self.norm_freq_err = None
			self.fmax_err = None
			#self.mean_err = None
			#self.sigma_err = None
			self.norm_value_err = None
		elif isinstance(f_name, str):
			print('reading stuff')
			self.read_hist(f_name)

	'''def getMean(self):
		#total events recorded
		total_events = sum(self.freq)

		#bin center * it's frecuency
		rel_freq = sum(f*c for f, c in zip(self.freq, self.bin_centers))

		self.mean = round(rel_freq/total_events, 2)

	def getSigma(self):
		if self.mean is None:
			self.getMean()

		#sum of deviations from the mean
		differences = sum((c-self.mean)**2 for c in self.bin_centers)

		self.sigma = round(np.sqrt(differences/self.nbins), 2)'''

	def normalize(self, norm_value=None, norm_value_err=None):
		if self.norm_freq is not None:
			print("Already normalized")

		self.fmax = max(self.freq)

		if norm_value is None:
			self.norm_freq = self.freq/self.fmax
			self.norm_value = self.fmax
		else:
			self.norm_freq = self.freq/norm_value
			self.norm_value = norm_value
			self.norm_value_err = norm_value_err

	def getErrors(self):
		if self.norm_freq is None:
			self.normalize()

		#relative error at fmax bin
		self.fmax_err = np.sqrt(self.fmax)

		#relative error at each bin
		self.freq_err = [np.sqrt(f) if f>0 else 0 for f in self.freq]

		#frequencies error in the normalized histogram
		self.norm_freq_err = [0]*self.nbins
		dN2 = (self.norm_value_err/self.norm_value)**2
		for j in range(self.nbins):
			if self.freq_err[j] != 0:
				df = self.freq_err[j]/self.freq[j]
				self.norm_freq_err[j] = self.norm_freq[j]*np.sqrt(df**2 + dN2)

		#self.mean_err = round(self.sigma/np.sqrt(self.nbins), 2)

	def print_hist(self, f_name=None):
		parameters = [str(self.name), str(self.bin_size), str(self.fmax), str(self.fmax_err), str(self.norm_value), str(self.norm_value_err)]
		
		values_label = "name, dx, fmax, fmax_err, norm_value, norm_vale_err\n"
		values = " ".join(str(p) for p in parameters)+"\n"
		columns_label = "bin_center, freq, freq_err, norm_freq, norm_freq_err"
		header = values_label+values+columns_label

		data = np.array([self.bin_centers, self.freq, self.freq_err, self.norm_freq, self.norm_freq_err]).T

		np.savetxt(f_name, data, fmt=f' '.join(['%f']+['%d']+['%f']*3), header=header)

	def read_hist(self, f_name=None):

		print('reading stuff indeed')

		#read spectra and uncertainties
		self.bin_centers, self.freq, self.freq_err, self.norm_freq, self.norm_freq_err = np.genfromtxt(f_name, dtype=None, unpack=True)
		
		#read parameters
		stuff = None
		with open(f_name, 'r') as f_handle:
			for i, line in enumerate(f_handle):
				if i == 0:
					stuff = f_handle.readline()[2:].split()

		self.nbins = len(self.bin_centers)
		self.name = stuff[0]
		self.bin_size = int(stuff[1])
		self.fmax, self.norm_value = [int(s) for s in (stuff[2], stuff[4])]
		self.fmax_err, self.norm_value_err = [float(s) for s in (stuff[3], stuff[5])]