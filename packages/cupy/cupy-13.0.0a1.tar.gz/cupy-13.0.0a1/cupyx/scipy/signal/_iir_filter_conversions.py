""" IIR filter conversion utilities.

Split off _filter_design.py
"""
import warnings

import cupy
from cupyx.scipy.special import binom as comb


class BadCoefficients(UserWarning):
    """Warning about badly conditioned filter coefficients"""
    pass


def _trim_zeros(filt, trim='fb'):
    # https://github.com/numpy/numpy/blob/v1.24.0/numpy/lib/function_base.py#L1800-L1850

    first = 0
    if 'f' in trim:
        for i in filt:
            if i != 0.:
                break
            else:
                first = first + 1

    last = len(filt)
    if 'f' in trim:
        for i in filt[::-1]:
            if i != 0.:
                break
            else:
                last = last - 1
    return filt[first:last]


def _align_nums(nums):
    """Aligns the shapes of multiple numerators.

    Given an array of numerator coefficient arrays [[a_1, a_2,...,
    a_n],..., [b_1, b_2,..., b_m]], this function pads shorter numerator
    arrays with zero's so that all numerators have the same length. Such
    alignment is necessary for functions like 'tf2ss', which needs the
    alignment when dealing with SIMO transfer functions.

    Parameters
    ----------
    nums: array_like
        Numerator or list of numerators. Not necessarily with same length.

    Returns
    -------
    nums: array
        The numerator. If `nums` input was a list of numerators then a 2-D
        array with padded zeros for shorter numerators is returned. Otherwise
        returns ``np.asarray(nums)``.
    """
    try:
        # The statement can throw a ValueError if one
        # of the numerators is a single digit and another
        # is array-like e.g. if nums = [5, [1, 2, 3]]
        nums = cupy.asarray(nums)
        return nums

    except ValueError:
        nums = [cupy.atleast_1d(num) for num in nums]
        max_width = max(num.size for num in nums)

        # pre-allocate
        aligned_nums = cupy.zeros((len(nums), max_width))

        # Create numerators with padded zeros
        for index, num in enumerate(nums):
            aligned_nums[index, -num.size:] = num

        return aligned_nums


def normalize(b, a):
    """Normalize numerator/denominator of a continuous-time transfer function.

    If values of `b` are too close to 0, they are removed. In that case, a
    BadCoefficients warning is emitted.

    Parameters
    ----------
    b: array_like
        Numerator of the transfer function. Can be a 2-D array to normalize
        multiple transfer functions.
    a: array_like
        Denominator of the transfer function. At most 1-D.

    Returns
    -------
    num: array
        The numerator of the normalized transfer function. At least a 1-D
        array. A 2-D array if the input `num` is a 2-D array.
    den: 1-D array
        The denominator of the normalized transfer function.

    Notes
    -----
    Coefficients for both the numerator and denominator should be specified in
    descending exponent order (e.g., ``s^2 + 3s + 5`` would be represented as
    ``[1, 3, 5]``).

    See Also
    --------
    scipy.signal.normalize

    """
    num, den = b, a

    den = cupy.atleast_1d(den)
    num = cupy.atleast_2d(_align_nums(num))

    if den.ndim != 1:
        raise ValueError("Denominator polynomial must be rank-1 array.")
    if num.ndim > 2:
        raise ValueError("Numerator polynomial must be rank-1 or"
                         " rank-2 array.")
    if cupy.all(den == 0):
        raise ValueError("Denominator must have at least on nonzero element.")

    # Trim leading zeros in denominator, leave at least one.
    den = _trim_zeros(den, 'f')

    # Normalize transfer function
    num, den = num / den[0], den / den[0]

    # Count numerator columns that are all zero
    leading_zeros = 0
    for col in num.T:
        if cupy.allclose(col, 0, atol=1e-14):
            leading_zeros += 1
        else:
            break

    # Trim leading zeros of numerator
    if leading_zeros > 0:
        warnings.warn("Badly conditioned filter coefficients (numerator): the "
                      "results may be meaningless", BadCoefficients)
        # Make sure at least one column remains
        if leading_zeros == num.shape[1]:
            leading_zeros -= 1
        num = num[:, leading_zeros:]

    # Squeeze first dimension if singular
    if num.shape[0] == 1:
        num = num[0, :]

    return num, den


