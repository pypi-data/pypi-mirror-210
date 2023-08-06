"""
Contem todas as coleções de sorteios
"""
from .Loto import ExportLoteriaBase
from .Loto import MegaSena
from .Loto import LotoFacil
from .Loto import Quina
from .Loto import LotoMania
from .Loto import TimeMania
from .Loto import DuplaSena
from .Loto import Federal
from .Loto import Loteca
from .Loto import DiaDeSorte
from .Loto import SuperSet

from .Collection import Collection


class CollectionDiaDeSorte(Collection):
    def __init__(self, maxThreads=8, concursoStart=1, verbose=False, autoStart=False):
        super().__init__(DiaDeSorte, maxThreads=maxThreads, concursoStart=concursoStart, verbose=verbose,
                         autoStart=autoStart)


class CollectionDuplaSena(Collection):
    def __init__(self, maxThreads=8, concursoStart=1, verbose=False, autoStart=False):
        super().__init__(DuplaSena, maxThreads=maxThreads, concursoStart=concursoStart, verbose=verbose,
                         autoStart=autoStart)


class CollectionFederal(Collection):
    def __init__(self, maxThreads=8, concursoStart=1, verbose=False, autoStart=False):
        super().__init__(Federal, maxThreads=maxThreads, concursoStart=concursoStart, verbose=verbose,
                         autoStart=autoStart)


class CollectionLoteca(Collection):
    def __init__(self, maxThreads=8, concursoStart=1, verbose=False, autoStart=False):
        super().__init__(Loteca, maxThreads=maxThreads, concursoStart=concursoStart, verbose=verbose,
                         autoStart=autoStart)


class CollectionLotoFacil(Collection):
    def __init__(self, maxThreads=8, concursoStart=1, verbose=False, autoStart=False):
        super().__init__(LotoFacil, maxThreads=maxThreads, concursoStart=concursoStart, verbose=verbose,
                         autoStart=autoStart)


class CollectionLotoMania(Collection):
    def __init__(self, maxThreads=8, concursoStart=1, verbose=False, autoStart=False):
        super().__init__(LotoMania, maxThreads=maxThreads, concursoStart=concursoStart, verbose=verbose,
                         autoStart=autoStart)


class CollectionMegaSena(Collection):
    def __init__(self, maxThreads=8, concursoStart=1, verbose=False, autoStart=False):
        super().__init__(MegaSena, maxThreads=maxThreads, concursoStart=concursoStart, verbose=verbose,
                         autoStart=autoStart)


class CollectionQuina(Collection):
    def __init__(self, maxThreads=8, concursoStart=1, verbose=False, autoStart=False):
        super().__init__(Quina, maxThreads=maxThreads, concursoStart=concursoStart, verbose=verbose,
                         autoStart=autoStart)


class CollectionSuperSet(Collection):
    def __init__(self, maxThreads=8, concursoStart=1, verbose=False, autoStart=False):
        super().__init__(SuperSet, maxThreads=maxThreads, concursoStart=concursoStart, verbose=verbose,
                         autoStart=autoStart)


class CollectionTimeMania(Collection):
    def __init__(self, maxThreads=8, concursoStart=1, verbose=False, autoStart=False):
        super().__init__(TimeMania, maxThreads=maxThreads, concursoStart=concursoStart, verbose=verbose,
                         autoStart=autoStart)


class _CollectionType:
    @property
    def DiaDeSorte(self):
        return 0

    @property
    def DuplaSena(self):
        return 1

    @property
    def Federal(self):
        return 2

    @property
    def Loteca(self):
        return 3

    @property
    def LotoFacil(self):
        return 4

    @property
    def LotoMania(self):
        return 5

    @property
    def MegaSena(self):
        return 6

    @property
    def Quina(self):
        return 7

    @property
    def SuperSet(self):
        return 8

    @property
    def TimeMania(self):
        return 9


CollectionType = _CollectionType()


def CollectionByType(typed=CollectionType.DiaDeSorte, maxThreads=8, concursoStart=1, verbose=False,
                     autoStart=False) -> Collection:
    r = [
        CollectionDiaDeSorte(maxThreads, concursoStart, verbose, autoStart),
        CollectionDuplaSena(maxThreads, concursoStart, verbose, autoStart),
        CollectionFederal(maxThreads, concursoStart, verbose, autoStart),
        CollectionLoteca(maxThreads, concursoStart, verbose, autoStart),
        CollectionLotoFacil(maxThreads, concursoStart, verbose, autoStart),
        CollectionLotoMania(maxThreads, concursoStart, verbose, autoStart),
        CollectionMegaSena(maxThreads, concursoStart, verbose, autoStart),
        CollectionQuina(maxThreads, concursoStart, verbose, autoStart),
        CollectionSuperSet(maxThreads, concursoStart, verbose, autoStart),
        CollectionTimeMania(maxThreads, concursoStart, verbose, autoStart)
    ]
    return r[typed]


def LoteriaByType(typed=CollectionType.DiaDeSorte, concursoStart='') -> ExportLoteriaBase:
    r = [
        DiaDeSorte(concursoStart),
        DuplaSena(concursoStart),
        Federal(concursoStart),
        Loteca(concursoStart),
        LotoFacil(concursoStart),
        LotoMania(concursoStart),
        MegaSena(concursoStart),
        Quina(concursoStart),
        SuperSet(concursoStart),
        TimeMania(concursoStart)
    ]
    return r[typed]
