"""
Comparação: Seu Algoritmo Permutacional vs TCC Andressa (UFU, 2025)
Matriz Base de calibração
"""
import numpy as np
import struct
import subprocess
import time
import json

# Matriz Base usada pela Andressa (Apêndice A)
MATRIZ_BASE_ANDRESSA = np.array([
    [0,8,4, 0,7,2, 1,0,5], 
    [2,0,7, 8,3,0, 9,0,0], 
    [6,0,0, 5,0,9, 0,0,8], 
    [0,6,0, 9,2,8, 4,0,0],
    [0,7,0, 0,0,0, 0,6,9], 
    [0,2,0, 0,0,0, 0,8,1], 
    [0,3,2, 0,5,0, 6,9,4], 
    [7,0,0, 0,0,0, 0,0,2], 
    [1,0,0, 2,0,4, 0,0,7]
])

def escreve_entrada(matriz, pop=1000, ger=300, mut=5, elit=5, torn=3):
    """Cria entrada.in para seu algoritmo"""
    celulas_vazias = np.argwhere(matriz == 0)
    celulas_vazias1d = np.where(matriz.flatten() == 0)[0]
    numeros_validos = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
    
    with open('entrada.in', 'wb') as f:
        f.write(pop.to_bytes(4, byteorder='big'))
        f.write(ger.to_bytes(4, byteorder='big'))
        f.write(struct.pack('>f', mut))
        f.write(elit.to_bytes(4, byteorder='big'))
        f.write(torn.to_bytes(4, byteorder='big'))
        np.save(f, numeros_validos)
        np.save(f, matriz)
        np.save(f, celulas_vazias)
        np.save(f, celulas_vazias1d)

def extrair_fitness(relatorio_path='relatorio.txt'):
    """Extrai o melhor fitness do relatório"""
    try:
        with open(relatorio_path, 'r') as f:
            linhas = f.readlines()
            if linhas:
                # Pega última linha
                ultima = linhas[-1]
                fitness = int(ultima.split('fitness: ')[1].strip())
                return fitness
    except:
        return None
    return None

def executar_teste_individual():
    """Executa uma vez seu algoritmo"""
    inicio = time.time()
    
    resultado = subprocess.run(
        ['python', 'agSudokuAleatorio.py'],
        capture_output=True,
        text=True
    )
    
    fim = time.time()
    fitness = extrair_fitness()
    
    return {
        'fitness': fitness,
        'tempo': fim - inicio,
        'sucesso': fitness == 0
    }

def executar_bateria(num_testes=10):
    """Executa bateria de testes"""
    print("="*70)
    print("COMPARAÇÃO: Algoritmo Permutacional vs TCC Andressa (UFU, 2025)")
    print("="*70)
    print(f"\nExecutando {num_testes} testes...\n")
    
    resultados = []
    
    for i in range(num_testes):
        print(f"Teste {i+1}/{num_testes}...", end=" ")
        
        # Gera entrada
        escreve_entrada(MATRIZ_BASE_ANDRESSA)
        
        # Executa
        resultado = executar_teste_individual()
        resultados.append(resultado)
        
        status = "✅ ÓTIMO!" if resultado['sucesso'] else f"fitness={resultado['fitness']}"
        print(f"{status} ({resultado['tempo']:.1f}s)")
    
    # Calcula estatísticas
    fitness_values = [r['fitness'] for r in resultados]
    tempos = [r['tempo'] for r in resultados]
    sucessos = sum(1 for r in resultados if r['sucesso'])
    
    stats = {
        'fitness_valores': fitness_values,
        'taxa_sucesso': (sucessos / num_testes) * 100,
        'fitness_medio': np.mean(fitness_values),
        'fitness_desvio': np.std(fitness_values),
        'fitness_min': min(fitness_values),
        'fitness_max': max(fitness_values),
        'tempo_medio': np.mean(tempos),
        'tempo_total': sum(tempos)
    }
    
    # Imprime relatório
    print("\n" + "="*70)
    print("RELATÓRIO COMPARATIVO")
    print("="*70)
    
    print("\n📊 RESULTADOS DO TCC ANDRESSA (Referência):")
    print("   Taxa de Sucesso: 20.0% (2/10)")
    print("   Fitness Médio: 4.2 ± 2.70")
    print("   Melhor: 0  |  Pior: 8")
    
    print("\n📊 RESULTADOS DO SEU ALGORITMO:")
    print(f"   Taxa de Sucesso: {stats['taxa_sucesso']:.1f}% ({sucessos}/{num_testes})")
    print(f"   Fitness Médio: {stats['fitness_medio']:.2f} ± {stats['fitness_desvio']:.2f}")
    print(f"   Melhor: {stats['fitness_min']}  |  Pior: {stats['fitness_max']}")
    print(f"   Tempo Médio: {stats['tempo_medio']:.1f}s")
    
    print("\n📈 COMPARAÇÃO DIRETA:")
    diff_taxa = stats['taxa_sucesso'] - 20.0
    diff_fitness = 4.2 - stats['fitness_medio']
    
    if diff_taxa > 0:
        print(f"   ✅ Taxa de Sucesso: +{diff_taxa:.1f}% (MELHOR)")
    elif diff_taxa == 0:
        print(f"   ➡️  Taxa de Sucesso: igual (20%)")
    else:
        print(f"   ❌ Taxa de Sucesso: {diff_taxa:.1f}% (pior)")
    
    if diff_fitness > 0:
        print(f"   ✅ Fitness Médio: {diff_fitness:.2f} melhor")
    elif diff_fitness == 0:
        print(f"   ➡️  Fitness Médio: igual")
    else:
        print(f"   ❌ Fitness Médio: {abs(diff_fitness):.2f} pior")
    
    print("\n" + "="*70)
    
    # Salva JSON
    with open('comparacao_andressa.json', 'w') as f:
        json.dump({'resultados': resultados, 'estatisticas': stats}, f, indent=2)
    
    print("\n💾 Dados salvos em 'comparacao_andressa.json'")
    
    return stats

if __name__ == "__main__":
    stats = executar_bateria(10)