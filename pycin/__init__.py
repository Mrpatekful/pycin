"""

@author:    Patrik Purgai
@copyright: Copyright 2019, pycin
@license:   MIT
@email:     purgai.patrik@gmail.com
@date:      2019.02.24.
"""

from .pycin import search_events, fetch_cinemas
from .pycin import (ALBA, ALLE, ARENA,
                    BALATON, CAMPONA, DEBRECEN,
                    DUNA_PLAZA, GYOR, MISKOLC,
                    NYIREGYHAZA, PECS, SAVARIA,
                    SOPRON, SZEGED, SZOLNOK,
                    WESTEND, ZALAEGERSZEG)
from .pycin import CINEMAS, BUDAPEST_CINEMAS



__all__ = [
    'search_events',
    'fetch_cinemas',
    'ALBA', 
    'ALLE', 
    'ARENA',
    'BALATON', 
    'CAMPONA', 
    'DEBRECEN',
    'DUNA_PLAZA', 
    'GYOR', 
    'MISKOLC',
    'NYIREGYHAZA',
    'PECS', 
    'SAVARIA',
    'SOPRON', 
    'SZEGED', 
    'SZOLNOK',
    'WESTEND', 
    'ZALAEGERSZEG',
    'CINEMAS',
    'BUDAPEST_CINEMAS'
]