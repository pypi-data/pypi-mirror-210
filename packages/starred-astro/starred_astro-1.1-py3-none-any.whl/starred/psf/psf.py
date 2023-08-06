import os
import dill as pkl
import warnings
from functools import partial

import jax.numpy as jnp
import numpy as np
from jax import jit, lax

from starred.utils.generic_utils import pad_and_convolve, pad_and_convolve_fft, fwhm2sigma, gaussian_function, \
    make_grid, \
    moffat_function, Downsample, scipy_convolve, save_npy, save_fits


class PSF(object):
    """
    Narrow Point Spread Function class. Coordinates and FWHM are given in the original pixel grid.
    
    """
    param_names_moffat = ['fwhm', 'beta', 'C']
    param_names_gaussian = ['a', 'x0', 'y0']
    param_names_background = ['background']

    def __init__(
            self,
            image_size=64,
            number_of_sources=2,
            upsampling_factor=2,
            gaussian_fwhm=2,
            convolution_method='fft',
            gaussian_kernel_size=None,
            include_moffat=True,
    ):
        """
        :param image_size: input images size in pixels
        :type image_size: int
        :param number_of_sources: amount of input images (each containing a point source)
        :type number_of_sources: int
        :param upsampling_factor: the rate at which the sampling frequency increases in the PSF with respect to the input images
        :type upsampling_factor: int
        :param gaussian_fwhm: the Gaussian's FWHM in pixels
        :type gaussian_fwhm: int
        :param convolution_method: method to use to calculate the convolution
        :type convolution_method: str
        :param gaussian_kernel_size: dimensions of the Gaussian kernel, not used if method = 'fft' (recommended)
        :type gaussian_kernel_size: int
        :param include_moffat: True for the PSF to be expressed as the sum of a Moffat and a grid of pixels. False to not include the Moffat.
        :type include_moffat: bool

        """
        self.image_size = image_size
        self.upsampling_factor = upsampling_factor
        self.image_size_up = self.image_size * self.upsampling_factor
        self.M = number_of_sources
        self.include_moffat = include_moffat

        if convolution_method == 'fft':
            self._convolve = pad_and_convolve_fft
            self.gaussian_size = self.image_size_up
            if (self.image_size * self.upsampling_factor) % 2 == 1:
                self.shift_gaussian = 0.
            else :
                self.shift_gaussian = 0.5 #convention for even kernel size and fft convolution
            self.shift_direction = 1.
        elif convolution_method == 'lax':
            self._convolve = pad_and_convolve
            if gaussian_kernel_size is None:
                self.gaussian_size = 12
            else:
                self.gaussian_size = gaussian_kernel_size
            self.shift_gaussian = 0.5
            self.shift_direction = 1.
        elif convolution_method == 'scipy':
            self._convolve = scipy_convolve
            if gaussian_kernel_size is None:
                self.gaussian_size = 64
            else:
                self.gaussian_size = gaussian_kernel_size
            warnings.warn("WARNING : jax.scipy has no FFT implementation for the moment. It might be faster to use 'fft' on CPU.")
            warnings.warn("WARNING : jax.scipy convolution has inverted shift convention for x0 and y0.")
            self.shift_gaussian = 0.5
            self.shift_direction = -1 #scipy has inverted shift convention
        else:
            raise NotImplementedError('Unknown convolution method : choose fft, scipy or lax')

        self.fwhm = gaussian_fwhm
        self.sigma = fwhm2sigma(self.fwhm)

    def shifted_gaussians(self, i, x0, y0):
        """
        Generates a 2D array with point sources. Normalized to 1.

        :param i: current point source index 
        :type i: int
        :param x0: 1D array containing the x positions of the point sources, shift are given in unit of 'big' pixels
        :param y0: 1D array containing the y positions of the point sources, shift are given in unit of 'big' pixels
        :return: 2D array

        """
        x, y = make_grid(numPix=self.gaussian_size, deltapix=1.)
        return jnp.array(gaussian_function(
            x=x, y=y,
            amp=1, sigma_x=self.sigma,
            sigma_y=self.sigma,
            center_x=-(self.upsampling_factor * x0[i])*self.shift_direction - self.shift_gaussian,
            center_y=-(self.upsampling_factor * y0[i])*self.shift_direction - self.shift_gaussian,  # Convention : gaussian is placed at a center of a pixel
        ).reshape(self.gaussian_size, self.gaussian_size))

    def analytic(self, fwhm, beta):
        """
        Generates the narrow PSF's analytic term.

        :param fwhm: the full width at half maximum value
        :type fwhm: float
        :param beta: the Moffat beta parameter
        :type beta: float

        :return: 2D Moffat

        """
        x, y = make_grid(numPix=self.image_size_up, deltapix=1.)
        return jnp.array(moffat_function(
            x=x, y=y,
            amp=1, fwhm=fwhm * self.upsampling_factor, beta=beta,
            center_x=0,
            center_y=-0,
        ).reshape(self.image_size_up, self.image_size_up))

    # @partial(jit, static_argnums=(0, 1, 5))
    def model(self, init=0, kwargs_moffat=None, kwargs_gaussian=None, kwargs_background=None, high_res=False):
        """
        Creates the 2D narrow Point Spread Function (PSF) image.
        
        :param init: stamp index 
        :type init: int
        :param kwargs_moffat: dictionary containing keyword arguments corresponding to the analytic term of the PSF
        :param kwargs_gaussian: dictionary containing keyword arguments corresponding to the Gaussian deconvolution kernel
        :param kwargs_background: dictionary containing keyword arguments corresponding to the grid of pixels
        :param high_res: returns the upsampled version of the PSF
        :type high_res: bool
        :return: array containing the model
        
        """

        s = self.get_narrow_psf(kwargs_moffat, kwargs_gaussian, kwargs_background, norm=False)
        r = self.get_gaussian(init, kwargs_gaussian)
        if high_res:
            model = self._convolve(s, r).reshape(self.image_size_up, self.image_size_up)
        else:
            model = Downsample(self._convolve(s, r).reshape(self.image_size_up, self.image_size_up),
                               factor=self.upsampling_factor)

        return model

    def get_moffat(self, kwargs_moffat, norm=True):
        """
        Returns the analytical part of the PSF.

        :param kwargs_moffat: dictionary containing keyword arguments corresponding to the analytic term of the PSF
        :param norm: normalizes the Moffat
        :type norm: bool

        """
        moff = kwargs_moffat['C'] * self.analytic(kwargs_moffat['fwhm'], kwargs_moffat['beta'])
        if norm:
            moff = moff / moff.sum()

        return moff

    def get_narrow_psf(self, kwargs_moffat=None, kwargs_gaussian=None, kwargs_background=None, norm=True):
        """
        Returns the `narrow` PSF s.

        :param kwargs_moffat: dictionary containing keyword arguments corresponding to the analytic term of the PSF
        :param kwargs_background: dictionary containing keyword arguments corresponding to the grid of pixels
        :return: array containing the `narrow` PSF
        """

        background = self.get_background(kwargs_background)
        if self.include_moffat:
            moff = kwargs_moffat['C'] * self.analytic(kwargs_moffat['fwhm'], kwargs_moffat['beta'])
            s = moff + background
        else:
            s = background
            moff = jnp.zeros_like(s)
            s += lax.cond(s.sum() == 0, lambda _: 1e-6, lambda _: 0., operand=None)  # to avoid division per 0

        if norm:
            s = s / s.sum()

        return s

    def get_full_psf(self, kwargs_moffat=None, kwargs_gaussian=None, kwargs_background=None, norm=True, high_res=True):
        """
        Returns the PSF of the original image, `i.e.`, the convolution between s, the `narrow` PSF, and r, the Gaussian kernel.

        :param kwargs_moffat: dictionary containing keyword arguments corresponding to the analytic term of the PSF
        :param kwargs_gaussian: dictionary containing keyword arguments corresponding to the Gaussian deconvolution kernel
        :param kwargs_background: dictionary containing keyword arguments corresponding to the grid of pixels
        :return: array containing the full PSF
        
        """
        s = self.get_narrow_psf(kwargs_moffat=kwargs_moffat, kwargs_gaussian=kwargs_gaussian, kwargs_background=kwargs_background, norm=norm)
        r = self.shifted_gaussians(0, [0.], [0.])
        if high_res:
            psf = self._convolve(s, r, False)
        else :
            psf = Downsample(self._convolve(s, r, False), factor=self.upsampling_factor)
        if norm:
            psf /= psf.sum()

        return psf

    def get_background(self, kwargs_background):
        """
        Returns the numerical part of the PSF.

        :param kwargs_background: dictionary containing keyword arguments corresponding to the grid of pixels
        :return: array containing the background correction
        """

        return kwargs_background['background'].reshape(self.image_size_up, self.image_size_up)

    def get_gaussian(self, init, kwargs_gaussian):
        """
        Returns a Gaussian function, adjusted to the star of index ``init``.

        :param init: stamp index
        :type init: int
        :param kwargs_gaussian: dictionary containing keyword arguments corresponding to the Gaussian deconvolution kernel
        :return: array containing the Gaussian kernel
        """
        x0, y0 = kwargs_gaussian['x0'], kwargs_gaussian['y0']
        r = self.shifted_gaussians(init, x0, y0)

        ga = kwargs_gaussian['a'][init] / jnp.mean(kwargs_gaussian['a']) #normalization by the mean to remove degeneracy with the C parameter of the moffat
        r = ga * r

        return r

    def get_amplitudes(self, kwargs_moffat=None, kwargs_gaussian=None, kwargs_background=None):
        """
        Returns the photometry of the stars.

        :param kwargs_moffat: dictionary containing keyword arguments corresponding to the analytic term of the PSF
        :param kwargs_gaussian: dictionary containing keyword arguments corresponding to the Gaussian deconvolution kernel
        :param kwargs_background: dictionary containing keyword arguments corresponding to the grid of pixels

        :return: list containing the relative photometry
       """

        kernel = self.get_narrow_psf(kwargs_moffat, kwargs_gaussian, kwargs_background, norm=False)
        kernel_norm = kernel.sum()
        amp = (kwargs_gaussian['a'] / jnp.mean(kwargs_gaussian['a'])) * kernel_norm
        return amp

    def get_photometry(self, kwargs_moffat=None, kwargs_gaussian=None, kwargs_background=None, high_res=False):
        """
        Returns the PSF photometry of all the stars.

        :param init: stamp index
        :type init: int
        :param kwargs_moffat: dictionary containing keyword arguments corresponding to the analytic term of the PSF
        :param kwargs_gaussian: dictionary containing keyword arguments corresponding to the Gaussian deconvolution kernel
        :param kwargs_background: dictionary containing keyword arguments corresponding to the grid of pixels
        :return: array containing the photometry
        """

        return jnp.array(
            [self.model(i, kwargs_moffat, kwargs_gaussian, kwargs_background, high_res).sum() for i in range(self.M)])

    def get_astrometry(self, kwargs_moffat=None, kwargs_gaussian=None, kwargs_background=None):
        """
        Returns the astrometry. In units of 'big' pixel.

        :param kwargs_moffat: dictionary containing keyword arguments corresponding to the analytic term of the PSF
        :param kwargs_gaussian: dictionary containing keyword arguments corresponding to the Gaussian deconvolution kernel
        :param kwargs_background: dictionary containing keyword arguments corresponding to the grid of pixels

        :return: list of tuples with format [(x1,y1), (x2,y2), ...]
        """
        coord = []
        for x, y in zip(kwargs_gaussian['x0'], kwargs_gaussian['y0']):
            coord.append([x, y])

        return np.asarray(coord)

    def export(self, output_folder, kwargs_final, data, sigma_2, format='fits'):
        """
        Saves all the output files.

        :param output_folder: path to the output folder
        :type output_folder: str
        :param kwargs_final: dictionary containing all keyword arguments
        :param data: array containing the images
        :param sigma_2: array containing the noise maps
        :param format: output format. Choose between ``npy`` or ``fits``
        :type format: str
        """
        if format == 'fits':
            save_fct = save_fits
        elif format == 'npy':
            save_fct = save_npy
        else:
            raise NotImplementedError(f'Format {format} unknown.')

        narrow = self.get_narrow_psf(**kwargs_final, norm=True)
        save_fct(narrow, os.path.join(output_folder, 'narrow_PSF'))

        full = self.get_full_psf(**kwargs_final, norm=True, high_res=True)
        save_fct(full, os.path.join(output_folder, 'full_PSF'))

        background = self.get_background(kwargs_final['kwargs_background'])
        save_fct(background, os.path.join(output_folder, 'background_PSF'))

        analytic = self.get_moffat(kwargs_final['kwargs_moffat'], norm=True)
        save_fct(analytic, os.path.join(output_folder, 'analytic_PSF'))

        for i in range(self.M):
            estimated_full_psf = self.model(i, **kwargs_final)
            dif = data[i, :, :] - estimated_full_psf
            rr = jnp.abs(dif) / jnp.sqrt(sigma_2[i, :, :])

            save_fct(estimated_full_psf, os.path.join(output_folder, f'full_psf_{i}'))
            save_fct(dif, os.path.join(output_folder, f'residuals_{i}'))
            save_fct(rr, os.path.join(output_folder, f'scaled_residuals_{i}'))

    def dump(self, path, kwargs, norm):
        """Stores information in a given file."""
        with open(path, 'wb') as f:
            pkl.dump([self, kwargs, norm], f)

    def smart_guess(self, data, fixed_background=True, guess_method = 'barycenter'):
        """
        Returns an initial guess of the kwargs, given the input data.

        :param data: array of shape (nimage, npix, npix) containing the input data
        :param fixed_background: fixes the background to 0
        :type fixed_background: bool
        :param guess_method: Method to guess the position of the point sources. Choose between 'barycenter' and 'max'
        :type guess_method: str

        :return: kwargs containing an initial guess of the parameters
        """

        initial_fwhm = 3.  # defined in pixel, this is a good enough guess
        initial_beta = 2.
        initial_background = jnp.zeros((self.image_size_up ** 2))

        # Positions (initialisation at the center of gravity)
        x0_est = np.zeros(self.M)
        y0_est = np.zeros(self.M)
        
        # need a grid of pixels for the center of gravity:
        X, Y = jnp.indices(data[0].shape)
        # we'll recenter the positions in the loop: 
        # ( -1 because coordinates start at 0)
        centerpos = (self.image_size - 1) / 2.

        if guess_method == 'barycenter':
            # calculate center of gravity for each epoch:
            for i in range(self.M):
                currentimage = data[i]
                # total weight of the image:
                partition = np.nansum(currentimage)
                # first moment: weight coordinates by image values
                x0 = np.nansum(X * currentimage) / partition
                y0 = np.nansum(Y * currentimage) / partition
                # x0 and y0 have their origin at top-left of image.
                x0_est[i] = y0 - centerpos
                y0_est[i] = x0 - centerpos #x and y needs to be inverted

        elif guess_method == 'max':
            # Positions (initialisation to the brightest pixel)
            x0_est = np.zeros(self.M)
            y0_est = np.zeros(self.M)
            for i in range(self.M):
                indices = np.where(data[i, :, :] == data[i, :, :].max())
                x0_est[i] = (indices[1] - self.image_size / 2.)
                y0_est[i] = (indices[0] - self.image_size / 2.) #x and y needs to be inverted
        else :
            raise ValueError('Guess methods unknown. PLease choose between "max" and "barycenter".')

        # Amplitude (use the total flux to scale the amplitude parameters)
        ratio = jnp.array([data[i].sum() / data[i].sum() for i in range(self.M)])
        initial_a = jnp.ones(self.M) * ratio
        kwargs_moffat_guess = {'fwhm': initial_fwhm, 'beta': initial_beta, 'C': 1.}
        flux_moffat = Downsample(self.get_moffat(kwargs_moffat_guess, norm=False), factor=self.upsampling_factor).sum()
        initial_C = float(data[0].sum() / flux_moffat)

        kwargs_init = {
            'kwargs_moffat': {'fwhm': initial_fwhm, 'beta': initial_beta, 'C': initial_C},
            'kwargs_gaussian': {'a': initial_a, 'x0': x0_est, 'y0': y0_est},
            'kwargs_background': {'background': initial_background},
        }

        kwargs_fixed = {
            'kwargs_moffat': {},
            'kwargs_gaussian': {},
            # 'kwargs_background': [{}],
            'kwargs_background': {},
        }
        if fixed_background:
            kwargs_fixed['kwargs_background']['background'] = initial_background

        # Default value for boundaries
        kwargs_up = {
            'kwargs_moffat': {'fwhm': jnp.inf, 'beta': jnp.inf, 'C': jnp.inf},
            'kwargs_gaussian': {'a': list([jnp.inf for i in range(self.M)]),
                                'x0': list([self.image_size for i in range(self.M)]),
                                'y0': list([self.image_size for i in range(self.M)])
                                },
            'kwargs_background': {'background': list([jnp.inf for i in range(self.image_size_up ** 2)])},
        }

        kwargs_down = {
            'kwargs_moffat': {'fwhm': 0., 'beta': 0., 'C': 0.},
            'kwargs_gaussian': {'a': list([0 for i in range(self.M)]),
                                'x0': list([-self.image_size for i in range(self.M)]),
                                'y0': list([-self.image_size for i in range(self.M)]),
                                },
            'kwargs_background': {'background': list([-jnp.inf for i in range(self.image_size_up ** 2)])},
        }

        return kwargs_init, kwargs_fixed, kwargs_up, kwargs_down
