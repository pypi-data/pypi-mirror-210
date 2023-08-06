from copy import deepcopy
from functools import partial

import jax.numpy as jnp
import numpy as np
from jax import jit, vmap
from jax.image import scale_and_translate
import dill as pkl
import os

from starred.utils.generic_utils import pad_and_convolve_fft, \
    pad_and_convolve, \
    fwhm2sigma, gaussian_function, \
    make_grid, Downsample, save_fits, save_npy


class Deconv(object):
    """
    Image deconvolution class. The order of the params below matters for unpacking re-packing dictionaries.

    """
    param_names_analytic = ['a', 'c_x', 'c_y', 'dx', 'dy']
    param_names_background = ['mean', 'h']

    def __init__(self, image_size, number_of_sources, scale,
                 upsampling_factor=2, epochs=1, psf=None,
                 gaussian_fwhm=2, convolution_method='fft'):
        """
        :param image_size: input image size in pixels
        :type image_size: int
        :param number_of_sources: amount of point sources 
        :type number_of_sources: int
        :param scale: scaling factor
        :type scale: float
        :param upsampling_factor: the proportion by which the sampling rate increases with respect to the input image
        :type upsampling_factor: int
        :param epochs: for a joint deconvolution, the number of epochs considered. For single deconvolution, ``epochs`` is 1
        :type epochs: int
        :param psf: Point Spread Function array from ``starred.psf.psf``, acting as deconvolution kernel here
        :param gaussian_fwhm: the Gaussian's FWHM in pixels
        :type gaussian_fwhm: int
        :param convolution_method: method to use to calculate the convolution
        :type convolution_method: str

        """
        self.image_size = image_size

        # setter since vectorized functions used here depend on upsampling factor:
        self.setUpsamplingFactor(upsampling_factor)

        self.image_size_up = image_size * upsampling_factor
        self.epochs = epochs
        self.M = number_of_sources
        self.gaussian_fwhm = gaussian_fwhm
        # let's carry the coordinates of our working grid (the upscaled one):
        self.x, self.y = make_grid(numPix=self.image_size_up, deltapix=1.)
        if convolution_method == 'fft':
            self._convolve = pad_and_convolve_fft
        elif convolution_method == 'lax':
            self._convolve = pad_and_convolve
        else:
            raise NotImplementedError('Unknown convolution method: choose fft or lax')

        if self.image_size_up % 2:
            raise ValueError(
                'With these settings the output will have odd dimensions. To obtain adequate results, at least one between the image size and the upsampling factor must be even.')

        if psf is None:
            raise TypeError('Please provide the narrow PSF.')
        else:
            if not len(psf.shape)==3:
                raise RuntimeError('We expect your psf to have shape (epochs, nx, ny). Your psf does not have the right number of dimensions, with shape: {psf.shape}')
            psf = np.flip(psf, (1,2))
            n_epochs, nx, ny = psf.shape
            assert n_epochs == self.epochs, "Please provide one PSF for each epoch"
            if (nx != self.image_size_up or ny != self.image_size_up) and convolution_method == 'fft':
                print('Padding the PSFs to match the upsampled image size...')
                if (self.image_size_up - nx)%2 or (self.image_size_up - ny)%2:
                    raise RuntimeError('Upsampled image size and PSF size do not match. Please pad the PSF manually to match '
                                       'the size of the upsampled image. Make sure it is properly centered. '
                                       'PSF kernels should have an even number of pixels')
                else :
                    padx, pady = int((self.image_size_up - nx) / 2), int((self.image_size_up - ny) / 2)
                    psf = jnp.pad(psf, ((0, 0), (padx, padx), (pady, pady)), constant_values=0.)

            self.psf = psf.astype(np.float32)
        self.sigma = fwhm2sigma(self.gaussian_fwhm)

        self._model = self.modelstack if self.epochs > 5 else self.modelstack_forloop
        self.scale = scale

    # @partial(jit, static_argnums=(0,))
    def shifted_gaussians(self, c_x, c_y, a):
        """
        Generates a 2D array with the point sources of the deconvolved image.

        :param c_x: 1D array containing the x positions of the point sources
        :param c_y: 1D array containing the y positions of the point sources
        :param a: 1D array containing the amplitude coefficients of each Gaussian representing a point source
        :return: 2D array

        """
        return jnp.sum(jnp.array([gaussian_function(
            x=self.x, y=self.y,
            amp=a[i], sigma_x=self.sigma,
            sigma_y=self.sigma,
            center_x=c_x[i],
            center_y=c_y[i],
        ).reshape(self.image_size_up, self.image_size_up) for i in range(self.M)]), axis=0)

    @partial(jit, static_argnums=(0,))
    def translate_array(self, array, dx, dy):
        """
        Using first order interpolation, translates the array by (dx, dy) pixels.
        In the context of this problem, typically we will have dx ~ dy < 1.

        :param array: 2D array to be translated
        :param dx: translation in the x direction (in pixels)
        :type dx: float
        :param dy: translation in the y direction (in pixels)
        :type dy: float
        :return: 2D array - A translated version of the input array

        """
        return scale_and_translate(image=array,
                                   shape=array.shape,
                                   spatial_dims=(0, 1),
                                   scale=jnp.array((1., 1.)),
                                   translation=jnp.array((dy, dx)),
                                   method='bilinear')

    # @partial(jit, static_argnums=(0,))
    def one_epoch(self, psf, params):
        """
        Produces a 2D array corresponding to one epoch of the deconvolution.

        :param psf: 2D array representing the PSF at this epoch, usually upsampled
        :param params: 1D array with the parameters in the following order:

            - the x positions of the point sources (M params)
            - the y positions of the point sources (M params)
            - the amplitudes of the point sources (M params)
            - the x translation of the whole epoch (1 param)
            - the y translation of the whole epoch (1 param)
            - the background (``self.image_size_up**2`` params)

        :return: 2D array that represents the model for one epoch. This is, a collection of point sources plus background, convolved with the PSF and potentially translated in the x and y directions

        """

        # unpack:
        # (a bit messy, see the re-packing in self.model and the comment there)
        # TODO
        c_x = params[0:self.M]
        c_y = params[self.M:2 * self.M]
        a = params[2 * self.M:3 * self.M]
        dx = params[3 * self.M]
        dy = params[3 * self.M + 1]
        mean = params[3 * self.M + 2]
        h = params[3 * self.M + 2: 3 * self.M + 2 + self.image_size_up ** 2]

        # initially, just the background:
        f = h.reshape((self.image_size_up, self.image_size_up))

        # add the point sources at the deconvoled resolution:
        f += self.scale * self.shifted_gaussians(c_x, c_y, a)

        # convolve with the psf to match the resolution of the observation:
        f = self._convolve(f, psf, False).reshape(self.image_size_up,
                                                  self.image_size_up)

        # shift to compensate small translations between epochs:
        f = self.translate_array(f, dx, dy)

        # now we can also add the constant background:
        f += mean
        # adding after translation avoids border effects 
        # (translation pads image with 0s, very noticeable when mean != 0)

        return f

    def getDeconvolved(self, kwargs, epoch):
        """
        This is a utility function to retrieve the deconvolved model at one 
        specific epoch. It will typically be called only once after the optimization process.

        :param kwargs: dictionary containing the parameters of the model
        :param epoch: number of epochs
        :type epoch: int
        :return: tuple of two 2D arrays: (deconvolved image, background)

        """
        kwargs_analytic = kwargs['kwargs_analytic']
        kwargs_background = kwargs['kwargs_background']
        c_x = kwargs_analytic['c_x']
        c_y = kwargs_analytic['c_y']
        a = kwargs_analytic['a'][self.M * epoch:self.M * (epoch + 1)]

        h = kwargs_background['h'].reshape(self.image_size_up, self.image_size_up)
        mean = kwargs_background['mean'][epoch]
        h = h.copy()
        f = h.copy()
        if self.M != 0:
            f += self.scale * self.shifted_gaussians(c_x, c_y, a)

        # shift:
        if epoch == 0:
            dx, dy = 0., 0.
        else:
            dx = kwargs_analytic['dx'][epoch - 1]
            dy = kwargs_analytic['dy'][epoch - 1]

        deconvolved = self.translate_array(f, dx, dy)
        background = self.translate_array(h, dx, dy) + mean

        return deconvolved, background

    def setUpsamplingFactor(self, upsampling_factor):
        """
        Sets the upsampling factor.

        :param upsampling_factor: the proportion by which the sampling rate increases with respect to the input image
        :type upsampling_factor: int

        """
        self._upsampling_factor = upsampling_factor

        # down sample operator from utils: will need a vectorized version.
        self.DownsampleAllEpochs = vmap(lambda array: Downsample(array, upsampling_factor),
                                        in_axes=(0,))

    # @partial(jit, static_argnums=(0,))
    def modelstack_forloop(self, pars):
        """
        Creates a model for all the epochs with shape (epoch, image_size_up, image_size_up) by looping over the epochs.
        This is slightly faster for a low number of epochs (~1 to 5) than using a vectorized version of ``self.one_epoch``.

        :param pars: stack of arrays of parameters for one epoch. Shape (epoch, N), where N is the number of parameters per epoch (see the docstring of ``self.one_epoch``)

        :return: 2D array of shape (epoch, image_size_up, image_size_up)

        """
        return jnp.array([self.one_epoch(self.psf[i], pars[i]) for i in range(self.epochs)])

    # @partial(jit, static_argnums=(0,))
    def modelstack(self, pars):
        """
        Creates a model for all the epochs with shape (epoch, image_size_up, image_size_up) by vectorizing ``self.one_epoch``.
        Much faster for a large number of epochs (> 10), regime where the ``self.modelstack_forloop`` version cannot be jit'ed anymore.

        :param pars: stack of arrays of parameters for one epoch. Shape (epoch, N), where N is the number of parameters per epoch (see the docstring of ``self.one_epoch``)
        
        :return: 2D array of shape (epoch, image_size_up, image_size_up)

        """

        # vmap magic to vectorize our one_epoch method:
        broadcast = vmap(self.one_epoch, in_axes=(0, 0))
        # here we specify `in_axes`: vectorize over the first axis of the
        # array of PSFs, and over the first axis of the array of parameters.
        # by the way:  
        # - array of PSFs: stack of 2D slices
        # - array of parameters: stack of 1D slices, each containing the parameters
        #                        for one epoch.

        return broadcast(self.psf, pars)

    # @partial(jit, static_argnums=(0,))
    def model(self, kwargs):
        """
        Creates the 2D deconvolution model image.
        
        :param kwargs: dictionary containing the parameters of the model.
        :return: 3D array - A stack of 2D images (one layer per epoch)

        """
        # part 1: unpack the key words and put them in a giant 2D array:

        an = deepcopy(kwargs['kwargs_analytic'])
        back = kwargs['kwargs_background']['h']
        mean = kwargs['kwargs_background']['mean']

        # for the translations, we have epochs-1 parameters
        # and the first epoch is fixed: pre-append 0.
        an['dx'] = jnp.hstack(([0.], an['dx']))
        an['dy'] = jnp.hstack(([0.], an['dy']))
        # a bit messy here, we manually unpack each keyword.
        # the ParameterDeconv class should be taking care of this,
        # but we don't have access to it in this class in the way
        # things are set up right now.
        # TODO 

        rows = []
        M = self.M
        for i in range(self.epochs):
            row1 = jnp.hstack((an[key] for key in ['c_x', 'c_y']))
            row2 = jnp.hstack((an[key][i * M:(i + 1) * M] for key in ['a']))
            row3 = jnp.hstack((an[key][i:i + 1] for key in ['dx', 'dy']))
            epochmean = jnp.array([mean[i]])
            row = jnp.hstack((row1, row2, row3, epochmean, back))
            rows.append(row)
        args = jnp.array(rows)

        # part 2, pass the giant 2D array to the model function:
        modelupscale = self._model(args)
        # this generates a model on the upscaled grid.

        # Now we down sample. Each new pixel is the average of all the
        # small pixels that composed it before.        
        model = self.DownsampleAllEpochs(modelupscale)

        # to conserve the surface brightness:
        model = model * ((self.image_size_up ** 2) / (self.image_size ** 2))

        return model

    def dump(self, path, kwargs):
        """Stores information in a given file."""
        with open(path, 'wb') as f:
            pkl.dump([self, kwargs], f)

    def export(self, output_folder, kwargs_final, data, sigma_2, epoch=None, format='fits'):
        """
        Saves all the output files.

        :param output_folder: path to the output folder
        :type output_folder: str
        :param kwargs_final: dictionary containing all keyword arguments
        :param data: array containing the images
        :param sigma_2: array containing the noise maps
        :param epoch: integer or array or list containing the indices of the epoch to export. None, for exporting all epochs.
        :param format: output format. Choose between ``npy`` or ``fits``
        :type format: str
        """

        if format == 'fits':
            save_fct = save_fits
        elif format == 'npy':
            save_fct = save_npy
        else:
            raise NotImplementedError(f'Format {format} unknown.')

        if epoch is None:
            print('Exporting all epochs')
            epoch_arr = np.arange(self.epochs)
        elif not hasattr(epoch, "__len__") :
            epoch_arr = np.array([epoch])
        else :
            epoch_arr = np.array(epoch)

        for i,e in enumerate(epoch_arr):
            output = self.model(kwargs_final)[e]
            deconv, h = self.getDeconvolved(kwargs_final, e)
            data_show = data[e, :, :]
            dif = data_show - output
            rr = np.abs(dif) / np.sqrt(sigma_2[e, :, :])

            if i == 0:
                save_fct(h, os.path.join(output_folder, 'background'))

            save_fct(data_show, os.path.join(output_folder, f'data_{i}'))
            save_fct(output, os.path.join(output_folder, f'model_{i}'))
            save_fct(dif, os.path.join(output_folder, f'residuals_{i}'))
            save_fct(deconv, os.path.join(output_folder, f'deconvolution_{i}'))
            save_fct(rr, os.path.join(output_folder, f'scaled_residuals_{i}'))

    def flux_at_epoch(self, kwargs, epoch=0):
        """
        Return an array containing the flux of the point sources at epoch `epoch`.

        :param kwargs_final: dictionary containing all keyword arguments
        :param epoch: index of the epoch
        """
        a = kwargs['kwargs_analytic']['a'][self.M * epoch:self.M * (epoch + 1)] * self.scale

        return a

