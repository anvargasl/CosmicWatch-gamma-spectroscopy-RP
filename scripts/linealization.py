import numpy as np

#X=lista de abscisas, Y=lista de ordenadas, S=incertidumbre de Y
def adjust(X, Y, S):
	dim = len(X)
	s = 0
	sx = 0
	sy = 0
	sxx = 0
	sxy = 0

	for i in range(dim): 
		s += 1/(S[i])**2
		sx += X[i]/(S[i])**2
		sy += Y[i]/(S[i])**2
		sxx += (X[i]/S[i])**2
		sxy += X[i]*Y[i]/(S[i])**2
	det = s*sxx - sx**2

	a0 = (sxx*sy - sx*sxy)/det
	a1 = (s*sxy - sx*sy)/det

	err_a0 = np.sqrt(sxx/det)
	err_a1 = np.sqrt(s/det)

	chi2 = 0
	for i in range(dim):
		chi2 += ((Y[i]-(a0+a1*X[i]))/S[i])**2

	print('f(x)=',round(a0,2),'+',str(round(a1,2))+'x')
	print('chi2:',round(chi2,2))
	print('d(a0):', round(err_a0,2))
	print('d(a1):', round(err_a1,2),'\n')

	return [a0, a1, err_a0, err_a1, chi2]