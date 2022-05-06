import numpy as np

def quantize_precision(points, precision=0.001, DBG=False):
    points /= precision
    points = np.round(points).astype('int32')
    min_bound = points.min(axis=0)
    points -= min_bound
    if DBG: 
        points_dq = (points + min_bound) * precision
        print('quantiztion error:\t', 1000*np.abs(points_dq - points).max(axis=0), 'mm')

    return points


def quantize_resolution(points, resolution=65535, DBG=False):
    min_bound = points.min(axis=0)
    points -= min_bound
    max_bound = points.max()
    points /= max_bound
    points *= resolution
    points = np.round(points).astype('int32')
    if DBG:
        points_dq = points / resolution * max_bound + min_bound
        print('quantiztion error:\t', 1000*np.abs(points_dq - points).max(axis=0), 'mm')

    return points