
import sys
from threading import Thread
#from pandas import DataFrame
import pandas as pd
from .Loto import ExportLoteriaBase
# from .Volante import Volantes
from .Apurar import Apostas

from .Conferir import Conferido

import warnings
warnings.filterwarnings('ignore')

class srcThread(Thread):
    '''
    Executa dados via Thread sem misturar valores externos
    '''

    def __init__(self, thNdx=-1, loteriaBase=ExportLoteriaBase(), concurso=0, callProcess=None, autoStart=False):
        Thread.__init__(self)
        self.index = thNdx
        self.lb = loteriaBase
        self.lb.concurso = concurso
        self.stop = False
        self.callProcess = callProcess

        if autoStart and (thNdx >= 0):
            self.start()

    def run(self) -> None:
        while not self.stop:
            if not self.stop and self.callProcess:
                self.stop = self.callProcess(self)

class srcCounter:
    def __init__(self, dezenas=0):
        self.__dezenas = dezenas
        self.soma = []
        self.cont = []

        #Lista para integrar o dicionário final
        self.finalSoma = []
        self.finalCont = []

        self.doMake()

    def doMake(self):
        self.soma = [0 for i in range(0, self.__dezenas)]
        self.cont = [0 for i in range(0, self.__dezenas)]

    def resetCont(self):
        self.cont = [0 for i in range(0, self.__dezenas)]

    def calculate(self, v):
        self.soma[v] += 1
        self.cont[v] += 1

    @property
    def getDict(self):
        soma = {}
        cont = {}

        def __process(i):
            soma.update({f'smDz{i}': self.soma[i]})
            cont.update({f'ctDz{i}': self.cont[i]})

        #for i in range(0, self.__dezenas):
        #    soma.update({f'smDz{i}': self.soma[i]})
        #    cont.update({f'ctDz{i}': self.cont[i]})
        [__process(i) for i in range(0, self.__dezenas)]

        r = {}
        r.update(soma)
        r.update(cont)
        return r

