from functools import partial

from jax import jit, grad, jacfwd, jacrev, jvp, value_and_grad

__all__ = ['InferenceBase']


class InferenceBase(object):
    """Class that defines wraps the loss function, and computes first and second order derivatives.
    
    :param loss_class: Loss instance
    :param param_class: Parameters instance
    """

    def __init__(self, loss_class, param_class):
        self._loss = loss_class
        self._param = param_class

    @property
    def parameters(self):
        """Returns the parameters."""
        return self._param

    # @partial(jit, static_argnums=(0,))
    def loss(self, args):
        """
        Loss function to be minimized. Called if arguments of ``self._loss_fn`` should be args-like (`i.e.`, as an array).
        """
        return self._loss(args)

    # @partial(jit, static_argnums=(0,))
    def gradient(self, args):
        """Returns the gradient (first derivative) of the loss function."""
        return grad(self.loss)(args)

    # @partial(jit, static_argnums=(0,))
    def value_and_gradient(self, args):
        """Returns both the value and the gradient (first derivative) of the loss function."""
        return value_and_grad(self.loss)(args)

    # @partial(jit, static_argnums=(0,))
    def hessian(self, args):
        """Returns the Hessian (second derivative) of the loss function."""
        return jacfwd(jacrev(self.loss))(args)

    # @partial(jit, static_argnums=(0,))
    def hessian_vec_prod(self, args, vec):
        """Hessian-vector product."""
        # forward-over-reverse (https://jax.readthedocs.io/en/latest/notebooks/autodiff_cookbook.html#hessian-vector-products-using-both-forward-and-reverse-mode)
        return jvp(grad(self.loss), (args,), (vec,))[1]
