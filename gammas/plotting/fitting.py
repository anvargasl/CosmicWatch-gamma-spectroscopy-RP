import matplotlib.pyplot as plt
import numpy as np
from lmfit import Model

def Gauss_plus_bkgd(x, a0, a1, I0, mu, sigma):
	return (a0+a1*x)+(I0*np.exp(-0.5*((x-mu)/sigma)**2))

#x = np.arange(0, 100, 1)
#y = Gaussian_Background(x, 2, -0.1, 10, 50, 8)

gaussModel = Model(Gauss_plus_bkgd)
gaussParams = gaussModel.make_params()

def Fit_Gauss_plus_bkgd(x, y, parameters):

	gaussParams.add('a0', value=parameters[0], vary=True)
	gaussParams.add('a1', value=parameters[1], vary=True)
	gaussParams.add('I0', value=parameters[2], vary=True)
	gaussParams.add('mu', value=parameters[3], vary=True)
	gaussParams.add('sigma', value=parameters[4], vary=True)

	return gaussModel.fit(y, x=x, params=gaussParams)

	#print(f'parameter names: {gaussModel.param_names}')
	#print(f'independent variables: {gaussModel.independent_vars}')

def Line(x, a0, a1):
	return a0+a1*x
	
lineModel = Model(Line)
lineParams = lineModel.make_params()

def Fit_Line(x, y, parameters=None):
	if parameters!=None:
		lineParams.add('a0', value=parameters[0], vary=True)
		lineParams.add('a1', value=parameters[1], vary=True)

	return lineModel.fit(y, x=x, params=lineParams)

def square_root(x, s0, s1):
	return s0 + s1*np.sqrt(x)

sqrtModel = Model(square_root)
sqrtParams = sqrtModel.make_params()

def Fit_sqrt(x, y, parameters=None):
	if parameters!=None:
		sqrtParams.add('s0', value=parameters[0], vary=True)
		sqrtParams.add('s1', value=parameters[1], vary=True)

	return sqrtModel.fit(y, x=x, params=sqrtParams)

'''print(result.fit_report())
print(result.params)
print(result.params['I0'].value)
print(result.params['I0'].stderr)

plt.plot(x, y)
plt.plot(x, result.init_fit, '--', label='initial fit')
plt.plot(x, result.best_fit, '-', label='best fit')
plt.legend()
plt.show()'''