# Código adaptado de: https://github.com/ifertz/SUdokuSolver

import time
from numba import njit # Incompatível com classes, sendo necessário a utilização de funções auxiliares para algumas funções
import numpy as np
import struct

class Individuo:
    #__init__ é um método construtor que inicializa os atributos dos objetos
    def __init__(self, fitness = 0, matriz = None):
        self.fitness = fitness # Número de caracteres repetidos em cada linha, coluna ou submatriz
        self.matriz = matriz # Matriz contendo as nove 'submatrizes'

class Parametros:
    def __init__(self, numeros_validos = None, matriz_base = None, populacao = 0, geracoes = 0, mutacao = 0, recombinacao = 0):
        self.numeros_validos = numeros_validos # Números válidos (1-9) para o Sudoku
        self.matriz_base = matriz_base # Matriz base
        self.populacao = populacao # Tamanho da população
        self.geracoes = geracoes # Número de gerações
        self.mutacao = mutacao # Taxa de mutação (0 a 99)

'''
    Função escreve_relatorio:
        Escreve no arquivo relatorio.txt a geração e o fitness de cada execução.
    Parâmetros: 
        geracao - número da geração atual.
        fitness - quantidade de números repetidos em linhas, colunas ou submatrizes.
    Retorno:
        Nulo.
'''
def escreve_relatorio(geracao, fitness):
    try:
        modo = 'w' if geracao == 0 else 'a' # Se for a primeira geração, cria o arquivo, se não adiciona ao final
        # Gravando os dados no arquivo relatorio.txt
        with open('relatorio.txt', modo, encoding='utf-8') as arquivo:
            arquivo.write(f'Geracao: {geracao:}, fitness: {fitness:}\n')
    except Exception as e: # Caso haja erro na criação do arquivo relatorio.txt
        print(f"Problemas na criação do arquivo {e}\n")
    
    try:
        with open('relatorio.txt', 'r') as arquivo:
            resultado = arquivo.read()
            if not resultado:
                print("Erro na gravação")
    except FileNotFoundError as e:
        print(f"Arquivo {e} não foi encontrado.\n")

'''
    Função le_arquivo:
        Lê no arquivo entrada.in com os parâmetros definidos pelo usuário
        para os testes.
    Retorno:
        Instância da classe Parametros com os parâmetros lidos.
'''
def le_arquivo():
    try:
        parametros = Parametros()
        # Lê o arquivo entrada.in
        with open('entrada.in', 'rb') as arquivo:
            populacao = arquivo.read(4) 
            geracoes = arquivo.read(4)
            mutacao = arquivo.read(4)
            recombinacao = arquivo.read(4)
            numeros_validos = np.load(arquivo) # Lê os números válidos do arquivo
            matriz_base = np.load(arquivo) # Lê a matriz base do arquivo

            parametros.populacao = int.from_bytes(populacao, byteorder='big')
            parametros.geracoes = int.from_bytes(geracoes, byteorder='big')
            parametros.mutacao = struct.unpack('>f', mutacao)[0]
            parametros.recombinacao = struct.unpack('>f', recombinacao)[0]
            parametros.numeros_validos = numeros_validos
            parametros.matriz_base = matriz_base
    
    except FileNotFoundError as e:
        print(f"Arquivo {e} não foi encontrado.\n")    

    return parametros

