"""
Script para testar o algoritmo genético com sudokus de diferentes níveis de dificuldade.
"""
import numpy as np
import struct
import subprocess
import time

# Definição dos sudokus de teste

SUDOKUS = {
    "Medio1": np.array([
        [0,0,0, 0,0,0, 0,8,5],
        [0,0,0, 2,1,0, 0,0,9],
        [9,6,0, 0,8,0, 1,0,0],
        [5,0,0, 8,0,0, 0,1,6],
        [0,0,0, 0,0,0, 0,0,0],
        [8,9,0, 0,0,6, 0,0,7],
        [0,0,9, 0,7,0, 0,5,2],
        [3,0,0, 0,5,4, 0,0,0],
        [4,8,0, 0,0,0, 0,0,0]
    ]),
    
    "Medio2": np.array([
        [0,0,0, 0,0,0, 0,0,0],
        [0,7,9, 0,5,0, 1,8,0],
        [8,0,0, 0,0,0, 0,0,7],
        [0,0,7, 3,0,6, 8,0,0],
        [4,5,0, 7,0,8, 0,9,6],
        [0,0,3, 5,0,2, 7,0,0],
        [7,0,0, 0,0,0, 0,0,5],
        [0,1,6, 0,3,0, 4,2,0],
        [0,0,0, 0,0,0, 0,0,0]
    ]),
    
    "Medio3": np.array([
        [3,8,0, 0,0,0, 0,0,0],
        [0,0,0, 4,0,0, 7,8,5],
        [0,0,9, 0,2,0, 3,0,0],
        [0,6,0, 0,9,0, 0,0,0],
        [8,0,0, 3,0,2, 0,0,9],
        [0,0,0, 0,4,0, 0,7,0],
        [0,0,1, 0,7,0, 5,0,0],
        [4,9,5, 0,0,6, 0,0,0],
        [0,0,0, 0,0,0, 0,9,2]
    ]),
    
    "Dificil1": np.array([
        [0,0,0, 0,0,0, 3,0,0],
        [0,2,0, 6,0,0, 0,0,0],
        [9,1,3, 0,0,2, 0,6,0],
        [0,0,0, 3,0,7, 9,0,0],
        [0,3,0, 0,8,0, 5,0,0],
        [0,0,8, 0,0,0, 0,0,2],
        [3,0,0, 0,5,6, 0,0,0],
        [0,0,0, 2,0,0, 6,7,0],
        [5,0,2, 8,0,0, 0,0,0]
    ]),
    
    "Dificil2": np.array([
        [0,0,0, 0,0,3, 0,1,7],
        [0,1,5, 0,0,9, 0,0,8],
        [0,6,0, 0,0,0, 0,0,0],
        [1,0,0, 0,0,7, 0,0,0],
        [0,0,9, 0,0,0, 2,0,0],
        [0,0,0, 5,0,0, 0,0,4],
        [0,0,0, 0,0,0, 0,2,0],
        [5,0,0, 6,0,0, 3,4,0],
        [3,4,0, 2,0,0, 0,0,0]
    ]),
    
    "Dificil3": np.array([
        [0,0,0, 7,0,0, 8,0,0],
        [0,0,6, 0,0,0, 0,3,1],
        [0,4,0, 0,0,2, 0,0,0],
        [0,2,4, 0,7,0, 0,0,0],
        [0,1,0, 0,3,0, 0,8,0],
        [0,0,0, 0,6,0, 2,9,0],
        [0,0,0, 8,0,0, 0,7,0],
        [8,6,0, 0,0,0, 5,0,0],
        [0,0,2, 0,0,6, 0,0,0]
    ])
}

def escreve_arquivo_teste(matriz_base, populacao=600, geracoes=300, mutacao=5, elitismo=5, torneio=3):
    """Cria o arquivo entrada.in com os parâmetros especificados."""
    celulas_vazias = np.argwhere(matriz_base == 0)
    celulas_vazias1d = np.where(matriz_base.flatten() == 0)[0]
    numeros_validos = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
    
    try:
        with open('entrada.in', 'wb') as arquivo:
            arquivo.write(populacao.to_bytes(4, byteorder='big'))
            arquivo.write(geracoes.to_bytes(4, byteorder='big'))
            arquivo.write(struct.pack('>f', mutacao))
            arquivo.write(elitismo.to_bytes(4, byteorder='big'))
            arquivo.write(torneio.to_bytes(4, byteorder='big'))
            np.save(arquivo, numeros_validos)
            np.save(arquivo, matriz_base)
            np.save(arquivo, celulas_vazias)
            np.save(arquivo, celulas_vazias1d)
        return True
    except Exception as e:
        print(f"Erro ao criar arquivo: {e}")
        return False

