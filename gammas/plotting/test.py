import json 

with open("../data/Ba133-october-12-2023/calibration.json", "r") as infile:
    calibration = json.load(infile)

# Data to be written 
'''dictionary = {
    "prefixes" : ["Ba133"],
    "prefix_bkgd" : "bkgd",
    "params_dict" : {"Ba133": [[100, 0, 1000, 2, 1]]},
    "range_dict" : {"Ba133": [[0, 2.5]]},
    "peak_dict" : {"Ba133": ["31 keV"]},
    "gauss_centers" : {"Ba133": []},
	"gauss_centers_err" : {"Ba133": []}
}'''

dictionary = {
    "prefixes" : ["Ba133"],
    "prefix_bkgd" : "bkgd",
    "peak_dict" : {"Ba133": {	"31 keV": {"range": [0, 3], "fit_init": [0, 0, 1, 1.87, 1], "fit_results": None},
    							"81 keV": {"range": [3, 7], "fit_init": [0.1, -1, 0.18, 6, 1], "fit_results": None}}},
}

with open("../data/Ba133-october-12-2023/calibration.json", "w") as outfile: 
    json.dump(dictionary, outfile, indent=4)

with open("test.json", "r") as infile: 
    calibration = json.load(infile)

prefix = "Ba133"
peak = "31 keV"
print(calibration["peak_dict"][prefix][peak]["fit_init"])