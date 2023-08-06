import jax.numpy as jnp
import numpy as np

from starred.utils.parameters import Parameters

__all__ = ['ParametersDeconv']


class ParametersDeconv(Parameters):
    """
    Deconvolution parameters class.

    """

    def __init__(self, image_class, kwargs_init, kwargs_fixed, kwargs_up=None, kwargs_down=None):
        """
        :param image_class: image/deconvolution class from ``starred.deconvolution.deconvolution``
        :param kwargs_init: dictionary with information on the initial values of the parameters 
        :param kwargs_fixed: dictionary containing the fixed parameters 
        :param kwargs_up: dictionary with information on the upper bounds of the parameters 
        :param kwargs_down: dictionary with information on the lower bounds of the parameters 

        """
        super(ParametersDeconv, self).__init__(image_class, kwargs_init, kwargs_fixed, kwargs_up=kwargs_up,
                                               kwargs_down=kwargs_down)

    def args2kwargs(self, args):
        """Obtain a dictionary of keyword arguments from positional arguments."""
        i = 0
        kwargs_analytic, i = self._get_params(args, i, 'kwargs_analytic')
        kwargs_background, i = self._get_params(args, i, 'kwargs_background')
        # wrap-up
        kwargs = {'kwargs_analytic': kwargs_analytic, 'kwargs_background': kwargs_background}
        return kwargs

    def kwargs2args(self, kwargs):
        """Obtain an array of positional arguments from a dictionary of keyword arguments."""
        args = self._set_params(kwargs, 'kwargs_analytic')
        args += self._set_params(kwargs, 'kwargs_background')
        return jnp.array(args)

    def get_param_names_for_model(self, kwargs_key):
        """Returns the names of the parameters according to the key provided."""
        if kwargs_key == 'kwargs_analytic':
            return self._image.param_names_analytic
        return self._image.param_names_background

    def _get_params(self, args, i, kwargs_key):
        """Getting the parameters."""
        kwargs = {}
        kwargs_fixed_k = self._kwargs_fixed[kwargs_key]
        param_names = self.get_param_names_for_model(kwargs_key)
        for name in param_names:
            if not name in kwargs_fixed_k:
                if name == 'a':
                    num_param = self._image.M * self._image.epochs
                elif name == 'h':
                    num_param = self._image.image_size_up ** 2
                elif name == 'mean':
                    num_param = self._image.epochs
                elif name == 'dx' or name == 'dy':
                    num_param = self._image.epochs - 1
                elif name == 'c_x' or name == 'c_y':
                    num_param = self._image.M
                else:
                    raise NameError(f"The ParametersDeconv class does not know about this parameter: {name}.")
                kwargs[name] = args[i:i + num_param]
                i += num_param
            else:
                kwargs[name] = kwargs_fixed_k[name]
        return kwargs, i

    def _set_params(self, kwargs, kwargs_key):
        """Setting the parameters."""
        args = []
        kwargs_profile = kwargs[kwargs_key]
        kwargs_fixed_k = self._kwargs_fixed[kwargs_key]
        param_names = self.get_param_names_for_model(kwargs_key)
        for name in param_names:
            if not name in kwargs_fixed_k and name != 'lambda':
                if isinstance(kwargs_profile[name], list):
                    args += kwargs_profile[name]
                elif isinstance(kwargs_profile[name], (np.ndarray, np.generic)):
                    args += kwargs_profile[name].tolist()
                elif isinstance(kwargs_profile[name], (jnp.ndarray, jnp.generic)):
                    args += kwargs_profile[name].tolist()
                else:
                    args += [kwargs_profile[name]]
        return args