def _relative_degree(z, p):
    """
    Return relative degree of transfer function from zeros and poles
    """
    degree = len(p) - len(z)
    if degree < 0:
        raise ValueError("Improper transfer function. "
                         "Must have at least as many poles as zeros.")
    else:
        return degree


def bilinear_zpk(z, p, k, fs):
    r"""
    Return a digital IIR filter from an analog one using a bilinear transform.

    Transform a set of poles and zeros from the analog s-plane to the digital
    z-plane using Tustin's method, which substitutes ``2*fs*(z-1) / (z+1)`` for
    ``s``, maintaining the shape of the frequency response.

    Parameters
    ----------
    z : array_like
        Zeros of the analog filter transfer function.
    p : array_like
        Poles of the analog filter transfer function.
    k : float
        System gain of the analog filter transfer function.
    fs : float
        Sample rate, as ordinary frequency (e.g., hertz). No prewarping is
        done in this function.

    Returns
    -------
    z : ndarray
        Zeros of the transformed digital filter transfer function.
    p : ndarray
        Poles of the transformed digital filter transfer function.
    k : float
        System gain of the transformed digital filter.

    See Also
    --------
    lp2lp_zpk, lp2hp_zpk, lp2bp_zpk, lp2bs_zpk
    bilinear
    scipy.signal.bilinear_zpk

    """
    z = cupy.atleast_1d(z)
    p = cupy.atleast_1d(p)

    degree = _relative_degree(z, p)

    fs2 = 2.0 * fs

    # Bilinear transform the poles and zeros
    z_z = (fs2 + z) / (fs2 - z)
    p_z = (fs2 + p) / (fs2 - p)

    # Any zeros that were at infinity get moved to the Nyquist frequency
    z_z = cupy.append(z_z, -cupy.ones(degree))

    # Compensate for gain change
    k_z = k * (cupy.prod(fs2 - z) / cupy.prod(fs2 - p)).real

    return z_z, p_z, k_z


def lp2lp_zpk(z, p, k, wo=1.0):
    r"""
    Transform a lowpass filter prototype to a different frequency.

    Return an analog low-pass filter with cutoff frequency `wo`
    from an analog low-pass filter prototype with unity cutoff frequency,
    using zeros, poles, and gain ('zpk') representation.

    Parameters
    ----------
    z : array_like
        Zeros of the analog filter transfer function.
    p : array_like
        Poles of the analog filter transfer function.
    k : float
        System gain of the analog filter transfer function.
    wo : float
        Desired cutoff, as angular frequency (e.g., rad/s).
        Defaults to no change.

    Returns
    -------
    z : ndarray
        Zeros of the transformed low-pass filter transfer function.
    p : ndarray
        Poles of the transformed low-pass filter transfer function.
    k : float
        System gain of the transformed low-pass filter.

    See Also
    --------
    lp2hp_zpk, lp2bp_zpk, lp2bs_zpk, bilinear
    lp2lp
    scipy.signal.lp2lp_zpk

    """
    z = cupy.atleast_1d(z)
    p = cupy.atleast_1d(p)
    wo = float(wo)  # Avoid int wraparound

    degree = _relative_degree(z, p)

    # Scale all points radially from origin to shift cutoff frequency
    z_lp = wo * z
    p_lp = wo * p

    # Each shifted pole decreases gain by wo, each shifted zero increases it.
    # Cancel out the net change to keep overall gain the same
    k_lp = k * wo**degree

    return z_lp, p_lp, k_lp


