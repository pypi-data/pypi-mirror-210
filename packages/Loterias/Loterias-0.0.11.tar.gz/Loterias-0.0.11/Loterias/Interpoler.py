import hashlib, itertools
import pandas as pd


class Interpoler:
    def __init__(self, build=[], elemt=2, parent=None):
        self.parent = parent  # Classe Demember pai
        self.elemt = elemt  # Número de elementos
        self.build = build  # Dados recombinados
        self.__suport = ' '  # Valor de suporte para cálculo do HASH

    @property
    def hash(self) -> str:
        self.__suport = ' '  # Espaço vazio para evitar erro

        def plus(v):
            self.__suport += f'{v}'

        [plus(b) for b in self.build]

        return hashlib.md5(self.__suport.encode()).hexdigest()

    @property
    def maker(self):
        r = list(self.build)
        r.insert(0, self.hash)
        r.insert(0, self.parent.concurso)
        r.insert(1, self.parent.hash)
        r.insert(2, self.elemt)
        return r


class Desmember:
    def __init__(self, build=[], concurso=0, interpolerStart=3):
        self.__interpolerStart = interpolerStart  # Númeno mínimo de recombinações
        self.__build = []
        self.interpoler = []
        self.hash = ''
        self.build = build
        self.concurso = concurso

    @property
    def build(self):
        return self.__build

    @build.setter
    def build(self, v):
        self.__build = v
        self.__doHash()  # Calcula o hash de origem
        self.__doMake()  # Calcula as combinaço

    def __doHash(self):
        '''
            Calcula o HASH de dados pai
        '''

        self.hash = ' '

        def plus(v):
            self.hash += f'{v}'

        [plus(b) for b in self.__build]

        self.hash = hashlib.md5(self.hash.encode()).hexdigest()

    def __doMake(self):
        '''
            Executa as combinações
        '''

        # Reseta a lista de recombinações
        self.interpoler = []

        # Calcula o número máximo de recombinações
        nMaxCombin = len(self.build)

        # Verifica se existe condição para continuar à atividade
        if nMaxCombin < 1:
            return

        # Percorre a lista de recombinações
        for i in range(self.__interpolerStart, nMaxCombin):

            # Executa a recombinação
            buffer = itertools.combinations(self.build, i)

            # Instancia a classe de recombinação
            for bf in buffer:
                self.interpoler.append(Interpoler(build=bf, elemt=i, parent=self))

        self.interpoler.append(Interpoler(build=self.build, elemt=nMaxCombin, parent=self))

    @property
    def lister(self) -> pd.DataFrame:
        '''
            Convete todos os dados em DataFrema

            É possível converter DataFrame em dados para SQLite

            conn = sqlite3.connect(data.sqlite)
            df.to_sql(tableName, conn, if_exists='replace', index=False)

            Mais detalhes em:
                https://www.skytowner.com/explore/writing_pandas_dataframe_to_sqlite

        '''
        nCol = ['concurso', 'hashPrincipal', 'dezenas', 'hashDerivado']
        [nCol.append(f'Dz{d}') for d in range(1, len(self.build) + 1)]

        interp = []
        [interp.append(i.maker) for i in self.interpoler]

        lst = pd.DataFrame(interp, columns=nCol)
        return lst.fillna('00')
