import numpy as np


def polyfit2d(x, y, z, *, nx=1, ny=1, returnResiduals=False):

    order = max(nx, ny)

    # Convert input lists into numpy arrays if needed
    x = np.array(x) if isinstance(x, list) else x
    y = np.array(y) if isinstance(y, list) else y
    z = np.array(z) if isinstance(z, list) else z

    # Number of coefficients
    N = (nx + 1) * (ny + 1)

    # Matrix-form least-square problem: find X to approach A*X = B
    X = np.ones((nx + 1, ny + 1))
    B = z  # Scattered data to fit a surface from
    A = np.zeros((N, len(B)))

    for index, (i, j) in enumerate(np.ndindex(X.shape)):
        A[index] = x ** i * y ** j if i + j <= order else 0

    coeffs, residuals, _, _ = np.linalg.lstsq(A.T, z, rcond=None)

    if not returnResiduals:
        return coeffs.reshape((nx + 1, ny + 1))
    else:
        return coeffs.reshape((nx + 1, ny + 1)), residuals


def convertRate(rate, outputInputRatio):
    # EG: r[%/hour] = - 100 / [24 hours in a day] * ln(1 - r[%/day] / 100)
    return - 100 * outputInputRatio * np.log(1 - rate / 100)
