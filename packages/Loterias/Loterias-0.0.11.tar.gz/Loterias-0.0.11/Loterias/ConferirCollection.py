import pandas as pd
from .Collections import CollectionByType, CollectionType

class ConfereCollection:
    def __init__(self, collectioType=CollectionType.LotoMania, sorteioInicial=1, sorteioFinal=1):
        self.sorteioInicial = sorteioInicial
        self.sorteioFinal = sorteioFinal
        self.apostas = {}

        #Parei aqui
        self.__collection = CollectionByType(collectioType)

    def add(self, nsb='', dezenas=[]):
        if (nsb == '') or (len(dezenas) < 1):
            return
        self.apostas.update({f'{nsb.upper()}': dezenas})

    @property
    def getApostas(self):
        apostas = self.apostas

        value = []
        for k in apostas.keys():
            value.append({'id': k, 'dz': str(apostas[k])})

        return pd.DataFrame(value) #[id, dz], columns=['id', 'dz'])



    def showSetup(self):
        concursos = self.__collection.conferirListar(self.sorteioInicial, self.sorteioFinal)
        print('     Sorteio inicial ', self.sorteioInicial)
        print('     Sorteio final   ', self.sorteioFinal)
        print('     Concursos       ', concursos)
        print(' DEZENAS')
        print(self.getApostas)

    #@property
    def getConferencia(self):
        concursos = self.__collection.conferirListar(self.sorteioInicial, self.sorteioFinal)
        self.__collection.sorteioInicial = self.sorteioInicial

        r = {}
        for k in self.apostas.keys():
            p = self.__collection.conferir(dezenas=self.apostas[k], apostaID=k, concursos=concursos)
            r.update({k: p})

        return r