class Collection:
    def __init__(self, loteriaBase=ExportLoteriaBase, maxThreads=8, concursoStart=1, verbose=False, autoStart=False):
        self.buffer = []

        self.__repescar = []
        self.__th = []
        self.__lb = loteriaBase
        self.__concursoStart = concursoStart

        if concursoStart < 1:
            self.__concursoStart = 1

        self.__concursoAtual = self.__concursoStart
        self.__thMax = 0

        #Soma individual de sorteios
        self.contagem = [0 for s in range(0, self.__lb().volante.dezenas)]

        self.verbose = verbose

        lb = loteriaBase()
        self.__ultimoSorteio = lb.numero()
        self.__concursoMax = self.__ultimoSorteio

        self.maxThreads = maxThreads

        self.apostas = Apostas(self)  # Volantes(self)

        if autoStart:
            self.start()

    @property
    def jogo(self):
        return self.__lb().jogo

    @property
    def __verbose(self):
        pass

    @__verbose.setter
    def __verbose(self, v):
        if self.verbose:
            sys.stdout.write('\r' + v)
            sys.stdout.flush()

    @property
    def sorteioInicial(self):
        return self.__concursoStart

    @sorteioInicial.setter
    def sorteioInicial(self, v):
        self.__concursoStart = v

        if self.__concursoAtual < v:
            self.__concursoAtual = v


        #dif = self.sorteioFinal - self.sorteioInicial + 1
        #if (dif > 0) and (dif < self.maxThreads):
        #    self.maxThreads = dif

        # Reposiciona todas as threads
        #for th in self.__th:
        #    th.lb.concurso = self.__concursoAtual
        #    self.__concursoAtual += 1

            #Reseta o buffer de dados
        self.buffer = []

        self.__ajustarThreads()

    @property
    def sorteioFinal(self):
        return self.__concursoMax

    @sorteioFinal.setter
    def sorteioFinal(self, v):
        if v > self.__ultimoSorteio:
            v = self.__ultimoSorteio

        if v > self.__concursoStart:
            self.__concursoMax = v

            if self.__concursoAtual > v:
                self.__concursoAtual = v

            #Reseta o buffer
            self.buffer = []

        #dif = self.sorteioFinal - self.sorteioInicial + 1
        #if dif < self.maxThreads:
        #    self.maxThreads = dif
        self.__ajustarThreads()

    @property
    def premiacao(self):
        return self.__lb().premiacao
    def __ajustarThreads(self):
        """
        Ajusta o número de Threads, conforme a faixa inicial e final de sorteios
        :return:
        """
        dif = self.sorteioFinal - self.sorteioInicial + 1
        if dif < self.maxThreads:
            self.maxThreads = dif

    @property
    def maxThreads(self):
        return self.__thMax

    @maxThreads.setter
    def maxThreads(self, v):
        if (self.__thMax != v) and (v > 1):
            self.__thMax = v
            self.__dumpThreads()


    def showSetup(self):
        jogo = self.__lb().jogo.upper()
        print('Parâmetros para', jogo)
        print('     Jogo             ', jogo)
        print('     Dezenas          ', self.__lb().volante.dezenas)
        print('     Sorteios         ', self.__lb().volante.sorteio)
        print('     Premiação        ', self.__lb().premiacao)
        print('     Sorteio inicial  ', self.sorteioInicial)
        print('     Sorteio final    ', self.sorteioFinal)
        print('     Threads          ', self.maxThreads)

    def __dumpThreads(self):

        # Encerra todas as Threads anteriores, se houver
        for th in self.__th:
            th.stop = True

        # Reseta a lista de threads
        self.__th = []

        # Instancia todas as threads
        for i in range(0, self.__thMax):
            self.__th.append(srcThread(thNdx=i, loteriaBase=self.__lb(), concurso=self.__concursoAtual,
                                       callProcess=self.__callProcess, autoStart=False))

            if self.verbose:
                __verbose = f'Iniciar thread {i} Concurso {self.__concursoAtual}'
                print(__verbose)

            self.__concursoAtual += 1

    def __callProcess(self, th) -> bool:

        th.lb.todosDados()

        self.__verbose = f'Processar thread {th.index} Sorteio {th.lb.concurso} / Atual: {self.__concursoAtual} de {self.__concursoMax}'

        # Verifica, não houve erro
        if th.lb.error.id == 0:
            sorteios = th.lb.listaDezenas()
            sorteios = [int(s) for s in sorteios]

            toSave = {
                'concurso': th.lb.numero(),
                'data': th.lb.dataApuracao(),
                'dezenas': sorteios,
                'sorteio': th.lb.dezenasNomeadas(),
                'hash': th.lb.hash(),
            }

            #Carrega a lista de dezenas de forma nomeada
            sorteios = th.lb.dezenasNomeadas()
            [toSave.update(srt) for srt in sorteios]

            #[toSave.update(s) for s in sorteios]

            self.buffer.append(toSave)

        else:
            self.__repescar.append(self.__concursoAtual)
            self.__verbose = f'Falha na pesquisa. Inclusão na repescagem {self.__concursoAtual}'

        # Verifica se chegou ao máximo
        r = (self.__concursoAtual + 1) > self.__concursoMax

        if not r:
            self.__concursoAtual += 1
            th.lb.concurso = self.__concursoAtual

        return r

    def start(self):
        '''
        Inicia todas as threads
        '''
        for th in self.__th:
            th.start()

    def wait(self):
        '''
        Aguarda conclusão das threads
        '''

        def doStop() -> bool:
            r = True
            for th in self.__th:
                r = r and th.stop
            return r

        meStop = False
        while not meStop:
            meStop = doStop()

        self.__doMakeCount()

    def __doMakeCount(self):
        self.__verbose = 'Calcular ocorrências'
        #Executa a contagem - precisa ser incluído no final de todos os processos, pois a busca é feita em thread
        bloco = pd.DataFrame(self.buffer).sort_values(by='concurso')

        #Ajusta a data
        bloco['data'] = pd.to_datetime(bloco['data'])

        counter = srcCounter(self.__lb().volante.dezenas)

        gruposDZ = list(bloco['dezenas'])
        concurso = list(bloco['concurso'])

        dc = []

        #Verifica individualmente cada grupo de dezenas
        for i in range(0, len(gruposDZ)):
            dzn = gruposDZ[i]
            #Reseta contagem individual de valores
            counter.resetCont()

            #Calcula todos os valores de uma vez só [soma e contagem]
            [counter.calculate(dz) for dz in dzn]

            cto = {'concurso': concurso[i]}
            cto.update(counter.getDict)

            dc.append(cto)

        blocCount = pd.DataFrame(dc)

        self.buffer = pd.merge(bloco, blocCount, on='concurso')

        self.__verbose = ''

        pass
        #bloco['soma'] = soma
        #bloco['contagem'] = contagem

        #self.buffer = bloco


    def startAndWait(self):
        self.__verbose = 'Preparar threads'
        self.start()
        self.__verbose = 'Iniciar pesquisa'
        self.wait()

    @property
    def values(self) -> pd.DataFrame:
        if len(self.buffer) == 0:
            self.startAndWait()
            print('')
        return self.buffer
        #df = DataFrame(self.buffer)
        #return df.sort_values(by='concurso')


    @property
    def volante(self):
        return self.__lb().volante

    @property
    def getDezenas(self):
        dzs = self.__lb().volante.sorteio
        cols = ['concurso', 'data']
        for i in range(1, dzs+1):
            cols.append(f'Dz{i}')

        return self.values[cols]

    @property
    def getSomas(self):
        dzs = self.__lb().volante.dezenas
        cols = ['concurso', 'data']
        for i in range(0, dzs):
            cols.append(f'smDz{i}')

        return self.values[cols]

    @property
    def getContagem(self):
        dzs = self.__lb().volante.dezenas
        cols = ['concurso', 'data']
        for i in range(0, dzs):
            cols.append(f'ctDz{i}')

        return self.values[cols]

    def __convertDznsStrToInt(self, dzs) -> list:
        """
            Converte lista STR em INT
        :param dzs:
        :return:
            list
        """

        r = str(dzs).replace('[', '').replace(']', '').split(',')
        final = [int(n) for n in r]
        return final

    def conferirListar(self, concursoInicial=1, concursoFinal=1) -> list:
        """
        Prepara lista de concursos para conferência
        :param concursoInicial:     Número inicial do concurso
        :param concursoFinal:       Número inicial do concurso
        :return: list               Lista de concursos
        Ex.:
            concursoInicial=200
            concursoFinal=203
            Retorna [200, 201, 202, 203]
        """
        r = []
        for i in range(concursoInicial, concursoFinal + 1):
            r.append(i)
        return r
    def conferir(self, dezenas=[], apostaID='', concursos=[]) -> pd.DataFrame:
        """
        Confere dezenas conforme o número do concurso
        :param dezenas:     Lista INT de dezenas apostadas, ex.: [12, 20, 34, 54, 43]

        concurso:    Número do(s) concurso(s) para comparar
                    [] [Default] Considera todos os sorteios
                    n           Considera somente o sorteio indicado, ex.: [1536], [1536, 1537]

        IMPORTANTE:
            Embora seja possível informar os números do concurso, é recomendável utilizar a faixa de apostas
            em dezenaInicial e dezenaFinal

        :return:
        """

        #if concurso > 0:
        #    self.sorteioInicial = 1
        #    self.sorteioFinal = self.__lb().numero()
        #else:
        #    self.sorteioInicial = concurso
        #    self.sorteioFinal = concurso

        if len(self.buffer) == 0:
            self.startAndWait()

        values = self.values[['concurso', 'dezenas']]

        if len(concursos) > 0:
            #conc_inicial = concursos[0]
            #conc_final = concursos[len(concursos)]
            values.query(f"concurso in {concursos}", inplace=True)
            values.reset_index(inplace=True)

        #Dados para retorno
        conferes = []

        #Informa parâmetros para premiacao
        premiacao = self.premiacao

        #Nenhum concurso indicado - considera todos os sorteios

        for i in range(0, len(values)):
            sorteio = self.__convertDznsStrToInt(values.loc[i]['dezenas']) #str(values.loc[i]['dezenas']).replace('[', '').replace(']', '').split(',')

            confere = Conferido(apostaID=apostaID, concurso=values.loc[i]['concurso'], dezenasSorteadas=sorteio,
                                dezenasApostadas=dezenas, premiacao=premiacao)
            confere.doProcess()
            #print(confere.concurso, confere.acertos.count, confere.erros.count)
            #print(confere.getData)
            conferes.append(confere.getData)

        return pd.DataFrame(conferes)