def lp2hp_zpk(z, p, k, wo=1.0):
    r"""
    Transform a lowpass filter prototype to a highpass filter.

    Return an analog high-pass filter with cutoff frequency `wo`
    from an analog low-pass filter prototype with unity cutoff frequency,
    using zeros, poles, and gain ('zpk') representation.

    Parameters
    ----------
    z : array_like
        Zeros of the analog filter transfer function.
    p : array_like
        Poles of the analog filter transfer function.
    k : float
        System gain of the analog filter transfer function.
    wo : float
        Desired cutoff, as angular frequency (e.g., rad/s).
        Defaults to no change.

    Returns
    -------
    z : ndarray
        Zeros of the transformed high-pass filter transfer function.
    p : ndarray
        Poles of the transformed high-pass filter transfer function.
    k : float
        System gain of the transformed high-pass filter.

    See Also
    --------
    lp2lp_zpk, lp2bp_zpk, lp2bs_zpk, bilinear
    lp2hp
    scipy.signal.lp2hp_zpk

    Notes
    -----
    This is derived from the s-plane substitution

    .. math:: s \rightarrow \frac{\omega_0}{s}

    This maintains symmetry of the lowpass and highpass responses on a
    logarithmic scale.

    """
    z = cupy.atleast_1d(z)
    p = cupy.atleast_1d(p)
    wo = float(wo)

    degree = _relative_degree(z, p)

    # Invert positions radially about unit circle to convert LPF to HPF
    # Scale all points radially from origin to shift cutoff frequency
    z_hp = wo / z
    p_hp = wo / p

    # If lowpass had zeros at infinity, inverting moves them to origin.
    z_hp = cupy.append(z_hp, cupy.zeros(degree))

    # Cancel out gain change caused by inversion
    k_hp = k * cupy.real(cupy.prod(-z) / cupy.prod(-p))

    return z_hp, p_hp, k_hp


def lp2bp_zpk(z, p, k, wo=1.0, bw=1.0):
    r"""
    Transform a lowpass filter prototype to a bandpass filter.

    Return an analog band-pass filter with center frequency `wo` and
    bandwidth `bw` from an analog low-pass filter prototype with unity
    cutoff frequency, using zeros, poles, and gain ('zpk') representation.

    Parameters
    ----------
    z : array_like
        Zeros of the analog filter transfer function.
    p : array_like
        Poles of the analog filter transfer function.
    k : float
        System gain of the analog filter transfer function.
    wo : float
        Desired passband center, as angular frequency (e.g., rad/s).
        Defaults to no change.
    bw : float
        Desired passband width, as angular frequency (e.g., rad/s).
        Defaults to 1.

    Returns
    -------
    z : ndarray
        Zeros of the transformed band-pass filter transfer function.
    p : ndarray
        Poles of the transformed band-pass filter transfer function.
    k : float
        System gain of the transformed band-pass filter.

    See Also
    --------
    lp2lp_zpk, lp2hp_zpk, lp2bs_zpk, bilinear
    lp2bp
    scipy.signal.lp2bp_zpk

    Notes
    -----
    This is derived from the s-plane substitution

    .. math:: s \rightarrow \frac{s^2 + {\omega_0}^2}{s \cdot \mathrm{BW}}

    This is the "wideband" transformation, producing a passband with
    geometric (log frequency) symmetry about `wo`.

    """
    z = cupy.atleast_1d(z)
    p = cupy.atleast_1d(p)
    wo = float(wo)
    bw = float(bw)

    degree = _relative_degree(z, p)

    # Scale poles and zeros to desired bandwidth
    z_lp = z * bw/2
    p_lp = p * bw/2

    # Square root needs to produce complex result, not NaN
    z_lp = z_lp.astype(complex)
    p_lp = p_lp.astype(complex)

    # Duplicate poles and zeros and shift from baseband to +wo and -wo
    z_bp = cupy.concatenate((z_lp + cupy.sqrt(z_lp**2 - wo**2),
                             z_lp - cupy.sqrt(z_lp**2 - wo**2)))
    p_bp = cupy.concatenate((p_lp + cupy.sqrt(p_lp**2 - wo**2),
                             p_lp - cupy.sqrt(p_lp**2 - wo**2)))

    # Move degree zeros to origin, leaving degree zeros at infinity for BPF
    z_bp = cupy.append(z_bp, cupy.zeros(degree))

    # Cancel out gain change from frequency scaling
    k_bp = k * bw**degree

    return z_bp, p_bp, k_bp


