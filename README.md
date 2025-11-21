# Algoritmos Evolutivos para Resolução de Sudoku

Este repositório contém implementações de algoritmos genéticos para resolução de quebra-cabeças Sudoku desenvolvidas como parte de um trabalho de conclusão de curso (TCC).

## Estrutura do Projeto

### Arquivos Principais

#### `agSudokuAleatorio.py`
**Implementação proposta no TCC**
- Algoritmo evolutivo desenvolvido para resolver Sudoku
- Pode ser executado de forma independente
- Contém implementações otimizadas com Numba para melhor performance
- Inclui múltiplas estratégias de mutação e recombinação para testes:
  - Mutação uniforme, por gene e por troca
  - Recombinação uniforme e por ponto único
  - Seleção por torneio e por roleta

#### `agSudokuReplicacao.py`
**Implementação baseada na literatura**
- Adaptação de algoritmo da literatura científica (baseado em https://github.com/ifertz/SUdokuSolver)
- Foca em operações por bloco 3x3
- Inclui pré-processamento lógico
- Requer o arquivo `testes.py` para execução devido à estrutura de testes

#### `testes.py`
**Sistema de testes automatizados**
- Executa baterias de testes exaustivos
- Gera gráficos de evolução (geração vs fitness)
- Permite comparação entre diferentes configurações
- Salva resultados consolidados em arquivos de relatório

## Dependências

```python
numpy
numba
matplotlib
struct
time
subprocess
```

## Como Usar

### Execução Individual (agSudokuAleatorio.py)

1. **Configuração manual no código:**
   ```python
   # Descomente a função escreve_arquivo() na main()
   # Modifique os parâmetros conforme necessário:
   populacao = 600
   geracoes = 200
   mutacao = 1
   elitismo = 5
   torneio = 3
   ```

2. **Execução:**
   ```bash
   python agSudokuAleatorio.py
   ```

3. **Saídas geradas:**
   - `relatorio.txt`: Evolução do fitness por geração
   - `tempoExec.txt`: Tempo total de execução

### Execução com Testes Automatizados

1. **Configure os parâmetros em `testes.py`:**
   ```python
   # Modifique o script a ser testado
   script_a_executar = 'agSudokuAleatorio.py'  # ou 'agSudokuReplicacao.py'
   
   # Ajuste os parâmetros de teste
   taxas_mutacao = [30.0, 50.0, 70.0, 90.0]
   tamanhos_populacao = range(4, 101, 4)
   ```

2. **Execute os testes:**
   ```bash
   python testes.py
   ```

3. **Saídas geradas:**
   - Diretório de resultados com gráficos individuais
   - `relatorio_consolidado.txt`: Dados tabulados de todos os testes

## Estrutura de Dados

### Formato do Arquivo `entrada.in`
O arquivo binário contém:
- Tamanho da população (4 bytes)
- Número de gerações (4 bytes)  
- Taxa de mutação (4 bytes float)
- Taxa de elitismo (4 bytes) - apenas agSudokuAleatorio.py
- Tamanho do torneio (4 bytes) - apenas agSudokuAleatorio.py
- Taxa de recombinação (4 bytes float) - apenas agSudokuReplicacao.py
- Arrays NumPy: números válidos, matriz base, células vazias

### Classes Principais

#### `Individuo`
```python
class Individuo:
    def __init__(self, fitness=0, matriz=None):
        self.fitness = fitness    # Número de violações das regras do Sudoku
        self.matriz = matriz      # Matriz 9x9 representando o Sudoku
```

#### `Parametros`
Armazena configurações do algoritmo evolutivo e dados do problema.

## Estratégias Implementadas

### Mutação
- **Uniforme**: Altera um gene aleatório
- **Por gene**: Cada gene tem probabilidade individual de mutação
- **Por troca**: Troca valores entre duas posições
- **Por troca em bloco**: Troca dentro de blocos 3x3 (agSudokuReplicacao.py)

### Recombinação
- **Uniforme**: Combina genes dos pais aleatoriamente
- **Ponto único**: Corte em ponto específico
- **Por bloco**: Opera em blocos 3x3 (agSudokuReplicacao.py)

### Seleção
- **Torneio**: Competição entre k indivíduos
- **Roleta**: Probabilidade proporcional ao fitness inverso

## Função Fitness

A função fitness conta o número total de violações das regras do Sudoku:
- Números repetidos em linhas
- Números repetidos em colunas  
- Numbers repetidos em blocos 3x3

**Objetivo**: Minimizar o fitness (fitness = 0 indica solução válida)

## Otimizações

- Uso de Numba (`@njit`) para acelerar funções críticas
- Operações vetorizadas com NumPy
- Estruturas de dados eficientes para rastreamento de células vazias

## Exemplos de Uso

### Testando Diferentes Configurações
```python
# Em testes.py, modifique:
configs_para_testar = []
for populacao in [50, 100, 200]:
    for mutacao in [1.0, 5.0, 10.0]:
        configs_para_testar.append({
            'populacao': populacao,
            'mutacao': mutacao,
            'geracoes': 100
        })
```

### Adicionando Novas Matrizes de Teste
```python
# Em testes.py, adicione à lista matrizes_para_testar:
{"nome": "NovoTeste",
 "dados": np.array([[0,1,2, ...], [...], ...])}
```

## Resultados

O sistema gera automaticamente:
- Gráficos de convergência por teste
- Relatórios tabulados para análise estatística
- Métricas de tempo de execução
- Comparações entre diferentes configurações

## Características Técnicas

- **Linguagem**: Python 3.12.3
- **Otimização**: Numba JIT compilation
- **Memória**: Estruturas otimizadas para matrizes 9x9
- **Saída**: Arquivos texto e gráficos PNG

## Limitações

- Não implementa paralelização
- Foco específico em Sudoku 9x9
- Dependência de bibliotecas externas para otimização
- Testes podem ser demorados para configurações grandes

## Contribuições

Este código foi desenvolvido como parte de pesquisa acadêmica. Sugestões e melhorias são bem-vindas através de issues e pull requests.# tavia