'''
    Função fitness:
        Calcula o fitness de um indivíduo (matriz base mutada) baseado nas regras do Sudoku.
    Parâmetros: 
        matriz - matriz do indivíduo a ser avaliado.
    Retorno:
        Quantidade de números repetidos em linhas, colunas e submatrizes.
'''
@njit
def fitness(matriz):
    repetidos = 0

    # Regras básicas do Sudoku:
    # Não pode haver números repetidos em linhas, colunas e submatrizes 3x3
    num_linhas = len(matriz)
    num_colunas = len(matriz[0])
    passo = 3 # Tamanho da submatriz 3x3
    tamanho_matriz = len(matriz) # Tamanho da matriz (9x9)

    # Verifica repetição de números nas linhas
    for i in range(num_linhas):
        contagem = np.bincount(matriz[i, :]) # Conta a ocorrência de cada número na linha
        repetidos += np.sum(contagem[contagem > 1] - 1) # Soma o número de repetições (ocorrências - 1)
        
    # Verifica repetição de números nas colunas
    for j in range(num_colunas):
        contagem = np.bincount(matriz[:, j]) # Conta a ocorrência de cada número na coluna
        repetidos += np.sum(contagem[contagem > 1] - 1) # Soma o número de repetições (ocorrências - 1)
        
    # Verifica repetição de números nas submatrizes 3x3
    for i in range(0, tamanho_matriz, passo): # Itera sobre as linhas com passo de 3
        for j in range(0, tamanho_matriz, passo): # Itera sobre as colunas com passo de 3
            submatriz = matriz[i:i+passo, j:j+passo].flatten() # Extrai a submatriz 3x3 e a transforma em um array unidimensional
            contagem = np.bincount(submatriz) # Conta a ocorrência de cada número na submatriz
            repetidos += np.sum(contagem[contagem > 1] - 1) # Soma o número de repetições (ocorrências - 1)
            
    return repetidos

'''
    Função mutacao_por_troca_bloco_auxiliar:
        Aplica a mutação por troca dentro de blocos 3x3, trocando dois números não fixos.
    Parâmetros:
        matriz - matriz do indivíduo a ser mutado.
        taxa_mutacao - taxa de mutação (0 a 99).
        matriz_base - matriz base.
    Retorno:
        Matriz mutada.
'''
@njit
def mutacao_por_troca_bloco_auxiliar(matriz, taxa_mutacao, matriz_base): #arrumar comentário
    nova_matriz = matriz.copy() # Matriz auxiliar
    probabilidade_mutacao = taxa_mutacao/100
    passo = 3 # Tamanho do bloco
    tamanho_matriz = len(matriz) # Tamanho da matriz (9x9)

    # Itera sobre CADA bloco 3x3
    for i in range(0, tamanho_matriz, passo): # Itera sobre as linhas com passo de 3
        for j in range(0, tamanho_matriz, passo): # Itera sobre as colunas com passo de 3
            # Cada bloco tem sua própria chance de sofrer mutação
            if np.random.random() <= probabilidade_mutacao:
                # Extrai os índices das células que podem ser trocadas (não fixas)
                submatriz_base1d = matriz_base[i:i+passo, j:j+passo].flatten()
                indices_trocaveis = np.where(submatriz_base1d == 0)[0]
                if len(indices_trocaveis) >= 2: # Se houver pelo menos duas células para trocar
                    # Seleciona dois índices aleatórios para troca
                    indices_para_trocar = np.random.choice(indices_trocaveis, size=2, replace=False)
                    indice1, indice2 = indices_para_trocar[0], indices_para_trocar[1]
                    # Extrai a submatriz do indivíduo e a transforma em array unidimensional
                    submatriz_individuo1d = nova_matriz[i:i+passo, j:j+passo].flatten()
                    # Realiza a troca dos valores nas posições selecionadas
                    valor_temp = submatriz_individuo1d[indice1]
                    submatriz_individuo1d[indice1] = submatriz_individuo1d[indice2]
                    submatriz_individuo1d[indice2] = valor_temp
                    # Atualiza a submatriz na nova matriz
                    nova_matriz[i:i+passo, j:j+passo] = submatriz_individuo1d.reshape((passo, passo))

    return nova_matriz # Retorna matriz

'''
    Função mutacao_por_troca_bloco:
        Utiliza a função mutacao_por_troca_bloco_auxiliar para realizar a mutação.
    Parâmetros:
        filho - indivíduo a ser mutado.
        parametros - classe Parametros.
    Retorno:
        Indivíduo mutado.
'''
def mutacao_por_troca_bloco(filho, parametros):
    individuo = Individuo(filho.fitness, filho.matriz)

    # Certifica que a matriz do filho não é None
    if filho.matriz is None:
        return Individuo(filho.fitness, None) # Retorna cópia sem array se original não tem

    # Realiza a mutação da matriz unidimensional do filho
    matriz_mutada = mutacao_por_troca_bloco_auxiliar(filho.matriz, parametros.mutacao, parametros.matriz_base)
    
    individuo.matriz = matriz_mutada # Transforma o array unidimensional em matriz 9x9

    return individuo

