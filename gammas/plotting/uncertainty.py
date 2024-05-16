import re

def my_uncertainty(a, a_std):
    a_exp = int(re.search(r'e([-+]?\d+)', "{:.2e}".format(a_std))[1])
    a_rd = 0

    if a_exp<0:
        a_rd = round(a, -a_exp)
    elif a_exp>0:
        a_rd = int(round(a, -a_exp))
    else:
        a_rd = round(a)

    if 0 < a_std < 10:
        a_std_rd = round(a_std*10**(-a_exp))
    elif a_std > 10:
        a_std_rd = round(a_std)

    return str(a_rd), str(a_std_rd)