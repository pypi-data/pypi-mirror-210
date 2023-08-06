# astromulti

This is a collection of modules for complementing AstroPy in astronomy analysis

# 

`fits_actions`: various analysis/modification routines for FITS images

* `remove_axes_34`: removes degenerate 3rd and 4th axes

* `bg_filter_I`: filter out background emission using 'un-sharp masking' method developed by Sofue & Reich (1979)

* `bg_filter_QU`: modified version of bg_filter_I to work for polarization data as well (-ve values)

* `convert_to_JyPerBeam`: convert a FITS file to Jy/beam units (original units in Kelvin)

* `regioncut`: get a cutout of a region

* `TTdata`: get pixel values of two FITS files with same WCS (for temperature-temperature plots)

* `measure_FD`: measure flux density of a region in a fits file

* `smooth_fits`: convolve a FITS image to a larger beam size

* `smooth_fits_to_commonbeam`: convolve two FITS images to a common beam size

* `gauss2Dfit_fits`: perform 2D Gaussian fitting on a point source

`linear_fitting`: do least squares fitting to get a line or a plane

`new_colormap`: make a new colormap that can be used in plotting data

`region_meta`: meta details of a region

`simple_funcs`: a collection of simple functions


As the license states, no liability will be accepted.  Whatever tests I ran are on Linux, and for my own use case.

