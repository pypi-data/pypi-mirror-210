import numpy
from typing import Tuple
from .cigsegy import (Pysegy, collect, fromfile, tofile,
                      create_by_sharing_header)
import warnings


def create(segy_out: str,
           binary_in: str or numpy.ndarray,
           sizeZ: int,
           sizeY: int,
           sizeX: int,
           format: int = 5,
           dt: int = 2000,
           start_time: int = 0,
           X_interval: float = 25,
           Y_interval: float = 25,
           min_iline: int = 1,
           min_xline: int = 1):
    """
    Create a segy format file from a binary file or numpy.ndarray
    
    Parameters:
        - segy_out: str, out segy format file path
        - binary_in: str or numpy.array, the input binary file or array
        - sizeZ: int, number of inline
        - sizeY: int, number of crossline
        - sizeX: int, number of samples per trace
        - format: int, the data format code, 1 for 4 bytes IBM float, 5 for 4 bytes IEEE float
        - dt: int, data sample interval, 2000 means 2ms
        - start_time: int, start time for each trace
        - X_interval: int
        - Y_interval: int
        - min_iline: int, the start inline number
        - min_xline: int, the start crossline number
    """
    if isinstance(binary_in, str):
        segy_create = Pysegy(binary_in, sizeX, sizeY, sizeZ)
    elif isinstance(binary_in, numpy.ndarray):
        if binary_in.shape == (sizeZ, sizeY, sizeX):
            segy_create = Pysegy(sizeX, sizeY, sizeZ)
        else:
            raise RuntimeError(
                f'the binary_in shape: {binary_in.shape} does not match the input dim: ({sizeZ}, {sizeY}, {sizeX})'
            )
    else:
        raise ValueError(
            f'the input argument: binary_in must be a string or numpy array')
    segy_create.setDataFormatCode(format)
    segy_create.setSampleInterval(dt)
    segy_create.setStartTime(start_time)
    segy_create.setXInterval(X_interval)
    segy_create.setYInterval(Y_interval)
    segy_create.setMinInline(min_iline)
    segy_create.setMinCrossline(min_xline)
    if isinstance(binary_in, str):
        segy_create.create(segy_out)
    else:
        segy_create.create(segy_out, binary_in)


def is_sorted(header: numpy.ndarray) -> bool:
    for i in range(header.shape[0] - 1):
        if (header[i, 0], header[i, 1]) >= (header[i + 1, 0], header[i + 1,
                                                                     1]):
            return False

    return True


def step(header: numpy.ndarray) -> Tuple[int, int]:
    warnings.warn(
        "`step()` function is deprecated and will be removed in the future.",
        stacklevel=2)
    iline = numpy.unique(header[:, 0])
    xline = numpy.unique(header[:, 1])
    step1 = iline[2] - iline[1]
    step2 = xline[2] - xline[1]
    if ((iline + step1)[:-1] == iline[1:]).all() and ((xline + step2)[:-1]
                                                      == xline[1:]).all():
        return (step1, step2)
    else:
        return (-1, -1)


def read_unstrict(segy_name, iline, xline) -> numpy.ndarray:
    warnings.warn(
        "`read_unstrict` function is deprecated and will be removed in the future."
        "Please consider use `fromfile(...)` instead.",
        stacklevel=2)
    data, header = collect(segy_name, iline, xline)
    if not is_sorted(header):
        raise RuntimeError("the segy file is unsorted, don't supprt now")

    step1, step2 = step(header)
    if step1 != -1 and step2 != -1:
        ni = (header[:, 0].max() - header[:, 0].min()) / step1 + 1
        nx = (header[:, 1].max() - header[:, 1].min()) / step2 + 1
        nt = data.shape[1]
        if ni * nx != data.shape[0]:
            raise RuntimeError(
                "n-inline * n-crossline != trace_count in this settings")

        data = data.reshape(int(ni), int(nx), nt)
        return data
    else:
        raise RuntimeError("Please use `cigsegy.fromfile()` function")


def read_with_step(segy_name, iline, xline, iline_step,
                   xline_step) -> numpy.ndarray:
    warnings.warn(
        "`read_unstrict` function is deprecated and will be removed in the future."
        "Please consider use `fromfile(..., istep, xstep)` instead.",
        stacklevel=2)
    data, header = collect(segy_name, iline, xline)
    ni = (header[:, 0].max() - header[:, 0].min()) / iline_step + 1
    nx = (header[:, 1].max() - header[:, 1].min()) / xline_step + 1
    nt = data.shape[1]
    if ni * nx != data.shape[0]:
        raise RuntimeError(
            "n-inline * n-crossline != trace_count in this settings")

    data = data.reshape(int(ni), int(nx), nt)
    return data


