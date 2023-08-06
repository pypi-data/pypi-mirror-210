import requests, hashlib
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import logging

urllib3.disable_warnings(InsecureRequestWarning)

logging.captureWarnings(True)

from .Interpoler import Desmember


# from .Volante import srcVolante

# from .Collection import Collection


class __LoteriaBase:
    class __cerror:
        def __init__(e, id=0, msg=""):
            e.id = id
            e.msg = msg

        def reset(e):
            e.id = 0
            e.msg = ''

        def attr(e, id, msg):
            e.id = id
            e.msg = msg

        @property
        def tostr(e):
            return f'({e.id}) {e.msg}'

    class __conferencia:

        class __lst(list):
            @property
            def size(l):
                return len(l)

        def __init__(c, concurso=0, dezenas=[], acertos=[], erros=[]):
            c.concurso = concurso
            c.dezenas = dezenas
            c.acertos = c.__lst(acertos)
            c.erros = c.__lst(erros)

    class __volante:
        # Define o número de dezenas que cada volante cotém e o número de dezenas que são sorteadas
        def __init__(self, dezenas=0, sorteio=0):
            self.dezenas = dezenas
            self.sorteio = sorteio

    def __init__(self, concurso='', jogo='megasena', dezenas=60, sorteio=6, interpolerStart=3,
                 premiominimo=3,
                 premiozero=False):
        '''
            Instancia a classe

            concurso            É o número do concurso em que as informações serão procuradas
            jogo                Nome do jogo
            sorteio             Número de dezenas sorteadas
            interpolerStart     Número inicial para interpolação de dezenas
            premiominimo        Número mínimo de dezenas que garante prêmio
            premiozero          Informa se nenhum acerto garante prêmio
        '''
        self.__reload = True  # Informa se é necessário recarregar dados do concurso
        self.__concurso = concurso  # Concurso atual
        self.__jogo = jogo  # Tipo de jogo para pesquisa
        self.__buffer = []  # Buffer interno [vazio]
        self.__error = self.__cerror()  # Monitora erro
        self.__support = ''  # Suporte para cálculo HASH
        self.interpolerStart = interpolerStart  # Número incial de recombinações
        self.volante = self.__volante(dezenas=dezenas, sorteio=sorteio)

        #Define parâmetros de premiação com número mínimo de acertos e se nenhum acerto é considerado válido
        self.__premiacao = {
            'minimo': premiominimo,
            'zero': premiozero
        }

    @property
    def error(self) -> __cerror:
        return self.__error

    @property
    def concurso(self):
        return self.__concurso

    @concurso.setter
    def concurso(self, v):
        # Informa se é necessário recarregar dados do concurso
        self.__reload = (self.__concurso != v)
        self.__concurso = v

    @property
    def premiacao(self):
        return self.__premiacao

    @property
    def jogo(self):
        return self.__jogo

    def pesquisar(self):
        if not self.__reload:
            return self.__buffer

        concurso = self.concurso
        if concurso == '0' or concurso == 0:
            concurso = ''

        url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/{self.__jogo}/{concurso}"
        self.__error.reset()
        try:
            self.__buffer = []

            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
                'Content-Type': 'application/json',
                'Connection': 'keep-alive',
                'withCredentials': 'True',
                'Cookie': 'security=true;'
            }

            r = requests.get(url, verify=False, headers=headers)

            if r.status_code >= 400:
                self.__error.attr(r.status_code, r.reason)
            else:
                self.__buffer = r.json()
                self.__reload = False
                if self.concurso == '':
                    self.__concurso = self.__buffer['numero']
        except:
            self.__error.attr(-4, 'Falha na internet')

        return self.__buffer

    def todosDados(self):
        r = self.pesquisar()
        if self.error.id != 0:
            print('Erro:', self.error.tostr, 'concurso:', self.concurso)

        return r

    def tipoJogo(self):
        return self.todosDados()['tipoJogo']

    def numero(self):
        return self.todosDados()['numero']

    def nomeMunicipioUFSorteio(self):
        return self.todosDados()['nomeMunicipioUFSorteio']

    def dataApuracao(self):
        return self.todosDados()['dataApuracao']

    def valorArrecadado(self):
        return self.todosDados()['valorArrecadado']

    def valorEstimadoProximoConcurso(self):
        return self.todosDados()['valorEstimadoProximoConcurso']

    def valorAcumuladoProximoConcurso(self):
        return self.todosDados()['valorAcumuladoProximoConcurso']

    def valorAcumuladoConcursoEspecial(self):
        return self.todosDados()['valorAcumuladoConcursoEspecial']

    def valorAcumuladoConcurso_0_5(self):
        return self.todosDados()['valorAcumuladoConcurso_0_5']

    def acumulado(self):
        return self.todosDados()['acumulado']

    def indicadorConcursoEspecial(self):
        return self.todosDados()['indicadorConcursoEspecial']

    def dezenasSorteadasOrdemSorteio(self):
        return self.todosDados()['dezenasSorteadasOrdemSorteio']

    def listaResultadoEquipeEsportiva(self):
        return self.todosDados()['listaResultadoEquipeEsportiva']

    def numeroJogo(self):
        return self.todosDados()['numeroJogo']

    def nomeTimeCoracaoMesSorte(self):
        return self.todosDados()['nomeTimeCoracaoMesSorte']

    def tipoPublicacao(self):
        return self.todosDados()['tipoPublicacao']

    def observacao(self):
        return self.todosDados()['observacao']

    def localSorteio(self):
        return self.todosDados()['localSorteio']

    def dataProximoConcurso(self):
        return self.todosDados()['dataProximoConcurso']

    def numeroConcursoAnterior(self):
        return self.todosDados()['numeroConcursoAnterior']

    def numeroConcursoProximo(self):
        return self.todosDados()['numeroConcursoProximo']

    def valorTotalPremioFaixaUm(self):
        return self.todosDados()['valorTotalPremioFaixaUm']

    def numeroConcursoFinal_0_5(self):
        return self.todosDados()['numeroConcursoFinal_0_5']

    def listaMunicipioUFGanhadores(self):
        return self.todosDados()['listaMunicipioUFGanhadores']

    def listaRateioPremio(self):
        return self.todosDados()['listaRateioPremio']

    def listaDezenas(self):
        return self.todosDados()['listaDezenas']

    def listaDezenasINT(self):
        '''
            Lista dezenas numéricas
        :return:
            Converte valores em números
        '''
        dz = self.listaDezenas()
        dz = [int(d) for d in dz]
        return dz

    def listaDezenasSegundoSorteio(self):
        return self.todosDados()['listaDezenasSegundoSorteio']

    def id(self):
        return self.todosDados()['id']

    def hash(self) -> str:
        '''
        Calcula o hash das dezenas
        :return: str
        '''
        dz = self.listaDezenas()

        # Evita erro
        self.__support = ''

        def plus(v):
            self.__support += f'{v}'

        [plus(b) for b in dz]

        return hashlib.md5(self.__support.encode()).hexdigest()

    def dezenasNomeadas(self):
        dz = self.listaDezenas()
        r = []
        [r.append({f'Dz{(i + 1)}': int(dz[i])}) for i in range(0, len(dz))]
        return r

    def desmember(self) -> Desmember:
        return Desmember(build=self.listaDezenas(), concurso=self.concurso, interpolerStart=self.interpolerStart)

    def conferencia(self, dezenas=[]) -> __conferencia:
        '''
            Confere dezenas com os dados sorteados

        :param sorteio: lista (str) com dezenas sorteadas
        :return:
        '''

        r = self.__conferencia(concurso=self.numero(), dezenas=dezenas, acertos=[], erros=[])
        sorteio = self.listaDezenas()

        for d in sorteio:
            if d in dezenas:
                r.acertos.append(d)
            else:
                r.erros.append(d)

        return r


