from functools import partial

import jax.numpy as jnp
from jax import jit, vmap
from jax.lax import conv_general_dilated, conv_dimension_numbers

def scale_norms(n_scales):
    npix_dirac = 2 ** (n_scales + 2)
    dirac = jnp.diag((jnp.arange(npix_dirac) == int(npix_dirac / 2)).astype(float))
    wt_dirac = decompose(dirac, n_scales)
    norms = jnp.sqrt(jnp.sum(wt_dirac ** 2, axis=(1, 2,)))

    return norms

@partial(jit, static_argnums=(2))
def convolveSeparableDilated(image2D, kernel1D, dilation=1):
    """
    Convolves an image contained in ``image2D`` with the 1D kernel ``kernel1D``. The operation is
    blured2D = image2D * (kernel1D ∧ kernel1D), where ∧ is a wedge product, here a tensor product.

    :param kernel1D: 1D array to convolve the image with
    :param image2D: 2D array
    :param dilation:  makes the spacial extent of the kernel bigger. The default is 1.

    :return: 2D array

    """

    # Preparations
    image = jnp.expand_dims(image2D, (2,))
    # shape (Nx, Ny, 1) -- (N, W, C)
    # we treat the Nx as the batch number!! (because it is a 1D convolution
    # over the rows)
    kernel = jnp.expand_dims(kernel1D, (0, 2,))
    # here we have kernel shape ~(I,W,O)

    # so:
    # (Nbatch, Width, Channel) * (Inputdim, Widthkernel, Outputdim)
    #                                            -> (Nbatch, Width, Channel)
    # where Nbatch is our number of rows.
    dimension_numbers = ('NWC', 'IWO', 'NWC')
    dn = conv_dimension_numbers(image.shape,
                                kernel.shape,
                                dimension_numbers)
    # with these conv_general_dilated knows how to handle the different
    # axes:
    rowblur = conv_general_dilated(image, kernel,
                                   window_strides=(1,),
                                   padding='SAME',
                                   rhs_dilation=(dilation,),
                                   dimension_numbers=dn)

    # now we do the same for the columns, hence this time we have
    # (Height, Nbatch, Channel) * (Inputdim, Widthkernel, Outputdim)
    #                                            -> (Height, Nbatch, Channel)
    # where Nbatch is our number of columns.
    dimension_numbers = ('HNC', 'IHO', 'HNC')
    dn = conv_dimension_numbers(image.shape,
                                kernel.shape,
                                dimension_numbers)

    rowcolblur = conv_general_dilated(rowblur, kernel,
                                      window_strides=(1,),
                                      padding='SAME',
                                      rhs_dilation=(dilation,),
                                      dimension_numbers=dn)

    return rowcolblur[:, :, 0]

@partial(jit, static_argnums=(1,))
def decompose(image, n_scales):
    """Decomposes an image into a chosen wavelet basis."""
    # Validate input
    assert n_scales >= 0, "nscales must be a non-negative integer"
    if n_scales == 0:
        return image

    # Preparations
    image = jnp.copy(image)
    kernel = jnp.array([1, 4, 6, 4, 1]) / 16. #kernel for wavelet

    # Compute the first scale:
    c1 = convolveSeparableDilated(image, kernel)
    # Wavelet coefficients:
    w0 = (image - c1)
    result = jnp.expand_dims(w0, 0)
    cj = c1

    # Compute the remaining scales
    # at each scale, the kernel becomes larger ( a trou ) using the
    # dilation argument in the jax wrapper for convolution.
    for step in range(1, n_scales):
        cj1 = convolveSeparableDilated(cj, kernel, dilation=2 ** step)
        # wavelet coefficients
        wj = (cj - cj1)
        result = jnp.concatenate((result, jnp.expand_dims(wj, 0)), axis=0)
        cj = cj1

    # Append final coarse scale
    result = jnp.concatenate((result, jnp.expand_dims(cj, axis=0)), axis=0)
    return result

@jit
def reconstruct(coeffs):
    """Reconstructs an image from wavelet decomposition coefficients."""
    return jnp.sum(coeffs, axis=0)