def setup_model(data, sigma_2, s, xs, ys, amps, subsampling_factor):
    """
    Utility setting up a deconvolution model. The returned dictionaries of
    parameters can later be adjusted by the user. 

    :param data: 3D array containing the images, one per epoch. shape (epochs, im_size, im_size)
    :param sigma_2: 3D array containing the noisemaps, one per epoch. shape (epochs, im_size, im_size)
    :param s: 3D array containing the the narrow PSFs, one per epoch. shape (epochs, im_size_up, im_size_up) where im_size_up needs be a multiple of im_size.
    :param xs: 1D array or list containing the x positions of the point sources. For N point sources, len(xs) is N.
    :param ys: 1D array or list containing the y positions of the point sources. For N point sources, len(ys) is N.
    :param amps: list containing the amplitudes of the point sources. For N point sources, len(amps) is N. The same amplitudes will be applied to all epochs.
    :param subsampling_factor: integer, ratio of the size of the data pixels to that of the PSF pixels.
    :return: a tuple: (a starred.deconvolution.Deconv instance, 
                       a dictionary with the initial values of the model parameters,
                       a dictionary with the upper boundaries of the model parameters,
                       a dictionary with the lower boundaries of the model parameters,
                       a dictionary with the fixed parameters of the model)
    """

    # amps MUST be a list, not a numpy array. (we're using epochs*amps to get
    # amps for each epoch)
    amps = [float(amp) for amp in amps]
    # xs and ys, let's make them numpy arrays cuz it's easier 
    xs = np.array(xs)
    ys = np.array(ys)
    
    if not len(amps) == xs.size == ys.size:
        message = "Your amps, xs or ys (refering to amplitudes and positions of your point sources)"
        message += " arguments need be the of the same length!\n"
        message += f"But we have size(xs)={xs.size}, size(ys)={ys.size}, size(amps)={len(amps)}"
        raise RuntimeError(message)
    
    epochs = data.shape[0]
    if not sigma_2.shape == data.shape:
        message = "The shape of your data and noisemaps is not what we expect."
        message += " They need be of shape ~ (epochs, some nx, some ny).\n"
        message += f"But we have shape(data)={data.shape}, shape(sigma_2)={sigma_2.shape}."
        raise RuntimeError(message)
        
    if not epochs == sigma_2.shape[0] == s.shape[0]:
        message = "The number of epochs in your data, noisemaps or PSFs do not match\n"
        message += f"We have shape(data)={data.shape}, shape(sigma_2)={sigma_2.shape}, shape(s)={s.shape}\n"
        message += "We expected the first dimension of each (# of epochs) to be the same."
        raise RuntimeError(message)
    
    im_size = data[0].shape[0]
    im_size_up = im_size * subsampling_factor
    
    # Parameter initialization
    M = xs.size # number of point sources
    initial_c_x = xs * subsampling_factor 
    initial_c_y = ys * subsampling_factor 
    # intensity per point:
    initial_a = np.array(epochs*amps)
    scale = data.max()
    initial_a /= scale
    # initial background:
    initial_h = np.zeros((im_size_up**2))
    # dictionary containing the parameters of deconvolution.
    # (The translations dx, dy are set to zero for the first epoch.
    # Thus we only initialize (epochs-1) of them.)
    kwargs_init = {
        'kwargs_analytic': {
                            'c_x': initial_c_x, # point sources positions
                            'c_y': initial_c_y,
                            'dx' : np.ravel([0. for _ in range(epochs-1)]), # translation per epoch
                            'dy' : np.ravel([0. for _ in range(epochs-1)]),
                            'a'  : initial_a}, # amplitudes of point sources
        'kwargs_background': {'h': initial_h, # background
                              'mean': np.ravel([0. for _ in range(epochs)])}, # additive constant for background per epoch
    }
    # same as above, providing fixed parameters:
    kwargs_fixed = {
        'kwargs_analytic': {},
        'kwargs_background': {},
    }
    # boundaries.
    kwargs_up = {
        'kwargs_analytic': {'c_x': list(initial_c_x+3),
                            'c_y': list(initial_c_y+3),
                            'dx' : [3. for _ in range(epochs-1)],
                            'dy' : [3. for _ in range(epochs-1)],
                             'a': list([np.inf for i in range(M*epochs)]) 
                           },
        'kwargs_background': {'h': list([np.inf for i in range(0, im_size_up**2)]),
                              'mean': [np.inf for _ in range(epochs)]
                               },
    }
    kwargs_down = {
        'kwargs_analytic': {'c_x': list(initial_c_x-3),
                            'c_y': list(initial_c_y-3),
                            'dx' : [-3. for _ in range(epochs-1)],
                            'dy' : [-3. for _ in range(epochs-1)],
                             'a': list([0 for i in range(M*epochs)]) },
        'kwargs_background': {'h': list([-np.inf for i in range(0, im_size_up**2)]),
                              'mean': [-np.inf for _ in range(epochs)]
                               },
    }
    # Initializing the model
    model = Deconv(image_size=im_size, 
                   number_of_sources=M, 
                   scale=scale, 
                   upsampling_factor=subsampling_factor, 
                   epochs=epochs, 
                   psf=s, 
                   convolution_method='fft')

    # returning model and kwargs.    
    return model, kwargs_init, kwargs_up, kwargs_down, kwargs_fixed