def lp2bs_zpk(z, p, k, wo=1.0, bw=1.0):
    r"""
    Transform a lowpass filter prototype to a bandstop filter.

    Return an analog band-stop filter with center frequency `wo` and
    stopband width `bw` from an analog low-pass filter prototype with unity
    cutoff frequency, using zeros, poles, and gain ('zpk') representation.

    Parameters
    ----------
    z : array_like
        Zeros of the analog filter transfer function.
    p : array_like
        Poles of the analog filter transfer function.
    k : float
        System gain of the analog filter transfer function.
    wo : float
        Desired stopband center, as angular frequency (e.g., rad/s).
        Defaults to no change.
    bw : float
        Desired stopband width, as angular frequency (e.g., rad/s).
        Defaults to 1.

    Returns
    -------
    z : ndarray
        Zeros of the transformed band-stop filter transfer function.
    p : ndarray
        Poles of the transformed band-stop filter transfer function.
    k : float
        System gain of the transformed band-stop filter.

    See Also
    --------
    lp2lp_zpk, lp2hp_zpk, lp2bp_zpk, bilinear
    lp2bs
    scipy.signal.lp2bs_zpk

    Notes
    -----
    This is derived from the s-plane substitution

    .. math:: s \rightarrow \frac{s \cdot \mathrm{BW}}{s^2 + {\omega_0}^2}

    This is the "wideband" transformation, producing a stopband with
    geometric (log frequency) symmetry about `wo`.

    """
    z = cupy.atleast_1d(z)
    p = cupy.atleast_1d(p)
    wo = float(wo)
    bw = float(bw)

    degree = _relative_degree(z, p)

    # Invert to a highpass filter with desired bandwidth
    z_hp = (bw/2) / z
    p_hp = (bw/2) / p

    # Square root needs to produce complex result, not NaN
    z_hp = z_hp.astype(complex)
    p_hp = p_hp.astype(complex)

    # Duplicate poles and zeros and shift from baseband to +wo and -wo
    z_bs = cupy.concatenate((z_hp + cupy.sqrt(z_hp**2 - wo**2),
                             z_hp - cupy.sqrt(z_hp**2 - wo**2)))
    p_bs = cupy.concatenate((p_hp + cupy.sqrt(p_hp**2 - wo**2),
                             p_hp - cupy.sqrt(p_hp**2 - wo**2)))

    # Move any zeros that were at infinity to the center of the stopband
    z_bs = cupy.append(z_bs, cupy.full(degree, +1j*wo))
    z_bs = cupy.append(z_bs, cupy.full(degree, -1j*wo))

    # Cancel out gain change caused by inversion
    k_bs = k * cupy.real(cupy.prod(-z) / cupy.prod(-p))

    return z_bs, p_bs, k_bs


def bilinear(b, a, fs=1.0):
    r"""
    Return a digital IIR filter from an analog one using a bilinear transform.

    Transform a set of poles and zeros from the analog s-plane to the digital
    z-plane using Tustin's method, which substitutes ``2*fs*(z-1) / (z+1)`` for
    ``s``, maintaining the shape of the frequency response.

    Parameters
    ----------
    b : array_like
        Numerator of the analog filter transfer function.
    a : array_like
        Denominator of the analog filter transfer function.
    fs : float
        Sample rate, as ordinary frequency (e.g., hertz). No prewarping is
        done in this function.

    Returns
    -------
    b : ndarray
        Numerator of the transformed digital filter transfer function.
    a : ndarray
        Denominator of the transformed digital filter transfer function.

    See Also
    --------
    lp2lp, lp2hp, lp2bp, lp2bs
    bilinear_zpk
    scipy.signal.bilinear

    """
    fs = float(fs)
    a, b = map(cupy.atleast_1d, (a, b))
    D = a.shape[0] - 1
    N = b.shape[0] - 1

    M = max(N, D)
    Np, Dp = M, M

    bprime = cupy.empty(Np + 1, float)
    aprime = cupy.empty(Dp + 1, float)

    # XXX (ev-br): worth turning into a ufunc invocation? (loops are short)
    for j in range(Dp + 1):
        val = 0.0
        for i in range(N + 1):
            bNi = b[N - i] * (2 * fs)**i
            for k in range(i + 1):
                for s in range(M - i + 1):
                    if k + s == j:
                        val += comb(i, k) * comb(M - i, s) * bNi * (-1)**k
        bprime[j] = cupy.real(val)

    for j in range(Dp + 1):
        val = 0.0
        for i in range(D + 1):
            aDi = a[D - i] * (2 * fs)**i
            for k in range(i + 1):
                for s in range(M - i + 1):
                    if k + s == j:
                        val += comb(i, k) * comb(M - i, s) * aDi * (-1)**k
        aprime[j] = cupy.real(val)

    return normalize(bprime, aprime)


