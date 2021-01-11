import HSI
import numpy as np
from scipy.signal import find_peaks, peak_prominences, peak_widths, savgol_filter
import scipy.stats
from sklearn import preprocessing
import spectral
from time import perf_counter as pfc
import matplotlib.pyplot as plt
from PIL import Image
import load_sample_spectra
import random
import cv2

# # Pearson tests
# # Creating linspaces
# ls = np.linspace(0, 1, 10)
# ls_long = np.linspace(0, 150, 10)
# print(ls)
# # Creating example spectrum
# s = np.array([22, 23, 24, 25, 26, 26.7, 27.4, 28, 29, 30])
# pearsons_r = scipy.stats.pearsonr(ls, s)
# print(pearsons_r)
# pearsons_r = scipy.stats.pearsonr(ls_long, s)
# print(pearsons_r)

fname = '/media/findux/DATA/HSI_Data/imec_sample data/sample_data_pills_and_leaf.hdr'
fname_mask = '/media/findux/DATA/HSI_Data/imec_sample data/sample_data_pills_and_leaf_MASK.png'

hdr = spectral.open_image(fname)
wlv = np.array(hdr.bands.centers)
print(type(wlv))
print(wlv.shape)
mask = HSI.BinaryMask(fname_mask, 'In')

# img_rgb = spectral.get_rgb(hdr)
# plt.imshow(img_rgb)
# plt.show()

# Grab one spectrum
leaf = hdr[1653, 929, :]
print(type(leaf))
leaf = HSI.unfold_cube(leaf)
print(type(leaf))
print(leaf.shape)
spct_leaf = HSI.Spectra(leaf, wlv)
spct_leaf.plot()

a = HSI.TriangleDescriptor(133, 160, 201, 'Test')
b = a
print(b)



print('EOF')