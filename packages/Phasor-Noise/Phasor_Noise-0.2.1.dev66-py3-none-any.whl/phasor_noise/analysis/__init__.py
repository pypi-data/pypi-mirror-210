import numpy as np


def PSD(signal: list) -> np.ndarray:
    """
    PSD = |x̂(f)|² with x̂ the Fourier Transform of the Signal scale by the time of integration.

    Parameters
    ----------
    signal : ndarray or list
        Containers of evaluated value by a function.

    Returns
    -------
    y : ndarray
        The Power Spectral Density of a signal.
    """
    f = np.fft.fft2(signal)
    f_s = np.fft.fftshift(f)
    return np.power(np.absolute(f_s), 2)


def mean(noise_array: list) -> float:
    """
    Mean retrieve the average from an array.

    Parameters
    ----------
    noise_array : ndarray or list
        Data containers.
    Returns
    -------
    y : float
        Mean of the parameters.
    """
    return np.average(noise_array)


def std_gap(noise_array: list) -> float:
    """
    std_gap retrieve the standard deviation of parameters.

    Parameters
    ----------
    noise_array : ndarray or list
        Data containers.
    Return
    ------
    y : float
        Standard deviation of parameters.
    """
    return np.std(noise_array)
