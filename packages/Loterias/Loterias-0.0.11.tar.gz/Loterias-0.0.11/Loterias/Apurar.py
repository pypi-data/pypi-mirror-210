import hashlib
from pandas import DataFrame


class srcVolante:
    """
    Dados de volante para conferencia
    """

    def __init__(self, dezenas=[], id=''):
        # Dados da aposta
        self.id = id
        self.dezenas = []

        # Armazena sorteio/apuracao
        self.apuracao = []

        if type(dezenas) is list:
            self.dezenas = dezenas
        elif type(dezenas) is str:
            self.decompose(dezenas)

    def decompose(self, s=''):
        dz = s.strip().split('	')
        if len(dz) > 0:
            if not dz[0].isdigit():
                self.id = dz.pop(0)

        self.dezenas = []
        self.dezenas = [int(d) for d in dz]

    def hash(self):
        s = ''
        for n in self.dezenas:
            s += f'{n:02}'
        return hashlib.md5(s.encode()).hexdigest()


class Apostas:
    def __init__(self, collection=None):
        self.__collection = collection
        self.apostas = []
        self.__buffer = []

    def add(self, dezenas):
        aps = srcVolante(dezenas=dezenas)
        self.apostas.append(aps)

        self.__check(aposta=aps.dezenas, id=aps.id)

    def __check(self, aposta=[], id=''):
        # verifica uma aposta
        if self.__collection == None:
            return

        vl = self.__collection.values

        cc = list(vl['concurso'])
        dz = list(vl['dezenas'])
        sz = len(cc)

        for i in range(0, sz):
            dd = [int(x) for x in dz[i]]

            acerto = []
            erro = []
            for a in dd:
                if a in aposta:
                    acerto.append(a)
                else:
                    erro.append(a)

            bf = {
                'id': id,
                'aposta': aposta,
                'sorteio': cc[i],
                'dezenas': dd,
                'DZacerto': acerto,
                'DZerro': erro,
                'TTacerto': len(acerto),
                'TTerro': len(erro)
            }

            self.__buffer.append(bf)

    @property
    def buffer(self):
        return self.__buffer

    @property
    def value(self):
        return DataFrame(self.__buffer)