def lp2lp(b, a, wo=1.0):
    r"""
    Transform a lowpass filter prototype to a different frequency.

    Return an analog low-pass filter with cutoff frequency `wo`
    from an analog low-pass filter prototype with unity cutoff frequency, in
    transfer function ('ba') representation.

    Parameters
    ----------
    b : array_like
        Numerator polynomial coefficients.
    a : array_like
        Denominator polynomial coefficients.
    wo : float
        Desired cutoff, as angular frequency (e.g. rad/s).
        Defaults to no change.

    Returns
    -------
    b : array_like
        Numerator polynomial coefficients of the transformed low-pass filter.
    a : array_like
        Denominator polynomial coefficients of the transformed low-pass filter.

    See Also
    --------
    lp2hp, lp2bp, lp2bs, bilinear
    lp2lp_zpk
    scipy.signal.lp2lp

    Notes
    -----
    This is derived from the s-plane substitution

    .. math:: s \rightarrow \frac{s}{\omega_0}

    """
    a, b = map(cupy.atleast_1d, (a, b))
    try:
        wo = float(wo)
    except TypeError:
        wo = float(wo[0])
    d = len(a)
    n = len(b)
    M = max(d, n)
    pwo = wo ** cupy.arange(M - 1, -1, -1)
    start1 = max((n - d, 0))
    start2 = max((d - n, 0))
    b = b * pwo[start1] / pwo[start2:]
    a = a * pwo[start1] / pwo[start1:]
    return normalize(b, a)


def lp2hp(b, a, wo=1.0):
    r"""
    Transform a lowpass filter prototype to a highpass filter.

    Return an analog high-pass filter with cutoff frequency `wo`
    from an analog low-pass filter prototype with unity cutoff frequency, in
    transfer function ('ba') representation.

    Parameters
    ----------
    b : array_like
        Numerator polynomial coefficients.
    a : array_like
        Denominator polynomial coefficients.
    wo : float
        Desired cutoff, as angular frequency (e.g., rad/s).
        Defaults to no change.

    Returns
    -------
    b : array_like
        Numerator polynomial coefficients of the transformed high-pass filter.
    a : array_like
        Denominator polynomial coefficients of the transformed high-pass
        filter.

    See Also
    --------
    lp2lp, lp2bp, lp2bs, bilinear
    lp2hp_zpk
    scipy.signal.lp2hp

    Notes
    -----
    This is derived from the s-plane substitution

    .. math:: s \rightarrow \frac{\omega_0}{s}

    This maintains symmetry of the lowpass and highpass responses on a
    logarithmic scale.
    """
    a, b = map(cupy.atleast_1d, (a, b))
    try:
        wo = float(wo)
    except TypeError:
        wo = float(wo[0])
    d = len(a)
    n = len(b)
    if wo != 1:
        pwo = wo ** cupy.arange(max(d, n))
    else:
        pwo = cupy.ones(max(d, n), b.dtype)
    if d >= n:
        outa = a[::-1] * pwo
        outb = cupy.resize(b, (d,))
        outb[n:] = 0.0
        outb[:n] = b[::-1] * pwo[:n]
    else:
        outb = b[::-1] * pwo
        outa = cupy.resize(a, (n,))
        outa[d:] = 0.0
        outa[:d] = a[::-1] * pwo[:d]

    return normalize(outb, outa)