class ExportLoteriaBase(__LoteriaBase):
    def __init__(self, concurso='', jogo='', dezenas=0, sorteio=0, interpolerStart=0):
        super().__init__(concurso=concurso, jogo=jogo, dezenas=dezenas, sorteio=sorteio,
                         interpolerStart=interpolerStart)


class MegaSena(__LoteriaBase):
    def __init__(self, concurso=''):
        super().__init__(concurso=concurso, jogo='megasena', dezenas=60, sorteio=6, interpolerStart=round(6 / 2),
                         premiominimo=4, premiozero=False)


class LotoFacil(__LoteriaBase):
    def __init__(self, concurso=''):
        super().__init__(concurso=concurso, jogo='lotofacil', dezenas=25, sorteio=15, interpolerStart=round(15 / 2),
                         premiominimo=11, premiozero=False)


class Quina(__LoteriaBase):
    def __init__(self, concurso=''):
        super().__init__(concurso=concurso, jogo='quina', dezenas=80, sorteio=5, interpolerStart=round(5 / 2),
                         premiominimo=2, premiozero=False)


class LotoMania(__LoteriaBase):
    def __init__(self, concurso=''):
        super().__init__(concurso=concurso, jogo='lotomania', dezenas=100, sorteio=20, interpolerStart=round(20 / 2),
                         premiominimo=15, premiozero=True)


class TimeMania(__LoteriaBase):
    def __init__(self, concurso=''):
        super().__init__(concurso=concurso, jogo='timemania', dezenas=80, sorteio=7, interpolerStart=round(7 / 2),
                         premiominimo=3, premiozero=False)


class DuplaSena(__LoteriaBase):
    def __init__(self, concurso=''):
        super().__init__(concurso=concurso, jogo='duplasena', dezenas=50, sorteio=6, interpolerStart=round(12 / 2),
                         premiominimo=3, premiozero=False)


class Federal(__LoteriaBase):
    def __init__(self, concurso=''):
        super().__init__(concurso=concurso, jogo='federal', dezenas=10, sorteio=1, interpolerStart=1,
                         premiominimo=1, premiozero=False)


class Loteca(__LoteriaBase):
    def __init__(self, concurso=''):
        super().__init__(concurso=concurso, jogo='loteca', dezenas=14, sorteio=14, interpolerStart=1,
                         premiominimo=13, premiozero=False)


class DiaDeSorte(__LoteriaBase):
    def __init__(self, concurso=''):
        super().__init__(concurso=concurso, jogo='diadesorte', dezenas=30, sorteio=7, interpolerStart=round(7 / 2),
                         premiominimo=4, premiozero=False)


class SuperSet(__LoteriaBase):
    def __init__(self, concurso=''):
        super().__init__(concurso=concurso, jogo='supersete', dezenas=49, sorteio=7, interpolerStart=1,
                         premiominimo=3, premiozero=False)


def Group(loteria=__LoteriaBase()):
    if loteria == None:
        return []

    loteria.concurso = 0
    finalConcurso = loteria.numero()
    finalDezenas = loteria.listaDezenas()

    r = []

    # Aproveita o último registro
    lastValue = {
        'concurso': loteria.numero(),
        'dezenas': loteria.listaDezenas()
    }

    for i in range(1, finalConcurso):
        loteria.concurso = i
        loteria.todosDados()
        if loteria.error.id == 0:
            r.append(
                {
                    'concurso': loteria.numero(),
                    'dezenas': loteria.listaDezenas()
                }
                # loteria.listaDezenas().insert(0, loteria.concurso)
            )

    # r.append(finalDezenas.insert(0, finalConcurso))
    r.append(lastValue)

    return r
