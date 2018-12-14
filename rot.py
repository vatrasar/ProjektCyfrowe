def _spectral_helper(x, y, fs=1.0, window='hann', nperseg=None, noverlap=None,
                     nfft=None, detrend='constant', return_onesided=True,
                     scaling='spectrum', axis=-1, mode='psd', boundary=None,
                     padded=False):
    """
    Calculate various forms of windowed FFTs for PSD, CSD, etc.

    This is a helper function that implements the commonality between
    the stft, psd, csd, and spectrogram functions. It is not designed to
    be called externally. The windows are not averaged over; the result
    from each window is returned.

    Parameters
    ---------
    x : array_like
        Array or sequence containing the data to be analyzed.
    y : array_like
        Array or sequence containing the data to be analyzed. If this is
        the same object in memory as `x` (i.e. ``_spectral_helper(x,
        x, ...)``), the extra computations are spared.
    fs : float, optional
        Sampling frequency of the time series. Defaults to 1.0.
    window : str or tuple or array_like, optional
        Desired window to use. If `window` is a string or tuple, it is
        passed to `get_window` to generate the window values, which are
        DFT-even by default. See `get_window` for a list of windows and
        required parameters. If `window` is array_like it will be used
        directly as the window and its length must be nperseg. Defaults
        to a Hann window.
    nperseg : int, optional
        Length of each segment. Defaults to None, but if window is str or
        tuple, is set to 256, and if window is array_like, is set to the
        length of the window.
    noverlap : int, optional
        Number of points to overlap between segments. If `None`,
        ``noverlap = nperseg // 2``. Defaults to `None`.
    nfft : int, optional
        Length of the FFT used, if a zero padded FFT is desired. If
        `None`, the FFT length is `nperseg`. Defaults to `None`.
    detrend : str or function or `False`, optional
        Specifies how to detrend each segment. If `detrend` is a
        string, it is passed as the `type` argument to the `detrend`
        function. If it is a function, it takes a segment and returns a
        detrended segment. If `detrend` is `False`, no detrending is
        done. Defaults to 'constant'.
    return_onesided : bool, optional
        If `True`, return a one-sided spectrum for real data. If
        `False` return a two-sided spectrum. Note that for complex
        data, a two-sided spectrum is always returned.
    scaling : { 'density', 'spectrum' }, optional
        Selects between computing the cross spectral density ('density')
        where `Pxy` has units of V**2/Hz and computing the cross
        spectrum ('spectrum') where `Pxy` has units of V**2, if `x`
        and `y` are measured in V and `fs` is measured in Hz.
        Defaults to 'density'
    axis : int, optional
        Axis along which the FFTs are computed; the default is over the
        last axis (i.e. ``axis=-1``).
    mode: str {'psd', 'stft'}, optional
        Defines what kind of return values are expected. Defaults to
        'psd'.
    boundary : str or None, optional
        Specifies whether the input signal is extended at both ends, and
        how to generate the new values, in order to center the first
        windowed segment on the first input point. This has the benefit
        of enabling reconstruction of the first input point when the
        employed window function starts at zero. Valid options are
        ``['even', 'odd', 'constant', 'zeros', None]``. Defaults to
        `None`.
    padded : bool, optional
        Specifies whether the input signal is zero-padded at the end to
        make the signal fit exactly into an integer number of window
        segments, so that all of the signal is included in the output.
        Defaults to `False`. Padding occurs after boundary extension, if
        `boundary` is not `None`, and `padded` is `True`.
    Returns
    -------
    freqs : ndarray
        Array of sample frequencies.
    t : ndarray
        Array of times corresponding to each data segment
    result : ndarray
        Array of output data, contents dependent on *mode* kwarg.

    Notes
    -----
    Adapted from matplotlib.mlab

    .. versionadded:: 0.16.0
    """
    # if mode not in ['psd', 'stft']:
    #     raise ValueError("Unknown value for mode %s, must be one of: "
    #                      "{'psd', 'stft'}" % mode)

    boundary_funcs = {'even': even_ext,
                      'odd': odd_ext,
                      'constant': const_ext,
                      'zeros': zero_ext,
                      None: None}

    # if boundary not in boundary_funcs:
    #     raise ValueError("Unknown boundary option '{0}', must be one of: {1}"
    #                       .format(boundary, list(boundary_funcs.keys())))

    # If x and y are the same object we can save ourselves some computation.
    same_data = y is x
    #
    # if not same_data and mode != 'psd':
    #     raise ValueError("x and y must be equal if mode is 'stft'")

    axis = int(axis)

    # Ensure we have np.arrays, get outdtype
    x = np.asarray(x)
    # if not same_data:
    #     y = np.asarray(y)
    #     outdtype = np.result_type(x, y, np.complex64)
    # else:
    outdtype = np.result_type(x, np.complex64)

    # if not same_data:
    #     # Check if we can broadcast the outer axes together
    #     xouter = list(x.shape)
    #     youter = list(y.shape)
    #     xouter.pop(axis)
    #     youter.pop(axis)
    #     try:
    #         outershape = np.broadcast(np.empty(xouter), np.empty(youter)).shape
    #     except ValueError:
    #         raise ValueError('x and y cannot be broadcast together.')

    if same_data:
        if x.size == 0:
            return np.empty(x.shape), np.empty(x.shape), np.empty(x.shape)
    else:
        if x.size == 0 or y.size == 0:
            outshape = outershape + (min([x.shape[axis], y.shape[axis]]),)
            emptyout = np.rollaxis(np.empty(outshape), -1, axis)
            return emptyout, emptyout, emptyout

    if x.ndim > 1:
        if axis != -1:
            x = np.rollaxis(x, axis, len(x.shape))
            if not same_data and y.ndim > 1:
                y = np.rollaxis(y, axis, len(y.shape))

    # Check if x and y are the same length, zero-pad if necessary
    # if not same_data:
    #     if x.shape[-1] != y.shape[-1]:
    #         if x.shape[-1] < y.shape[-1]:
    #             pad_shape = list(x.shape)
    #             pad_shape[-1] = y.shape[-1] - x.shape[-1]
    #             x = np.concatenate((x, np.zeros(pad_shape)), -1)
    #         else:
    #             pad_shape = list(y.shape)
    #             pad_shape[-1] = x.shape[-1] - y.shape[-1]
    #             y = np.concatenate((y, np.zeros(pad_shape)), -1)

    if nperseg is not None:  # if specified by user
        nperseg = int(nperseg)
        if nperseg < 1:
            raise ValueError('nperseg must be a positive integer')

    # parse window; if array like, then set nperseg = win.shape
    win, nperseg = _triage_segments(window, nperseg,input_length=x.shape[-1])

    if nfft is None:
        nfft = nperseg
    elif nfft < nperseg:
        raise ValueError('nfft must be greater than or equal to nperseg.')
    else:
        nfft = int(nfft)

    if noverlap is None:
        noverlap = nperseg//2
    else:
        noverlap = int(noverlap)
    if noverlap >= nperseg:
        raise ValueError('noverlap must be less than nperseg.')
    nstep = nperseg - noverlap

    # Padding occurs after boundary extension, so that the extended signal ends
    # in zeros, instead of introducing an impulse at the end.
    # I.e. if x = [..., 3, 2]
    # extend then pad -> [..., 3, 2, 2, 3, 0, 0, 0]
    # pad then extend -> [..., 3, 2, 0, 0, 0, 2, 3]

    if boundary is not None:
        ext_func = boundary_funcs[boundary]
        x = ext_func(x, nperseg//2, axis=-1)
        if not same_data:
            y = ext_func(y, nperseg//2, axis=-1)

    # if padded:
    #     # Pad to integer number of windowed segments
    #     # I.e make x.shape[-1] = nperseg + (nseg-1)*nstep, with integer nseg
    #     nadd = (-(x.shape[-1]-nperseg) % nstep) % nperseg
    #     zeros_shape = list(x.shape[:-1]) + [nadd]
    #     x = np.concatenate((x, np.zeros(zeros_shape)), axis=-1)
    #     if not same_data:
    #         zeros_shape = list(y.shape[:-1]) + [nadd]
    #         y = np.concatenate((y, np.zeros(zeros_shape)), axis=-1)

    # Handle detrending and window functions
    if not detrend:
        def detrend_func(d):
            return d
    elif not hasattr(detrend, '__call__'):
        def detrend_func(d):
            return signaltools.detrend(d, type=detrend, axis=-1)
    elif axis != -1:
        # Wrap this function so that it receives a shape that it could
        # reasonably expect to receive.
        def detrend_func(d):
            d = np.rollaxis(d, -1, axis)
            d = detrend(d)
            return np.rollaxis(d, axis, len(d.shape))
    else:
        detrend_func = detrend

    if np.result_type(win,np.complex64) != outdtype:
        win = win.astype(outdtype)


    if scaling == 'spectrum':
        scale = 1.0 / win.sum()**2
    else:
        raise ValueError('Unknown scaling: %r' % scaling)

    if mode == 'stft':
        scale = np.sqrt(scale)

    if return_onesided:
        if np.iscomplexobj(x):
            sides = 'twosided'
            warnings.warn('Input data is complex, switching to '
                          'return_onesided=False')
        else:
            sides = 'onesided'
            if not same_data:
                if np.iscomplexobj(y):
                    sides = 'twosided'
                    warnings.warn('Input data is complex, switching to '
                                  'return_onesided=False')
    else:
        sides = 'twosided'

    if sides == 'twosided':
        freqs = fftpack.fftfreq(nfft, 1/fs)
    elif sides == 'onesided':
        freqs = np.fft.rfftfreq(nfft, 1/fs)

    # Perform the windowed FFTs
    result = _fft_helper(x, win, detrend_func, nperseg, noverlap, nfft, sides)

    # if not same_data:
    #     # All the same operations on the y data
    #     result_y = _fft_helper(y, win, detrend_func, nperseg, noverlap, nfft,
    #                            sides)
    #     result = np.conjugate(result) * result_y
    # elif mode == 'psd':
    #     result = np.conjugate(result) * result

    result *= scale
    # if sides == 'onesided' and mode == 'psd':
    #     if nfft % 2:
    #         result[..., 1:] *= 2
    #     else:
    #         # Last point is unpaired Nyquist freq point, don't double
    #         result[..., 1:-1] *= 2

    time = np.arange(nperseg/2, x.shape[-1] - nperseg/2 + 1,
                     nperseg - noverlap)/float(fs)
    # if boundary is not None:
    #     time -= (nperseg/2) / fs

    result = result.astype(outdtype)

    # All imaginary parts are zero anyways
    # if same_data and mode != 'stft':
    #     result = result.real

    # Output is going to have new last axis for time/window index, so a
    # negative axis index shifts down one
    if axis < 0:
        axis -= 1

    # Roll frequency axis back to axis where the data came from
    result = np.rollaxis(result, -1, axis)

    return freqs, time, result


def _triage_segments(window, nperseg,input_length):
    """
    Parses window and nperseg arguments for spectrogram and _spectral_helper.
    This is a helper function, not meant to be called externally.

    Parameters
    ---------
    window : string, tuple, or ndarray
        If window is specified by a string or tuple and nperseg is not
        specified, nperseg is set to the default of 256 and returns a window of
        that length.
        If instead the window is array_like and nperseg is not specified, then
        nperseg is set to the length of the window. A ValueError is raised if
        the user supplies both an array_like window and a value for nperseg but
        nperseg does not equal the length of the window.

    nperseg : int
        Length of each segment

    input_length: int
        Length of input signal, i.e. x.shape[-1]. Used to test for errors.

    Returns
    -------
    win : ndarray
        window. If function was called with string or tuple than this will hold
        the actual array used as a window.

    nperseg : int
        Length of each segment. If window is str or tuple, nperseg is set to
        256. If window is array_like, nperseg is set to the length of the
        6
        window.
    """

    #parse window; if array like, then set nperseg = win.shape
    if isinstance(window, string_types) or isinstance(window, tuple):
        # if nperseg not specified
        if nperseg is None:
            nperseg = 256  # then change to default
        if nperseg > input_length:
            warnings.warn('nperseg = {0:d} is greater than input length '
                              ' = {1:d}, using nperseg = {1:d}'
                              .format(nperseg, input_length))
            nperseg = input_length
        win = get_window(window, nperseg)
    return win, nperseg



def _fft_helper(x, win, detrend_func, nperseg, noverlap, nfft, sides):
    """
    Calculate windowed FFT, for internal use by
    scipy.signal._spectral_helper

    This is a helper function that does the main FFT calculation for
    `_spectral helper`. All input validation is performed there, and the
    data axis is assumed to be the last axis of x. It is not designed to
    be called externally. The windows are not averaged over; the result
    from each window is returned.

    Returns
    -------
    result : ndarray
        Array of FFT data

    Notes
    -----
    Adapted from matplotlib.mlab

    .. versionadded:: 0.16.0
    """
    # Created strided array of data segments
    if nperseg == 1 and noverlap == 0:
        result = x[..., np.newaxis]
    else:
        # http://stackoverflow.com/a/5568169
        step = nperseg - noverlap
        shape = x.shape[:-1]+((x.shape[-1]-noverlap)//step, nperseg)
        strides = x.strides[:-1]+(step*x.strides[-1], x.strides[-1])
        result = np.lib.stride_tricks.as_strided(x, shape=shape,
                                                 strides=strides)

    # Detrend each data segment individually
    result = detrend_func(result)

    # Apply window by multiplication
    result = win * result

    # Perform the fft. Acts on last axis by default. Zero-pads automatically
    if sides == 'twosided':
        func = fftpack.fft
    else:
        result = result.real
        func = np.fft.rfft
    result = func(result, n=nfft)

    return result

def const_ext(x, n, axis=-1):

    if n < 1:
        return x
    left_end = axis_slice(x, start=0, stop=1, axis=axis)
    ones_shape = [1] * x.ndim
    ones_shape[axis] = n
    ones = np.ones(ones_shape, dtype=x.dtype)
    left_ext = ones * left_end
    right_end = axis_slice(x, start=-1, axis=axis)
    right_ext = ones * right_end
    ext = np.concatenate((left_ext,
                          x,
                          right_ext),
                         axis=axis)
    return ext
def axis_slice(a, start=None, stop=None, step=None, axis=-1):
    """Take a slice along axis 'axis' from 'a'.

    Parameters
    ----------
    a : numpy.ndarray
        The array to be sliced.
    start, stop, step : int or None
        The slice parameters.
    axis : int, optional
        The axis of `a` to be sliced.

    Examples
    --------
    >>> a = array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    >>> axis_slice(a, start=0, stop=1, axis=1)
    array([[1],
           [4],
           [7]])
    >>> axis_slice(a, start=1, axis=0)
    array([[4, 5, 6],
           [7, 8, 9]])

    Notes
    -----
    The keyword arguments start, stop and step are used by calling
    slice(start, stop, step).  This implies axis_slice() does not
    handle its arguments the exacty the same as indexing.  To select
    a single index k, for example, use
        axis_slice(a, start=k, stop=k+1)
    In this case, the length of the axis 'axis' in the result will
    be 1; the trivial dimension is not removed. (Use numpy.squeeze()
    to remove trivial axes.)
    """
    a_slice = [slice(None)] * a.ndim
    a_slice[axis] = slice(start, stop, step)
    b = a[a_slice]
    return b