def lp2bp(b, a, wo=1.0, bw=1.0):
    r"""
    Transform a lowpass filter prototype to a bandpass filter.

    Return an analog band-pass filter with center frequency `wo` and
    bandwidth `bw` from an analog low-pass filter prototype with unity
    cutoff frequency, in transfer function ('ba') representation.

    Parameters
    ----------
    b : array_like
        Numerator polynomial coefficients.
    a : array_like
        Denominator polynomial coefficients.
    wo : float
        Desired passband center, as angular frequency (e.g., rad/s).
        Defaults to no change.
    bw : float
        Desired passband width, as angular frequency (e.g., rad/s).
        Defaults to 1.

    Returns
    -------
    b : array_like
        Numerator polynomial coefficients of the transformed band-pass filter.
    a : array_like
        Denominator polynomial coefficients of the transformed band-pass
        filter.

    See Also
    --------
    lp2lp, lp2hp, lp2bs, bilinear
    lp2bp_zpk
    scipy.signal.lp2bp

    Notes
    -----
    This is derived from the s-plane substitution

    .. math:: s \rightarrow \frac{s^2 + {\omega_0}^2}{s \cdot \mathrm{BW}}

    This is the "wideband" transformation, producing a passband with
    geometric (log frequency) symmetry about `wo`.

    """
    a, b = map(cupy.atleast_1d, (a, b))
    D = len(a) - 1
    N = len(b) - 1
    artype = cupy.mintypecode((a.dtype, b.dtype))
    ma = max(N, D)
    Np = N + ma
    Dp = D + ma
    bprime = cupy.empty(Np + 1, artype)
    aprime = cupy.empty(Dp + 1, artype)
    wosq = wo * wo
    for j in range(Np + 1):
        val = 0.0
        for i in range(0, N + 1):
            for k in range(0, i + 1):
                if ma - i + 2 * k == j:
                    val += comb(i, k) * b[N - i] * (wosq) ** (i - k) / bw ** i
        bprime[Np - j] = val

    for j in range(Dp + 1):
        val = 0.0
        for i in range(0, D + 1):
            for k in range(0, i + 1):
                if ma - i + 2 * k == j:
                    val += comb(i, k) * a[D - i] * (wosq) ** (i - k) / bw ** i
        aprime[Dp - j] = val

    return normalize(bprime, aprime)


def lp2bs(b, a, wo=1.0, bw=1.0):
    r"""
    Transform a lowpass filter prototype to a bandstop filter.

    Return an analog band-stop filter with center frequency `wo` and
    bandwidth `bw` from an analog low-pass filter prototype with unity
    cutoff frequency, in transfer function ('ba') representation.

    Parameters
    ----------
    b : array_like
        Numerator polynomial coefficients.
    a : array_like
        Denominator polynomial coefficients.
    wo : float
        Desired stopband center, as angular frequency (e.g., rad/s).
        Defaults to no change.
    bw : float
        Desired stopband width, as angular frequency (e.g., rad/s).
        Defaults to 1.

    Returns
    -------
    b : array_like
        Numerator polynomial coefficients of the transformed band-stop filter.
    a : array_like
        Denominator polynomial coefficients of the transformed band-stop
        filter.

    See Also
    --------
    lp2lp, lp2hp, lp2bp, bilinear
    lp2bs_zpk
    scipy.signal.lp2bs

    Notes
    -----
    This is derived from the s-plane substitution

    .. math:: s \rightarrow \frac{s \cdot \mathrm{BW}}{s^2 + {\omega_0}^2}

    This is the "wideband" transformation, producing a stopband with
    geometric (log frequency) symmetry about `wo`.
    """
    a, b = map(cupy.atleast_1d, (a, b))
    D = len(a) - 1
    N = len(b) - 1
    artype = cupy.mintypecode((a.dtype, b.dtype))
    M = max(N, D)
    Np = M + M
    Dp = M + M
    bprime = cupy.empty(Np + 1, artype)
    aprime = cupy.empty(Dp + 1, artype)
    wosq = wo * wo
    for j in range(Np + 1):
        val = 0.0
        for i in range(0, N + 1):
            for k in range(0, M - i + 1):
                if i + 2 * k == j:
                    val += (comb(M - i, k) * b[N - i] *
                            (wosq) ** (M - i - k) * bw ** i)
        bprime[Np - j] = val

    for j in range(Dp + 1):
        val = 0.0
        for i in range(0, D + 1):
            for k in range(0, M - i + 1):
                if i + 2 * k == j:
                    val += (comb(M - i, k) * a[D - i] *
                            (wosq) ** (M - i - k) * bw ** i)
        aprime[Dp - j] = val

    return normalize(bprime, aprime)
