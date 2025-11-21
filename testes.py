import matplotlib.pyplot as plt
import re
import os
import subprocess
import numpy as np
import sys
import struct
import time

def plotar_grafico(valores_geracoes, valores_fitness, caminho_salvar):
    """
    Plota e salva o gráfico de evolução do fitness.
    """
    plt.figure(figsize=(9, 5))

    # Obtém o eixo atual (gca = Get Current Axes) e define a proporção
    ax = plt.gca()
    ax.set_aspect('equal', adjustable='box')

    plt.plot(valores_geracoes, valores_fitness, color='b')
    
    plt.xlabel('Geração')
    plt.ylabel('Fitness')
    plt.title('Evolução do Fitness por Geração')
    plt.grid(True)
    
    # Ajusta os eixos para mostrar melhor a tendência
    if valores_geracoes:
        # Arredonda o valor máximo para a próxima dezena
        max_x = (max(valores_geracoes) // 10) * 10
        plt.xticks(range(0, max_x + 1, 10)) # Define os marcadores do eixo X
        plt.xlim(left=0)

    if valores_fitness:
        # Arredonda o valor máximo para a próxima dezena
        max_y = int((max(valores_fitness) // 10) * 10)
        plt.yticks(range(0, max_y + 1, 10)) # Define os marcadores do eixo Y    
        plt.ylim(bottom=0)

    # Destaca o melhor ponto no gráfico
    if valores_fitness:
        min_fitness = min(valores_fitness)
        # Encontra o índice da primeira ocorrência do melhor fitness
        indice_min = valores_fitness.index(min_fitness)
        geracoes_min = valores_geracoes[indice_min]
        
        # Adiciona um ponto vermelho e um texto para destacar o melhor resultado
        plt.plot(geracoes_min, min_fitness, 'ro', markersize=3)
        # Adiciona um texto para destacar o melhor resultado, sem seta
        plt.text(geracoes_min, min_fitness + 5, # Coordenadas do texto
                f'{min_fitness},{geracoes_min}', # O texto a ser exibido
                ha='center') # Alinhamento horizontal

    plt.tight_layout() # Ajusta o layout para evitar que os rótulos se sobreponham
    plt.savefig(caminho_salvar)

def ler_relatorio(caminho_arquivo):
    """
    Lê um arquivo de relatório e extrai os dados de geração e fitness.
    """
    valores_geracoes = []
    valores_fitness = []
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            for linha in arquivo:
                match = re.search(r'Geracao:\s*(\d+),\s*fitness:\s*(\d+)', linha, re.IGNORECASE)
                if match:
                    valores_geracoes.append(int(match.group(1)))
                    valores_fitness.append(int(match.group(2)))
    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro ao ler o arquivo: {e}")
    return valores_geracoes, valores_fitness

#def escreve_arquivo_parametrizado(populacao, geracoes, mutacao, elitismo, torneio, matriz_base):
def escreve_arquivo_parametrizado(populacao, geracoes, mutacao, recombinacao, matriz_base):    
    """Escreve os parâmetros fornecidos para o arquivo entrada.in."""
    '''celulas_vazias = np.argwhere(matriz_base == 0)
    celulas_vazias1d = np.where(matriz_base.flatten() == 0)[0]'''
    numeros_validos = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    
    try:
        with open('entrada.in', 'wb') as arquivo:
            arquivo.write(populacao.to_bytes(4, byteorder='big')) 
            arquivo.write(geracoes.to_bytes(4, byteorder='big'))
            arquivo.write(struct.pack('>f', mutacao))
            arquivo.write(struct.pack('>f', recombinacao))
            #arquivo.write(elitismo.to_bytes(4, byteorder='big'))
            #arquivo.write(torneio.to_bytes(4, byteorder='big'))
            np.save(arquivo, numeros_validos)
            np.save(arquivo, matriz_base)
            #np.save(arquivo, celulas_vazias)
            #np.save(arquivo, celulas_vazias1d)
    except Exception as e:
        print(f"Problemas na criação do arquivo {e}\n")

def main():
    """
    Função principal que executa uma bateria de testes com diferentes parâmetros
    e diferentes matrizes de Sudoku.
    """
    script_a_executar = 'agSudokuReplicacao.py'
    num_execucoes_por_teste = 4
    diretorio_base_saida = os.path.expanduser('~/caminho/para/salvar/resultados')  # Altere para o diretório desejado
    #os.makedirs(diretorio_base_saida, exist_ok=True)

    # Define o caminho para o relatório final
    caminho_relatorio_final = os.path.join(diretorio_base_saida, 'relatorio_consolidado_replicacao.txt')

    # Matrizes de Sudoku para os testes
    matrizes_para_testar = [
                            {"nome": "matriz_base",
                             "dados":
                                np.block([[0,8,4, 0,7,2, 1,0,5], 
                                                    [2,0,7, 8,3,0, 9,0,0], 
                                                    [6,0,0, 5,0,9, 0,0,8], 
                                                    [0,6,0, 9,2,8, 4,0,0],
                                                    [0,7,0, 0,0,0, 0,6,9], 
                                                    [0,2,0, 0,0,0, 0,8,1], 
                                                    [0,3,2, 0,5,0, 6,9,4], 
                                                    [7,0,0, 0,0,0, 0,0,2], 
                                                    [1,0,0, 2,0,4, 0,0,7]])},
                            {"nome": "Facil1",
                            "dados":
                                np.block([[0,3,0, 0,6,8, 1,7,0],
                                        [0,0,0, 1,0,0, 0,0,3],
                                        [0,1,0, 7,3,2, 9,0,0],
                                        [0,8,0, 0,1,4, 0,5,0],
                                        [6,4,0, 0,0,0, 0,9,1],
                                        [0,5,0, 9,8,0, 0,2,0],
                                        [0,0,2, 3,9,7, 0,1,0],
                                        [4,0,0, 0,0,6, 0,0,0],
                                        [0,7,8, 4,5,0, 0,6,0]])},

                            {"nome": "Facil2",
                            "dados":
                                np.block([[0,0,3, 0,2,0, 6,0,0],
                                        [9,0,0, 3,0,5, 0,0,1],
                                        [0,0,1, 8,0,6, 4,0,0],
                                        [0,0,8, 1,0,2, 9,0,0],
                                        [7,0,0, 0,0,0, 0,0,8],
                                        [0,0,6, 7,0,8, 2,0,0],
                                        [0,0,2, 6,0,9, 5,0,0],
                                        [8,0,0, 2,0,3, 0,0,9],
                                        [0,0,5, 0,1,0, 3,0,0]])},
    
                            {"nome": "Facil3",
                            "dados":
                                np.block([[8,0,2, 0,5,0, 7,0,1],
                                        [0,0,7, 0,8,2, 4,6,0],
                                        [0,1,0, 9,0,0, 0,0,0],
                                        [6,0,0, 0,0,1, 8,3,2],
                                        [5,0,0, 0,0,0, 0,0,9],
                                        [1,8,4, 3,0,0, 0,0,6],
                                        [0,0,0, 0,0,4, 0,2,0],
                                        [0,9,5, 6,1,0, 3,0,0],
                                        [3,0,8, 0,9,0, 6,0,7]])},

                            {"nome": "Medio1",
                            "dados":
                                np.array([[0,0,0, 0,0,0, 0,8,5],
                                        [0,0,0, 2,1,0, 0,0,9],
                                        [9,6,0, 0,8,0, 1,0,0],
                                        [5,0,0, 8,0,0, 0,1,6],
                                        [0,0,0, 0,0,0, 0,0,0],
                                        [8,9,0, 0,0,6, 0,0,7],
                                        [0,0,9, 0,7,0, 0,5,2],
                                        [3,0,0, 0,5,4, 0,0,0],
                                        [4,8,0, 0,0,0, 0,0,0]])},
                                        
                            {"nome": "Medio2",
                            "dados":
                                np.array([[0,0,0, 0,0,0, 0,0,0],
                                        [0,7,9, 0,5,0, 1,8,0],
                                        [8,0,0, 0,0,0, 0,0,7],
                                        [0,0,7, 3,0,6, 8,0,0],
                                        [4,5,0, 7,0,8, 0,9,6],
                                        [0,0,3, 5,0,2, 7,0,0],
                                        [7,0,0, 0,0,0, 0,0,5],
                                        [0,1,6, 0,3,0, 4,2,0],
                                        [0,0,0, 0,0,0, 0,0,0]])},

                            {"nome": "Medio3",
                            "dados":
                                np.array([[3,8,0, 0,0,0, 0,0,0],
                                        [0,0,0, 4,0,0, 7,8,5],
                                        [0,0,9, 0,2,0, 3,0,0],
                                        [0,6,0, 0,9,0, 0,0,0],
                                        [8,0,0, 3,0,2, 0,0,9],
                                        [0,0,0, 0,4,0, 0,7,0],
                                        [0,0,1, 0,7,0, 5,0,0],
                                        [4,9,5, 0,0,6, 0,0,0],
                                        [0,0,0, 0,0,0, 0,9,2]])},

                            {"nome": "Dificil1",
                            "dados":
                                np.array([[0,0,0, 0,0,0, 3,0,0],
                                        [0,2,0, 6,0,0, 0,0,0],
                                        [9,1,3, 0,0,2, 0,6,0],
                                        [0,0,0, 3,0,7, 9,0,0],
                                        [0,3,0, 0,8,0, 5,0,0],
                                        [0,0,8, 0,0,0, 0,0,2],
                                        [3,0,0, 0,5,6, 0,0,0],
                                        [0,0,0, 2,0,0, 6,7,0],
                                        [5,0,2, 8,0,0, 0,0,0]])},

                            {"nome": "Dificil2",
                            "dados":
                                np.array([[0,0,0, 0,0,3, 0,1,7],
                                        [0,1,5, 0,0,9, 0,0,8],
                                        [0,6,0, 0,0,0, 0,0,0],
                                        [1,0,0, 0,0,7, 0,0,0],
                                        [0,0,9, 0,0,0, 2,0,0],
                                        [0,0,0, 5,0,0, 0,0,4],
                                        [0,0,0, 0,0,0, 0,2,0],
                                        [5,0,0, 6,0,0, 3,4,0],
                                        [3,4,0, 2,0,0, 0,0,0]])},

                            {"nome": "Dificil3",
                            "dados":
                                np.array([[0,0,0, 7,0,0, 8,0,0],
                                        [0,0,6, 0,0,0, 0,3,1],
                                        [0,4,0, 0,0,2, 0,0,0],
                                        [0,2,4, 0,7,0, 0,0,0],
                                        [0,1,0, 0,3,0, 0,8,0],
                                        [0,0,0, 0,6,0, 2,9,0],
                                        [0,0,0, 8,0,0, 0,7,0],
                                        [8,6,0, 0,0,0, 5,0,0],
                                        [0,0,2, 0,0,6, 0,0,0]])}]

    # Configurações para testes
    configs_para_testar = []
    taxas_mutacao = [30.0, 50.0, 70.0, 90.0]
    geracoes_fixas = 100
    #elitismo_fixo = 5
    #torneio_fixo = 3
    taxas_recombinacao = [30.0, 40.0, 50.0, 60.0, 70.0]
    tamanhos_populacao = range(4, 101, 4) # De 4 a 100, de 4 em 4

    for matriz in matrizes_para_testar:
        for mutacao in taxas_mutacao:
            for recombinacao in taxas_recombinacao: #
                for populacao in tamanhos_populacao:
                    '''configs_para_testar.append({'populacao': populacao,'mutacao': mutacao,'geracoes': geracoes_fixas,
                        'elitismo': elitismo_fixo,'torneio': torneio_fixo, 'matriz': matriz})'''
                    configs_para_testar.append({'populacao': populacao, 'mutacao': mutacao, 'geracoes': geracoes_fixas,
                                                'recombinacao': recombinacao, 'matriz': matriz})

    # Cria o arquivo de relatório final
    try:
        with open(caminho_relatorio_final, 'w', encoding='utf-8') as f_txt:
            # Cria o cabeçalho com colunas separadas por tabulação (\t)
            cabecalho = "Nome_Matriz\tPopulacao\tMutacao\tRecombinacao\tExecucao_Num\tMelhor_Fitness\tTempo_Execucao_s\n"
            f_txt.write(cabecalho)
    except IOError as e:
        print(f"ERRO CRÍTICO: Não foi possível criar o arquivo de relatório em '{caminho_relatorio_final}'. Erro: {e}")
        return

    total_configs = len(configs_para_testar)
    total_execucoes = total_configs * num_execucoes_por_teste
    tempo_inicial_total = time.time()

    print(f"===== INICIANDO BATERIA DE TESTES COM {total_configs} CONFIGURAÇÕES =====")

    for config_id, config in enumerate(configs_para_testar):
        pop = config['populacao']
        mut = config['mutacao']
        ger = config['geracoes']
        rec = config['recombinacao']
        #eli = config['elitismo']
        #tor = config['torneio']
        matriz_info = config['matriz']
        
        nome_teste = f"{matriz_info['nome']}_pop{pop}_mut{mut}_rec{rec}"
        diretorio_saida_teste = os.path.join(diretorio_base_saida, nome_teste)
        os.makedirs(diretorio_saida_teste, exist_ok=True)

        print(f"\n--- [Teste {config_id + 1}/{total_configs}] INICIANDO: {nome_teste} ---")

        for i in range(1, num_execucoes_por_teste + 1):
            print(f"  --- Execução {i}/{num_execucoes_por_teste} ---")
            
            escreve_arquivo_parametrizado(
                populacao=pop,
                geracoes=ger,
                mutacao=mut,
                recombinacao=rec,
                #elitismo=eli,
                #torneio=tor,
                matriz_base=matriz_info['dados']
            )
            
            try:
                # Timeout de 3 minutos por segurança, para evitar execuções presas
                subprocess.run([sys.executable, script_a_executar], check=True, capture_output=True, text=True, timeout=180)
            except subprocess.TimeoutExpired:
                print(f"    -> ERRO: A execução {i} excedeu o tempo limite.")
                continue
            except subprocess.CalledProcessError as e:
                print(f"    -> ERRO ao executar {script_a_executar}:\n{e.stderr}")
                continue

            valores_geracoes, valores_fitness = ler_relatorio('relatorio.txt')
            if not valores_geracoes:
                print(f"    -> AVISO: Não foram encontrados dados no relatorio.txt para a execução {i}.")
                continue

            melhor_fitness = valores_fitness[-1]
            tempo_execucao = 0.0
            try:
                with open('tempoExec.txt', 'r', encoding='utf-8') as f_tempo:
                    tempo_str = f_tempo.read().strip()
                    if tempo_str:
                        tempo_execucao = float(tempo_str)
            except (FileNotFoundError, ValueError): pass
            
            try:
                with open(caminho_relatorio_final, 'a', encoding='utf-8') as f_txt:
                    # Formata a linha de dados com tabulação e a escreve no arquivo
                    '''linha_dados = (f"{matriz_info['nome']}\t{pop}\t{mut}\t{ger}\t{eli}\t{tor}\t"
                                   f"{i}\t{melhor_fitness}\t{tempo_execucao:.2f}\n")'''
                    linha_dados = (f"{matriz_info['nome']}\t{pop}\t{mut}\t{rec}\t{ger}\t"
                                   f"{i}\t{melhor_fitness}\t{tempo_execucao:.2f}\n")
                    f_txt.write(linha_dados)
            except IOError as e:
                print(f"    -> ERRO ao escrever no relatório consolidado: {e}")

            #nome_grafico = f'execucao_{i}_fitness_{melhor_fitness}.png'
            #caminho_completo_grafico = os.path.join(diretorio_saida_teste, nome_grafico)
            #plotar_grafico(valores_geracoes, valores_fitness, caminho_completo_grafico)

        print(f"--- Teste '{nome_teste}' concluído. Resultados salvos em '{diretorio_saida_teste}'. ---")

    tempo_final_total = time.time()
    print("\n=================================================")
    print("TODOS OS TESTES FORAM FINALIZADOS.")
    print(f"Total de execuções do algoritmo: {total_execucoes}")
    print(f"Relatório consolidado salvo em: {caminho_relatorio_final}")
    print(f"Tempo total da bateria de testes: {(tempo_final_total - tempo_inicial_total) / 60:.2f} minutos.")
    print("=================================================")

if __name__ == "__main__":
    main()