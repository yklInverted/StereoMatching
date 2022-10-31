import numpy as np
import cv2
from numpy.lib.stride_tricks import as_strided


def sumOfSquaredDiff(image, template, mask=None):
    if mask is None:
        mask = np.ones_like(template)
    window_size = template.shape

    updatedImage = as_strided(image, shape=(image.shape[0] - window_size[0] + 1, image.shape[1] - window_size[1] + 1,) +
                                           window_size, strides=image.strides * 2)

    # Compute the sum of squared differences
    ssd = ((updatedImage - template) ** 2 * mask).sum(axis=-1).sum(axis=-1)
    return ssd


def disparity_ssd(left, right, templateSize, window, lambdaValue):
    im_rows, im_cols = left.shape
    tpl_rows = tpl_cols = templateSize
    disparity = np.zeros(left.shape, dtype=np.float32)

    for r in range(int(tpl_rows/2), im_rows-int(tpl_rows/2)):
        tr_min, tr_max = int(max(r-tpl_rows/2, 0)), int(min(r+tpl_rows/2+1, im_rows))
        for c in range(int(tpl_cols/2), im_cols-int(tpl_cols/2)):
            tc_min = int(max(c-tpl_cols/2, 0))
            tc_max = int(min(c+tpl_cols/2+1, im_cols))
            tpl = left[tr_min:tr_max, tc_min:tc_max].astype(np.float32)
            rc_min = int(max(c - window / 2, 0))
            rc_max = int(min(c + window / 2 + 1, im_cols))
            R_strip = right[tr_min:tr_max, rc_min:rc_max].astype(np.float32)
            error = sumOfSquaredDiff(R_strip, tpl)
            c_tf = max(c-rc_min-tpl_cols/2, 0)
            dist = np.arange(error.shape[1]) - c_tf
            cost = error + np.abs(dist * lambdaValue)
            _,_,min_loc,_ = cv2.minMaxLoc(cost)
            disparity[r, c] = dist[min_loc[0]]
    return disparity