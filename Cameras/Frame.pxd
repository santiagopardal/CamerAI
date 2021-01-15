cimport numpy as np

cdef class Frame:
    cdef object _time

    cdef np.ndarray _frame

    cdef np.ndarray _resized_and_grayscale
    cdef object _denoised

    cdef list _stored_in