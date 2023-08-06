import warnings
from functools import partial

import jax.numpy as jnp
import numpy as np
from jax import jit
from utils.jax_utils import decompose, scale_norms


class Loss(object):
    """
    Class that manages the (auto-differentiable) loss function, defined as:
    L = - log(likelihood) - log(regularization) - log(positivity)

    Note that gradient, hessian, etc. are computed in the ``InferenceBase`` class.

    """

    _supported_ll = ('l2_norm')
    _supported_regul_source = ('l1_starlet')

    def __init__(self, data, deconv_class, param_class, sigma_2,
                 regularization_terms=None, regularization_strength_scales=None, regularization_strength_hf=None,
                 regularization_strength_positivity=0., regularization_strength_positivity_ps=0., W=None,
                 regularize_full_model = False):
        """
        :param data: array containing the observations
        :param deconv_class: deconvolution class from ``starred.deconvolution.deconvolution``
        :param param_class: parameters class from ``starred.deconvolution.parameters``
        :param sigma_2: array containing the square of the noise maps
        :param N: number of observations stamps
        :type N: int
        :param regularization_terms: information about the regularization terms
        :type regularization_terms: str
        :param regularization_strength_scales: Lagrange parameter that weights intermediate scales in the transformed domain 
        :type regularization_strength_scales: float
        :param regularization_strength_hf: Lagrange parameter weighting the highest frequency scale
        :type regularization_strength_hf: float
        :param regularization_strength_positivity: Lagrange parameter weighting the positivity of the background. 0 means no positivity constrain.
        :type regularization_strength_positivity: float
        :param regularization_strength_positivity_ps: Lagrange parameter weighting the positivity of the point sources. 0 means no positivity constrain.
        :type regularization_strength_positivity: float
        :param W: weight matrix. Shape (n_scale, n_pix*subsampling_factor, n_pix*subsampling_factor)

        """
        self._data = data
        self._sigma_2 = sigma_2
        self.W = W
        self._deconv = deconv_class
        self._datar = self._data.reshape(self._deconv.epochs,
                                         self._deconv.image_size,
                                         self._deconv.image_size)
        self._sigma_2r = self._sigma_2.reshape(self._deconv.epochs,
                                               self._deconv.image_size,
                                               self._deconv.image_size)

        self._param = param_class
        self.epochs = self._deconv.epochs
        self.regularize_full_model = regularize_full_model
        self._init_likelihood()
        self._init_regularizations(regularization_terms, regularization_strength_scales, regularization_strength_hf,
                                   regularization_strength_positivity, regularization_strength_positivity_ps)

    # @partial(jit, static_argnums=(0,))
    def __call__(self, args):
        return self.loss(args)

    def loss(self, args):
        """Defined as the negative log(likelihood*regularization)."""
        kwargs = self._param.args2kwargs(args)
        neg_log = - (self._log_likelihood(kwargs) + self._log_regul(kwargs) + self._log_regul_positivity(kwargs) + self._log_regul_positivity_ps(kwargs))
        return jnp.nan_to_num(neg_log, nan=1e15, posinf=1e15, neginf=1e15)

    @property
    def datar(self):
        """Returns the observations array."""
        return self._datar.astype(dtype=np.float32)

    @property
    def sigma_2r(self):
        """Returns the noise map array."""
        return self._sigma_2r.astype(dtype=np.float32)

    def _init_likelihood(self):
        """Intialization of the data fidelity term of the loss function."""
        self._log_likelihood = self._log_likelihood_chi2

    def _init_regularizations(self, regularization_terms, regularization_strength_scales, regularization_strength_hf,
                              regularization_strength_positivity, regularization_strength_positivity_ps):
        """Intialization of the regularization terms of the loss function."""
        regul_func_list = []
        # add the log-regularization function to the list
        regul_func_list.append(getattr(self, '_log_regul_' + regularization_terms))

        if regularization_terms == 'l1_starlet':
            n_pix_src = min(*self.datar[0, :, :].shape) * self._deconv._upsampling_factor
            self.n_scales = int(np.log2(n_pix_src))  # maximum allowed number of scales
            if self.W is None:  # old fashion way
                if regularization_strength_scales != 0 and regularization_strength_hf != 0:
                    warnings.warn('lambda is not normalized. Provide the weight map !')
                wavelet_norms = scale_norms(self.n_scales)[:-1]  # ignore coarsest scale
                self._st_src_norms = jnp.expand_dims(wavelet_norms, (1, 2)) * jnp.ones((n_pix_src, n_pix_src))
            else:
                self._st_src_norms = self.W[:-1]  # ignore the coarsest scale
            self._st_src_lambda = float(regularization_strength_scales)
            self._st_src_lambda_hf = float(regularization_strength_hf)

        # positivity term
        self._pos_lambda = float(regularization_strength_positivity)
        self._pos_lambda_ps = float(regularization_strength_positivity_ps)
        # build the composite function (sum of regularization terms)
        self._log_regul = lambda kw: sum([func(kw) for func in regul_func_list])

    # @partial(jit, static_argnums=(0,))
    def _log_likelihood_chi2(self, kwargs):
        """Computes the data fidelity term of the loss function using the L2 norm."""
        model = self._deconv.model(kwargs)
        return - 0.5 * (1. / self.epochs) * jnp.sum((model - self.datar) ** 2 / self.sigma_2r)

        # return - 0.5 * jnp.sum(jnp.array([jnp.sum(jnp.subtract(self.data[i,:,:], self._deconv.model(i, **kwargs)[0])**2 / self.sigma_2[i,:,:]) for i in range(self.epochs)]))

    # @partial(jit, static_argnums=(0,))
    def _log_regul_l1_starlet(self, kwargs):
        """
        Computes the regularization terms as the sum of:
        
        - the L1 norm of the Starlet transform of the highest frequency scale, and
        - the L1 norm of the Starlet transform of all remaining scales (except the coarsest).
        """
        if self.regularize_full_model:
            toreg, _ = self._deconv.getDeconvolved(kwargs, epoch=0)
        else :
            toreg = kwargs['kwargs_background']['h'].reshape(self._deconv.image_size_up, self._deconv.image_size_up)
        st = decompose(toreg, self.n_scales)[:-1]  # ignore coarsest scale
        st_weighted_l1_hf = jnp.sum(self._st_src_norms[0] * jnp.abs(st[0]))  # first scale (i.e. high frequencies)
        st_weighted_l1 = jnp.sum(self._st_src_norms[1:] * jnp.abs(st[1:]))  # other scales
        tot_l1_reg = - (self._st_src_lambda_hf * st_weighted_l1_hf + self._st_src_lambda * st_weighted_l1)
        return tot_l1_reg / self._deconv._upsampling_factor**2

    def _log_regul_positivity(self, kwargs):
        """
        Computes the posivity constraint term. A penalty is applied if the epoch with the smallest background mean has negative pixels.

        :param kwargs:
        """
        h = jnp.array(kwargs['kwargs_background']['h'])
        sum_pos = -jnp.where(h < 0., h, 0.).sum()
        return - self._pos_lambda * sum_pos

    def _log_regul_positivity_ps(self, kwargs):
        """
        Computes the posivity constraint term for the point sources. A penalty is applied if one of the point sources have negative amplitude.

        :param kwargs:
        """
        fluxes = jnp.array(kwargs['kwargs_analytic']['a'])
        min_amp = jnp.min(fluxes, initial=0.)
        return - self._pos_lambda * jnp.abs(jnp.minimum(0., min_amp))

    def update_weights(self, W):
        """Updates the weight matrix W."""
        self._st_src_norms = W[:-1]
        self.W = W
