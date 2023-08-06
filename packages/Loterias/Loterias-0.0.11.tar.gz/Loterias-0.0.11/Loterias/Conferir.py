#import pandas as pd

#from .Collections import CollectionByType, CollectionType

class Verificar:
    def __init__(self, sorteadas=[], apostadas=[]):
        self.sorteadas = sorteadas
        self.apostadas = apostadas

class Verificado:
    def __init__(self, dezenas=[]):
        self.dezenas = dezenas

    @property
    def count(self):
        return len(self.dezenas)

class Conferido:
    def __init__(self, apostaID='', concurso=0, dezenasSorteadas=[], dezenasApostadas=[], premiacao={}):
        self.apostaID = apostaID
        self.concurso = concurso
        self.dezenas = Verificar(sorteadas=dezenasSorteadas, apostadas=dezenasApostadas)
        self.acertos = Verificado()
        self.erros = Verificado()
        self.__premiacao = premiacao
        self.premiado = False

        if self.isReady():
            self.doProcess()

    def isReady(self) -> bool:
        return (self.acertos.count > 0) and (self.erros.count > 0)

    def doProcess(self):
        self.acertos.dezenas = []
        self.erros.dezenas = []

        def __intraChecker(v):
            if v in self.dezenas.apostadas:
                self.acertos.dezenas.append(v)
            else:
                self.erros.dezenas.append(v)

        [__intraChecker(dz) for dz in self.dezenas.sorteadas]

        #Se o critério de premiação foi informado, faz a verificação
        if len(self.__premiacao) > 0:
            self.premiado = (self.acertos.count > self.__premiacao['minimo'])

            #Se a premiação por nenhum acerto for ativada, confere nesse sentido também
            if not self.premiado and self.__premiacao['zero']:
                self.premiado = (self.acertos.count == 0)

    @property
    def getData(self):
        """
            Prepara dados para Dataframe
        :return:
            Retorna valor [linha] para constituir Dataframe
        """

        r = {}

        r.update({'concurso': self.concurso})

        r.update({'apostaID': self.apostaID})

        #Transporta as dezenas
        #[r.update({f'dz{i}': self.dezenas.sorteadas[i]}) for i in range(0, len(self.dezenas.sorteadas))]

        r.update({'DezenasSorteadas': self.dezenas.sorteadas})

        r.update({'DezenasApostadas': self.dezenas.apostadas})

        #Adiciona acertos
        r.update({'AcertosCount': self.acertos.count})

        # Adiciona acertos
        r.update({'ErrosCount': self.erros.count})

        #Transporta acertos
        r.update({'AcertosDz': self.acertos.dezenas})
        #[r.update({f'AcertoDz{i}': self.acertos.dezenas[i]}) for i in range(0, self.acertos.count)]

        #Transporta erros
        r.update({'ErrosDz': self.erros.dezenas})

        #Transporta informação sobre premiacao
        r.update({'premiado': self.premiado})

        return r


