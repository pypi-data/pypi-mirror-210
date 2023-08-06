"""
Silicon

.. [Phillip1960] H. R. Phillip and E. A. Taft “Optical Constants of Silicon in the Region 1 to 10 eV”.
   In: Phys. Rev. 120 (1 Oct. 1960)
   https://doi.org/10.1103/PhysRev.120.37
"""

from __future__ import annotations

import logging

import pint
from numpy.typing import NDArray
from pint import Quantity

from legendoptics.utils import readdatafile

log = logging.getLogger(__name__)
u = pint.get_application_registry()


def silicon_complex_rindex() -> tuple[Quantity, Quantity, Quantity]:
    """Real and imaginary parts as tuple(wavelength, Re, Im). Measurements from [Phillip1960]_."""
    real = readdatafile("si_rindex_real.dat")
    imag = readdatafile("si_rindex_imag.dat")
    assert (real[0] == imag[0]).all()
    return real[0], real[1], imag[1]