def contar_celulas_vazias(matriz):
    """Conta quantas células vazias (zeros) existem na matriz."""
    return np.sum(matriz == 0)

def executar_teste(nome, matriz, populacao=600, geracoes=300, mutacao=10):
    """Executa o teste para um sudoku específico."""
    print(f"\n{'='*60}")
    print(f"TESTANDO: {nome}")
    print(f"Células vazias: {contar_celulas_vazias(matriz)}")
    print(f"Parâmetros: pop={populacao}, ger={geracoes}, mut={mutacao}%")
    print(f"{'='*60}")
    print("Matriz:")
    print(matriz)
    print()
    
    # Cria arquivo de entrada
    escreve_arquivo_teste(matriz, populacao, geracoes, mutacao)
    
    # Executa o algoritmo
    inicio = time.time()
    resultado = subprocess.run(
        ['python', 'agSudokuAleatorio.py'],
        capture_output=True,
        text=True,
        cwd=r'c:\Users\rhuan\OneDrive\Documentos\workspace\tavia'
    )
    fim = time.time()
    
    # Extrai resultado
    output = resultado.stdout
    linhas = output.strip().split('\n')
    
    # Procura último fitness
    melhor_fitness = None
    melhor_geracao = None
    for linha in linhas:
        if 'melhor fitness' in linha.lower():
            try:
                # Extrai iteração e fitness
                partes = linha.split(',')
                for parte in partes:
                    if 'iteracao' in parte.lower():
                        melhor_geracao = int(''.join(filter(str.isdigit, parte)))
                    if 'fitness' in parte.lower():
                        melhor_fitness = int(''.join(filter(str.isdigit, parte.split('fitness')[-1])))
            except:
                pass
    
    print(f"\nRESULTADO {nome}:")
    print(f"  Melhor fitness alcançado: {melhor_fitness}")
    print(f"  Tempo de execução: {fim - inicio:.2f} segundos")
    if melhor_fitness == 0:
        print(f"  ✅ SOLUÇÃO ENCONTRADA!")
    else:
        print(f"  ❌ Não encontrou solução perfeita")
    
    return {
        'nome': nome,
        'fitness': melhor_fitness,
        'tempo': fim - inicio,
        'celulas_vazias': contar_celulas_vazias(matriz),
        'sucesso': melhor_fitness == 0
    }

def main():
    print("="*60)
    print("TESTES DE SUDOKUS MÉDIOS E DIFÍCEIS")
    print("Algoritmo Genético com Operadores Permutacionais")
    print("="*60)
    
    resultados = []
    
    # Testa sudokus difíceis
    sudokus_dificeis = {k: v for k, v in SUDOKUS.items() if 'Dificil' in k}
    for nome, matriz in sudokus_dificeis.items():
        resultado = executar_teste(
            nome, 
            matriz, 
            populacao=1000,   # População grande
            geracoes=500,     # Gerações moderadas
            mutacao=20        # Taxa de mutação moderada-alta
        )
        resultados.append(resultado)
    
    # Resumo final
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    print(f"{'Sudoku':<12} {'Vazias':<8} {'Fitness':<10} {'Tempo(s)':<10} {'Status'}")
    print("-"*60)
    
    for r in resultados:
        status = "✅ OK" if r['sucesso'] else "❌ Falhou"
        print(f"{r['nome']:<12} {r['celulas_vazias']:<8} {r['fitness']:<10} {r['tempo']:<10.2f} {status}")
    
    # Estatísticas
    sucessos = sum(1 for r in resultados if r['sucesso'])
    print("-"*60)
    print(f"Taxa de sucesso: {sucessos}/{len(resultados)} ({100*sucessos/len(resultados):.1f}%)")
    print(f"Tempo total: {sum(r['tempo'] for r in resultados):.2f} segundos")

if __name__ == "__main__":
    main()