'''
    Função recombinacao_bloco_1_ponto_auxiliar:
        Combina os blocos do pai e da mãe utilizando a técnica de um ponto de corte,
        onde o filho herda os blocos do pai até o ponto de corte e os blocos da mãe 
        depois do ponto de corte.
    Parâmetros:
        matriz_pai - matriz do pai.
        matriz_mae - matriz da mãe.
        matriz_base - matriz base.
    Retorno:
        Matriz do filho resultante da combinação entre pai e mãe.
'''
@njit
def recombinacao_bloco_1_ponto_auxiliar(matriz_pai, matriz_mae, matriz_base, taxa_recombinacao):
    # Verifica se a recombinação deve ocorrer. Usa np.random.random() por ser compatível com Numba.
    if np.random.random() < taxa_recombinacao / 100:
        # Se a recombinação ocorrer, executa o crossover.
        filho = matriz_base.copy()
        passo = 3 # Tamanho do bloco

        ponto_de_corte = np.random.randint(1, 9) # Sorteia um número entre 1 e 8

        # Itera sobre os 9 blocos
        for indice_bloco in range(9):
            linha_inicio = (indice_bloco // 3) * passo
            coluna_inicio = (indice_bloco % 3) * passo
            
            if indice_bloco < ponto_de_corte:
                bloco_para_copiar = matriz_pai[linha_inicio : linha_inicio+passo, coluna_inicio : coluna_inicio+passo]
            else:
                bloco_para_copiar = matriz_mae[linha_inicio : linha_inicio+passo, coluna_inicio : coluna_inicio+passo]
            
            filho[linha_inicio : linha_inicio+passo, coluna_inicio : coluna_inicio+passo] = bloco_para_copiar
        
        return filho
    else:
        # Se não houver recombinação, o filho é um clone do primeiro pai.
        return matriz_pai.copy()

'''
    Função recombinacao_bloco_1_ponto:
        Utiliza a função recombinacao_bloco_1_ponto_auxiliar para realizar a recombinação
        entre pai e mãe.
    Parâmetros:
        pai - um dos indivíduos da população.
        mae - um dos indivíduos da população.
        parametros - classe Parametros.
    Retorno:
        Indivíduo filho resultante da combinação entre pai e mãe.
'''
def recombinacao_bloco_1_ponto(pai, mae, parametros):
    filho = Individuo()

    if pai.matriz is None or mae.matriz is None:
        return Individuo()

    matriz_filho = recombinacao_bloco_1_ponto_auxiliar(pai.matriz, mae.matriz, parametros.matriz_base, parametros.recombinacao)
    
    filho.matriz = matriz_filho

    return filho

'''
    Função selecao_por_roleta:
        Seleciona um indivíduo da população baseado em uma roleta, 
        onde a probabilidade de seleção é inversamente proporcional ao fitness.
    Parâmetros:
        populacao - população de indivíduos (matrizes cópias).
    Retorno:
        Retorna o indivíduo selecionado pela roleta.
'''
def selecao_por_roleta(populacao):
    # Converte o fitness: um fitness menor (melhor) tem uma fatia maior.
    # Adição de 1.0 para evitar divisão por zero se o fitness for 0.
    aptidoes = [1.0 / (1.0 + individuo.fitness) for individuo in populacao]
    soma_total_aptdao = sum(aptidoes)

    # Se a soma for zero, retorna um aleatório.
    if soma_total_aptdao == 0:
        return populacao[np.random.randint(0, len(populacao))]
    
    probabilidades = [aptidao/soma_total_aptdao for aptidao in aptidoes]

    # "Gira" a roleta gerando um ponto aleatório.
    ponto_aleatorio = np.random.random()

    # Encontra o indivíduo correspondente ao ponto da roleta.
    soma_parcial = 0
    for i, prob in enumerate(probabilidades):
        soma_parcial += prob
        if soma_parcial >= ponto_aleatorio:
            return populacao[i]

    # Caso de imprecisão aritmética, retorna o último indivíduo.        
    return populacao[-1]


'''
    Função reproducao:
        Aplica as funções de elitismo, torneio, recombinação e mutação na população.
    Parâmetros:
        populacao - população de indivíduos (matrizes cópias).
        parametros - classe Parametros.
    Retorno:
        Retorna o melhor indivíduo da população.
'''
def reproducao(populacao, parametros):
    melhor = Individuo()
    filho = Individuo()
    nova_populacao = [Individuo() for _ in range(parametros.populacao)]

    melhor = Individuo(fitness=populacao[0].fitness, matriz=np.copy(populacao[0].matriz))

    for i in range(parametros.populacao):
        pai = selecao_por_roleta(populacao)
        mae = selecao_por_roleta(populacao)
        filho = recombinacao_bloco_1_ponto(pai, mae, parametros)
        filho = mutacao_por_troca_bloco(filho, parametros)
        filho.fitness = fitness(filho.matriz)

        nova_populacao[i] = filho
        
        if filho.fitness < melhor.fitness:
            melhor = Individuo(fitness=filho.fitness, matriz=np.copy(filho.matriz))

    for i in range(parametros.populacao):
        populacao[i] = nova_populacao[i]

    return melhor

'''
    Função gera_matrizes_aleatorias:
        Gera matrizes aleatórias para inicializar a população, preenchendo as células vazias
        da matriz base com números válidos de forma aleatória, respeitando a regra de não 
        repetição dentro de cada bloco 3x3.
    Parâmetros:
        tamanho_populacao - tamanho da população.
        numeros_validos - números válidos para o Sudoku.
        matriz_base - matriz base.
    Retorno:
        Lista de matrizes aleatórias geradas.
'''
@njit
def gera_matrizes_aleatorias(tamanho_populacao, numeros_validos, matriz_base):
    matrizes = []
    passo = 3 # Define o tamanho da submatriz (3x3)
    tamanho_matriz = len(matriz_base) # Tamanho da matriz (9x9)


    for _ in range(tamanho_populacao):
        # Começa com uma cópia nova da matriz base para cada indivíduo
        matriz_individuo = matriz_base.copy()
        # Itera sobre cada bloco 3x3 da matriz
        for i in range(0, tamanho_matriz, passo):
            for j in range(0, tamanho_matriz, passo):
                # Extrai a submatriz atual
                submatriz = matriz_individuo[i:i+passo, j:j+passo]
                # Encontra os números que já estão fixos no bloco
                numeros_presentes = set()
                for valor in submatriz.flatten():
                    if valor != 0:
                        numeros_presentes.add(valor)
                # Determina quais números estão faltando para preencher o bloco
                numeros_faltantes = []
                for numero in numeros_validos:
                    if numero not in numeros_presentes:
                        numeros_faltantes.append(numero)
                # Embaralha aleatoriamente os números que faltam
                np.random.shuffle(np.array(numeros_faltantes))
                # Preenche as células vazias do bloco com os números embaralhados
                indice_faltante = 0
                for l in range(passo):
                    for c in range(passo):
                        if matriz_individuo[i+l, j+c] == 0:
                            matriz_individuo[i+l, j+c] = numeros_faltantes[indice_faltante]
                            indice_faltante += 1
                            
        matrizes.append(matriz_individuo)
        
    return matrizes

'''
    Função pre_processamento_logico:
        Aplica um pré-processamento lógico na matriz base, preenchendo células que possuem 
        apenas um candidato possível com base nas regras do Sudoku.
    Parâmetros:
        matriz - matriz base.
    Retorno:
        Matriz processada após o pré-processamento lógico.
'''
@njit
def pre_processamento_logico(matriz):
    matriz_processada = matriz.copy()
    passo = 3

    while True:
        houve_mudanca = False
        # Percorre cada célula da matriz
        for linha in range(9):
            for coluna in range(9):
                # Se a célula já estiver preenchida, pule para a próxima
                if matriz_processada[linha, coluna] != 0:
                    continue
                numeros_usados = set()
                # 1. Verifica a linha
                for valor in matriz_processada[linha, :]:
                    if valor != 0:
                        numeros_usados.add(valor)
                # 2. Verifica a coluna
                for valor in matriz_processada[:, coluna]:
                    if valor != 0:
                        numeros_usados.add(valor)
                # 3. Verifica a sub-grade 3x3
                linha_inicio = (linha // passo) * passo
                coluna_inicio = (coluna // passo) * passo
                submatriz = matriz_processada[linha_inicio:linha_inicio+passo, coluna_inicio:coluna_inicio+passo]
                for valor in submatriz.flatten():
                    if valor != 0:
                        numeros_usados.add(valor)
                # 4. Determina quais números são possíveis para esta célula
                numeros_possiveis = []
                for num in range(1, 10): # Números válidos de 1 a 9
                    if num not in numeros_usados:
                        numeros_possiveis.append(num)
                # 5. Se houver APENAS UM candidato possível, preenche a célula!
                if len(numeros_possiveis) == 1:
                    matriz_processada[linha, coluna] = numeros_possiveis[0]
                    houve_mudanca = True # Sinaliza que fizemos progresso

        # Se o loop inteiro terminou e nenhuma célula foi alterada, o processo terminou.
        if not houve_mudanca:
            break
            
    return matriz_processada

'''
    Função inicializa:
        Utiliza a função gera_matrizes_aleatorias para inicializar a população com matrizes 
        aleatórias de tamanho definido e calcula o fitness de cada uma delas.
    Parâmetros:
        populacao - população de indivíduos (matrizes cópias).
        parametros - classe Parametros.
    Retorno:
        Nulo.
'''
def inicializa(populacao, parametros):
    numeros_validos = parametros.numeros_validos
    tamanho_populacao = parametros.populacao
    matriz_base = parametros.matriz_base
    
    matriz_pre_processada = pre_processamento_logico(matriz_base)
    matrizes_geradas = gera_matrizes_aleatorias(tamanho_populacao, numeros_validos, matriz_pre_processada)
    
    for i in range(tamanho_populacao):
        populacao[i] = Individuo()
        populacao[i].matriz = matrizes_geradas[i]
        populacao[i].fitness = fitness(populacao[i].matriz)

'''
    Função set_seed: 
        Define uma semente para o gerador de números aleatórios usado pela biblioteca
        numba, permitindo reprodutibilidade nos testes.
    Parâmetros:
        seed - semente a ser definida.
    Retorno:
        Nulo.
'''
'''@njit
def set_seed(seed):
    np.random.seed(seed)'''

'''
    Função main:
        Implementa o Algoritmo Evolutivo para o problema: dada uma instância do jogo Sudoku (matriz base),
        ache a solução através de uma população de matrizes cópias preenchidas aleatoriamente.
'''

def main():
    #np.random.seed(0) # Semente fixa para testes
    #setSeed(0) # Semente fixa para testes
    
    inicio = time.time()

    #escreve_arquivo()
    parametros = le_arquivo()

    geracao = 0
    populacao = [Individuo() for _ in range(parametros.populacao)]

    np.random.seed(int(time.time())) # Semente de acordo com o tempo de máquina
    inicializa(populacao, parametros)
    while geracao <= parametros.geracoes:
        melhor = reproducao(populacao, parametros)
        print(f"\nIteracao {geracao}, melhor fitness {melhor.fitness}.\n")
        escreve_relatorio(geracao, melhor.fitness)
        print(f"{melhor.matriz}\n")
        geracao += 1
        if melhor.fitness == 0:
            break

    fim = time.time()
    total = fim - inicio

    try:
        # Gravando o tempo de execução real
        with open('tempoExec.txt', 'w', encoding='utf-8') as arquivo:
            arquivo.write(f'{total}')
    except Exception as e: # Caso haja erro na criação do arquivo tempoExec.txt
        print(f"Problemas na criação do arquivo {e}\n")

    print(f"Tempo total gasto pela CPU: {total}")

if __name__ == "__main__":
    main()