def eval_xline(segy: Pysegy):
    tracecout = segy.trace_cout()
    options = [193, 17, 21]
    select = [193, 17, 21]
    for op in options:
        segy.setCrosslineLocation(op)
        l = []
        l.append(segy.get_traceInfo(0)[1])
        l.append(segy.get_traceInfo(1)[1])
        l.append(segy.get_traceInfo(2)[1])
        l.append(segy.get_traceInfo(tracecout // 2)[1])
        l.append(segy.get_traceInfo(tracecout - 1)[1])
        if sum([x > 0 for x in l]) != 5:
            select.remove(op)
            continue
        if l[0] == l[1] or l[0] == l[2] or l[1] == l[2]:
            select.remove(op)
            continue
        step = l[1] - l[0]
        if max(l) - min(l) > min((tracecout * step / 10), 10000 * step):
            select.remove(op)
            continue

    if select == []:
        raise RuntimeError("Cannot evaluate crossline location")

    return select


def eval_iline(segy: Pysegy):
    tracecout = segy.trace_cout()
    options = [189, 5, 9, 221]
    select = [189, 5, 9, 221]
    for op in options:
        segy.setInlineLocation(op)
        l0 = segy.get_traceInfo(0)[0]
        ll = segy.get_traceInfo(tracecout - 1)[0]
        l2 = segy.get_traceInfo(tracecout // 2)[0]
        if sum([x > 0 for x in [l0, ll, l2]]) != 3:
            select.remove(op)
            continue
        if l0 == ll or l0 == l2 or ll == l2:
            select.remove(op)
            continue
        if max([l0, ll, l2]) - min([l0, ll, l2]) > tracecout - 1:
            select.remove(op)
            continue
        l1 = segy.get_traceInfo(1)[0]
        ll2 = segy.get_traceInfo(tracecout - 2)[0]
        if l0 != l1 or ll != ll2:
            select.remove(op)
            continue

    if select == []:
        raise RuntimeError("Cannot evaluate inline location")

    return select


def eval_xstep(segy: Pysegy, xline):
    segy.setCrosslineLocation(xline)
    l0 = segy.get_traceInfo(0)[1]
    l1 = segy.get_traceInfo(1)[1]
    l2 = segy.get_traceInfo(2)[1]

    if l2 - l1 != l1 - l0:
        return 0
    else:
        return l2 - l1


def eval_istep(segy: Pysegy, iline):
    segy.setInlineLocation(iline)
    i0 = segy.get_traceInfo(0)[0]
    x1 = 1
    while segy.get_traceInfo(x1)[0] == i0:
        x1 += 1
    i1 = segy.get_traceInfo(x1)[0]

    x2 = x1 + 1
    while segy.get_traceInfo(x2)[0] == i1:
        x2 += 1
    i2 = segy.get_traceInfo(x2)[0]

    if i2 - i1 != i1 - i0:
        return 0
    else:
        return i2 - i1


def guess(segy_name: str):
    """
    guess the locations and steps of inline and crossline

    Parameters:
        - segy_name: str, the input segy file

    return:
    locs: [loc1, loc2, ...], all possible loctaions,
          each location is like: [iline, xline, istep, xstep]
    """
    segy = Pysegy(segy_name)
    xlines = eval_xline(segy)
    ilines = eval_iline(segy)
    xselect = []
    iselect = []
    xsteps = []
    isteps = []

    for xline in xlines:
        xstep = eval_xstep(segy, xline)
        if xstep:
            xselect.append(xline)
            xsteps.append(xstep)

    for iline in ilines:
        istep = eval_istep(segy, iline)
        if istep:
            iselect.append(iline)
            isteps.append(istep)
    segy.close_file()

    out = []
    for i in range(len(iselect)):
        for x in range(len(xselect)):
            try:
                s = Pysegy(segy_name)
                s.setInlineLocation(iselect[i])
                s.setCrosslineLocation(xselect[x])
                s.setSteps(isteps[i], xsteps[x])
                t = s.metaInfo()
            except:
                continue

            out.append([iselect[i], xselect[x], isteps[i], xsteps[x]])

    if out == []:
        raise RuntimeError("cannot guess the location and steps")

    return out


def textual_header(segy_name: str):
    segy = Pysegy(segy_name)
    print(segy.textual_header())
    segy.close_file()


def metaInfo(segy_name: str,
             iline: int = 189,
             xline: int = 193,
             istep: int = 1,
             xstep: int = 1,
             use_guess: bool = False):
    if use_guess:
        [iline, xline, istep, xstep] = guess(segy_name)[0]
    segy = Pysegy(segy_name)
    segy.setInlineLocation(iline)
    segy.setCrosslineLocation(xline)
    segy.setSteps(istep, xstep)
    print(segy.metaInfo())
    segy.close_file()


def fromfile_by_guess(segy_name: str) -> numpy.ndarray:
    """
    reading from a segy file.

    Parameters:
    - segy_name: the input segy file name
    """

    loc = guess(segy_name)

    for l in loc:
        try:
            metaInfo(segy_name, l[0], l[1], l[2], l[3])
            d = fromfile(segy_name, l[0], l[1], l[2], l[3])
            return d
        except:
            continue

    raise RuntimeError(
        "Cannot read by guess location, please specify the location")


def tofile_by_guess(segy_name: str, out_name: str) -> None:
    """
    convert a segy file to a binary file

    Parameters:
    - segy_name: the input segy file name
    - out_name: the output binary file name
    """
    loc = guess(segy_name)
    finish = False

    for l in loc:
        try:
            metaInfo(segy_name, l[0], l[1], l[2], l[3])
            tofile(segy_name, l[0], l[1], l[2], l[3])
            finish = True
            break
        except:
            continue

    if not finish:
        raise RuntimeError(
            "Cannot read by guess location, please specify the location")


def create_by_sharing_header_guess(segy_name: str,
                                   header_segy: str,
                                   src: numpy.ndarray or str,
                                   shape=None) -> None:
    """
    create a segy and its header is from an existed segy.

    Parameters:
    - segy_name: str, the out segy name
    - header_segy: str, the header segy file
    - src: numpy.ndarray, source data
    - shape: if src is str, shape must be specify
    """
    if isinstance(src, str) and shape is None:
        raise ValueError("Shape is None!")

    loc = guess(header_segy)
    finish = False

    for l in loc:
        try:
            if isinstance(src, str):
                create_by_sharing_header(segy_name, header_segy, src, shape,
                                         l[0], l[1], l[2], l[3])
            else:
                create_by_sharing_header(segy_name, header_segy, src, l[0],
                                         l[1], l[2], l[3])
            finish = True
            break
        except:
            continue

    if not finish:
        raise RuntimeError(
            "Cannot read by guess location, please specify the location")
