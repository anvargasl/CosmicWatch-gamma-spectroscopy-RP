# Data acquisition

There are two main ways to obtain data from the Rohde&Schwarz RTO 6 Series oscilloscope in order to create the spectra [1.](#waveform-histories) Save the acquired waveforms history in a binary file and [2.](#direct-measurement) Meassure the area under each waveform directly in the oscilloscope. Each method requires different processing of the obtained data. This README aims to explain the beamline used in each case.

## Waveform histories

This method requires a large amount of data due to the fact that each acquisition is saved in the same binary file, which can get very heavy. We do not know the maximum number of aqcuisitions the oscilloscope can output. For example `Ba133-live-history.Wfm.bin` has the data of only 5 minutes of measutement and weights **8.7 GB** for 217111 acquisitions. This is not good unless really detailed processing of the waveforms needs to be implemented; however, as we have found, the oscilloscope gives very accurate measurements when it commes to pulse area which, is the focuse of this project, we suggest then the approach mentioned in [Direct Measurement](#direct-measurement) section.

### getStartPoint.py

Get the start point and DC offset average for every acquisition from a `history.bin` file obtained from the oscilloscope. This program will also save a plot under `figures/Random_Signals` of a randomly chosen acquisition to show that the waveform start and DC offset level are being calculated correctly.

### getAreas.py

Uses the start point and DC offset average data obtained with **getStartPoint.py** to measure the amplitude and area of each acquisition. This information is saved under the `Waveform_data` folder.

### createSpectra.py

Reads the amplitud and area information created with **getAreas.py** and creates a `Histogram` object to save the spectra under the `spectra` folder.

## Direct measurement

### oscilloscope.py

Reads histograms outputted by RTO 6 Series oscilloscope and saves it in a `Histogram` object again under the `spectra` folder to be processed by **fit_plot_Spectra.py**

# Processing

Once the spectra is constructed we need to calibrate the channels to their corresponding energy values.

### fit_plot_Spectra.py

Use the spectra created by **createSpectra.py** or **oscilloscope.py** to fit gaussians for the peaks specified in **calibration.json**, this will also create an Intensity-vs-cannel (SiPM pulse area) plot.

### calibration.py

Use the obtained centroids from **fit_plot_Spectra.py** to get the channel-energy calibration and create an Intensity-vs-Energy plot.

## Modules

### histogram_class.py

`Histogram` class designed to contain all the information and functions necessary to create a normalized spectrum with its respective error in counts. 

Each histogram object requires a `name` string, `bin_size` resolution, `bin_edges` list including the left and right most edges of the first and last bins respectively, and the `freq` corresponding to each bin. This parametes can also be omitted and just specify the name `f_name` of the file where the histogram was last saved using the **print_hist()** function.

**normalize()** can take two optional parameters: `norm_value` and `norm_value_err`, each frequency value in the original spectrum is divided by `norm_value`. When `norm_value` is not specified the maximum frequency on the spectrum is calculated and used to normalize.

**getErrors()** calculates the error of each suitable atribute of the histogram object, including for example the error in frequency *f* at each bean as *sqrt(f)*.

**print_hist()** and **read_hist()** save and read the original and normalized histogram with its respective errors in a file under the `spectra` folder.

### fitting.py

Contains the implementation of models for gaussian and linear functions as required by the [`lmfit`](https://pypi.org/project/lmfit/) library.

**Fit_Gauss_plus_bkgd()** models a gauss distrbution plus a straight line as background, it takes parameters `x` and `y` as the data to be fitted, and `parameters` as a list of initial values for the constants to be fitted by `lmfit`.

**Fit_Line()** models a straight line, taking also `x` and `y` as data to fit, and `parameters` as initial value constants.

## Specifying peaks to fit

**calibration.json** contains all the information that tells each program what isotopes, energies, and initial fitting values are going to be used. This is a short example of the sintax used.
```yaml
{
    "prefixes": [//list of isotopes meassured with the same oscilloscope setup
        "Ba133"
    ],
    "prefix_bkgd": "bkgd", //prefix of background file
    "peak_dict": { //dictionary containing peaks to be fitted arranged by isotope
        "Ba133": {
            "31 keV": {
                "range": [ //range on x axis to use for fitting
                    0,
                    3
                ],
                "fit_init": { //initial parameres required to fit a gaussian with background
                    "a0": 0.0005,
                    "a1": 0.02,
                    "I0": 0.9,
                    "mu": 1.88,
                    "sigma": 0.4
                },
                "fit_results": { //saved results from last fit performed [value, error]
                    "a0": [
                        -3.1623471965320507,
                        6.695604200475429
                    ],
                    "a1": [
                        0.9734801649789617,
                        1.7666916779765152
                    ],
                    "I0": [
                        3.2184676068361955,
                        6.030552305696506
                    ],
                    "mu": [
                        0.3945692982675226,
                        0.8968999035343789
                    ],
                    "sigma": [
                        1.2633135456894429,
                        0.9746543764488398
                    ]
                }
            },
            "81 keV": {
                "range": [
                    3,
                    7
                ],
                "fit_init": {
                    "a0": 0.1,
                    "a1": -0.006,
                    "I0": 0.16,
                    "mu": 5.53,
                    "sigma": 0.67
                },
                "fit_results": {
                    "a0": [
                        0.05776376372719058,
                        0.003470082520441964
                    ],
                    "a1": [
                        0.006252590133596302,
                        0.0010918180711283554
                    ],
                    "I0": [
                        -0.035075971507207385,
                        0.002782662203847789
                    ],
                    "mu": [
                        5.6811481641448065,
                        0.04170866282878926
                    ],
                    "sigma": [
                        0.8020298358108067,
                        0.058946600488754185
                    ]
                }
            }
        },
        "Na22": {
            "511 keV": {
                "range": [
                    30,
                    45
                ],
                "fit_init": {
                    "a0": 0.2,
                    "a1": -0.02,
                    "I0": 0.9,
                    "mu": 38,
                    "sigma": 2
                },
                "fit_results": {
                    "a0": [
                        0.055838422722464906,
                        0.0020541319951442537
                    ],
                    "a1": [
                        -0.0006218216296886716,
                        5.352061989187962e-05
                    ],
                    "I0": [
                        0.05705855677395226,
                        0.0006248304562552915
                    ],
                    "mu": [
                        37.252080172204636,
                        0.022678620884797374
                    ],
                    "sigma": [
                        1.8121899841766584,
                        0.02639944652910687
                    ]
                }
            },
            "1275 keV": {
                "range": [
                    78,
                    94
                ],
                "fit_init": {
                    "a0": 0,
                    "a1": 0,
                    "I0": 0.08,
                    "mu": 86,
                    "sigma": 1
                },
                "fit_results": {
                    "a0": [
                        0.012921186883907207,
                        0.0010381922591402905
                    ],
                    "a1": [
                        -0.00012039190358380087,
                        1.1911897421375227e-05
                    ],
                    "I0": [
                        0.003778158038515747,
                        0.00013265778486606334
                    ],
                    "mu": [
                        85.71599146947469,
                        0.09695077901222847
                    ],
                    "sigma": [
                        2.4289371222031857,
                        0.12215322017518654
                    ]
                }
            }
        }
    }
}
```
