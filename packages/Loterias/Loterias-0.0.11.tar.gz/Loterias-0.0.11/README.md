#Biblioteca Python para extrair, via thread, dados de jogos lotéricos

Sintaxe básica
    from Loterias import CollectionType, CollectionByType


Onde:
    CollectionType
                    Contem identificador básico para coleções de dados

    CollectionByType(typed=CollectionType.DiaDeSorte, maxThreads=8, concursoStart=1, verbose=False, autoStart=False)
                    Instancia a classe para busca de dados    

    typed           Tipo de jogo, definido por CollectionType
    maxThreads      Número de máximo de Threads, default 8 [para múltipla pesquisa]
    concursoStart   Número do primeiro concurso que será pesquisado, default 1
    verbose         Apresenta ou não algumas informações durante a pesquisa
    autoStart       Inicia a pesquisa de imediato

Elementos/Rotinas de CollectionByType
    maxThreads      Ajusta o número máximo de threads [para múltipla pesquisa]
    sorteioInicial  Ajusta o número do sorteio inicial
    sorteioFinal    Limita o número do sorteio final [default é o último sorteio
    verbose         Apresenta ou não algumas informações durante a pesquisa
    value           Inicia a busca, se necessário, de dados e apresenta o resultado em pandas.DataFrame

v 0.0.5
    Adicionados métodos
    getDezenas      Extrai a lista de dezemas
    getSomas        Extrai a lista de somas, considerado cada sorteio
    getContagem     Extrai a contagem individual relativo a cada sorteio