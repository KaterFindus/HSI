#!/usr/bin/env python3
import spectral
import numpy as np
import scipy.stats
import matplotlib.pyplot as plt
import math
import random
from typing import Union  # So multiple types can be specified in function annotations


# ToDo: Think about what to do when using different WLVs for different samples.
#       would dictionaries be too slow?
#       This is actually the case with Josef's reference spectra.


def load_hsi(fpath: str) -> 'hdr, img, wlv':
    """hdr, img, wlv = hsi_import(fpath)\n\n
    Takes path to a header (.hdr) hsi file and returns
    header file, hypercube array and wavelength vector (WLV)
    (aka wavenumbers).
    WLV is retrieved from the centers of bands.
    :rtype: .hdr, np.array, np.array
    """
    hdr = spectral.open_image(fpath)
    img_cube = hdr.load()
    wlv = np.array(hdr.bands.centers)
    return hdr, img_cube, wlv

# def preprocessing(spectra: Spectra):
#
#     pass
#     # ToDo: normalisation, mean centering


def find_peaks(spectrum: np.array, wlv: np.array):
    pass


class Spectra:
    """2D np.array containing a set of spectra.
    """
    def __init__(self, intensities: np.array, wlv: np.array, material_column: list = None):
        self.wlv = wlv
        self.intensities = intensities
        self.material_column = material_column

    def random_subsample(self, n=250, seed=42):
        subset_index = random.choices(range(self.intensities.shape[0]), k=n) # ToDo: Incorporate seed
        return Spectra(self.intensities[subset_index], self.wlv, self.material_column)

    def export_npz(self, savename):
        np.savez(savename, self.intensities, self.wlv)

    def plot(self):
        x = self.wlv
        y = self.intensities
        plt.plot(x, y.T)
        plt.show()


def unfold_cube(cube):  # Rename to unfold cube?
    """spectra = spectra_from_cube(cube)\n\n
    Unfolds a hypercube of the dimensions (x, y, z) into a 2D array
    of the dimensions (x * y, z) containing the spectra for each pixel.
    """
    _cubearray = np.array(cube)
    _x, _y, _spec = _cubearray.shape
    spectra = _cubearray.reshape((_x * _y, _spec))
    return spectra


def random_spectrum(spectra):  # Can be replaced by "Spectra.random_subsample(n=1)
    pass


class BinaryMask:
    """
    Binary mask object with the following attributes:
    .mask_2D        binary 2D array
    .full_vector    unfolded mask (with 0 for out-, 1 for in-values)
    .index_vector   unfolded mask vector containing indices for in-values
    .material       Material string
    """
    def __init__(self, img_path: str, material: str):
        _mask = plt.imread(img_path)[:, :, 0]
        # Crank everything above 50% intensity up to 100%:
        _mask = np.where(_mask > 0.5, 1, 0)
        _x, _y = _mask.shape
        self.mask_2D = _mask
        self.full_vector = _mask.reshape((_x * _y))  # Unfold
        self.index_vector = np.where(self.full_vector == 1)[0]  # Locate only "in" values
        self.material = material

class MulticlassMask:
    # ToDo: Combine binary masks, material = mask fname.
    pass


def mask_spectra(spectra: Spectra, mask: BinaryMask):
    pass


class TriangleDescriptor:
    """ToDo: Break this up.

    Takes a start wavelength, peak wavelengths and stop wavelength, as well
    as a WavelengthVector object as input.
    """
    def __init__(self, material_name: str,
                 wl_start: Union[int, float],
                 wl_peak: Union[int, float],
                 wl_stop: Union[int, float],
                 wlv: np.array):
        self.material_name = material_name
        # Wavelength values validation
        if not wl_start < wl_peak < wl_stop:
            raise ValueError('Invalid wavelengths input.\n'
                             'Are they float or int?\n'
                             'Are they in order START, PEAK, STOP?')
        # Wavelength attributes for start, peak and stop
        self.start_wl = wl_start
        self.peak_wl = wl_peak
        self.stop_wl = wl_stop
        # Initiate index attributes
        self.start_bin_index = None
        self.peak_bin_index = None
        self.stop_bin_index = None
        # Initiate Pearson Correlation Coefficients
        self.pearsons_r_asc = tuple()
        self.pearsons_r_desc = tuple()
        self.pearsons_r_avg = (self.pearsons_r_asc[0] + self.pearsons_r_desc[0]) / 2

    def compare_to_spectrum(self, spectrum, wlv: np.array):  # ToDo: Maybe separate this into its own function
        """
        Takes a Spectrum as input and then compares how well it is matched by the descriptors.
        ToDo: The actual comparison.
        :param spectrum:
        :param wlv:
        :return:
        """
        # Account for values outside of wlv range:
        assert min(wlv) < self.peak_wl < max(wlv)
        if self.start_wl <= min(wlv): self.start_wl = min(wlv)
        if self.stop_wl >= max(wlv): self.stop_wl = max(wlv)

        # Get bin indices
        self.start_bin_index = np.argmin(np.abs(wlv - self.start_wl))
        self.peak_bin_index = np.argmin(np.abs(wlv - self.start_wl))
        self.stop_bin_index = np.argmin(np.abs(wlv - self.start_wl))

        # Create linspaces
        before_peak = int(self.peak_bin_index - self.start_bin_index)
        after_peak = int(self.stop_bin_index - self.peak_bin_index)
        asc_linspace = np.linspace(0, 1, before_peak)
        desc_linspace = np.linspace(1, 0, after_peak)
        # print(asc_linspace)
        # print(desc_linspace)

        # Calculate Pearson's Correlation Coefficient (r):
        self.pearsons_r_asc = scipy.stats.pearsonr(spectrum[self.start_bin_index:self.peak_bin_index + 1], asc_linspace)
        self.pearsons_r_desc = scipy.stats.pearsonr(spectrum[self.peak_bin_index:self.stop_bin_index + 1], asc_linspace)
        return self.pearsons_r_avg

    # Output when print() is run on the descriptor:
    def __str__(self):
        return 'HSI.TriangleDescriptor: {0} (start, peak, stop)'\
            .format((self.start_wl, self.peak_wl, self.stop_wl))

    def __get__(self):
        return tuple(self.start_wl, self.peak_wl, self.stop_wl)


def pearson_corr_coeff(descriptors, samples):
    # read wlv only once
    pass


class reference_spectra:
    def __init__(self):
        pass