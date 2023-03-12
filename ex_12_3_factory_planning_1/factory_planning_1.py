"""Factory Planning 1

Solução do problema 12.3 do livro "Model Building in Mathematical
Programming" de H. Paul Williams.

Dado um conjunto de restrições de capacidade produtiva, mercado, e estoque, o
objetivo é encontrar o número de unidades de cada um de 7 produtos que deve ser
produzido a cada mês num período de 6 meses, maximizando o lucro obtido.
"""
from pulp import *
import pandas as pd

### Definição dos parâmetros do problema

num_products = 7
num_months = 6
num_production_steps = 5

# Cada entrada corresponde a um produto PROD1, ... PROD7
profit_per_unit = [10, 6, 8, 4, 11, 9, 3]

# Custo mensal; igual para todos os produtos
stock_cost_per_unit = 0.5

# Horas necessárias em cada etapa de produção para cada produto
# Linhas correspondem a produtos e colunas a estapas de produção
production_hours = [
    [0.5, 0.1, 0.2, 0.05, 0],
    [0.7, 0.2, 0, 0.03, 0],
    [0, 0, 0.8, 0, 0.01],
    [0, 0.3, 0, 0.07, 0],
    [0.3, 0, 0, 0.1, 0.05],
    [0.2, 0.6, 0, 0, 0],
    [0.5, 0, 0.6, 0.08, 0.05]
]

# Número de máquinas disponível por mês para cada tipo
# Cada tipo de máquina corresponde a uma etapa sucessiva da produção
# Linhas correspondem a etapas/tipos de máquinas e colunas aos meses
machines_available = [
    [3, 4, 4, 4, 3, 4],  # grinders
    [2, 2, 2, 1, 1, 2],  # vertical drills
    [3, 1, 3, 3, 3, 2],  # horizontal drills
    [1, 1, 0, 1, 1, 1],  # borer
    [1, 1, 1, 1, 1, 0]   # planer
]

# Horas disponíveis mensalmente por tipo de máquina
# Considera 16 horas úteis por dia e 24 dias úteis por mês
# Linhas correspondem a tipos de máquina, colunas aos meses
hours_available = [
    [machines_available[k][j]*16*24 for j in range(num_months)]
    for k in range(num_production_steps)
]

# Capacidade de mercado por produto (linhas) por mês (colunas), em unidades
market_limit = [
    [500, 600, 300, 200, 0, 500],
    [1000, 500, 600, 300, 100, 500],
    [300, 200, 0, 400, 500, 100],
    [300, 0, 0, 500, 100, 300],
    [800, 400, 500, 200, 1000, 1100],
    [200, 300, 400, 0, 300, 500],
    [100, 150, 100, 100, 0, 60]
]

### Definição das variáveis de otimização

# Unidades produzidas de cada produto por mês
production = [
    [
        LpVariable(f'p_{i}_{j}', 0, cat=const.LpInteger)
        for j in range(num_months)
    ]
    for i in range(num_products)
]
# Unidades vendidas de cada produto por mês
# Valor máximo dado pela capacidade de mercado
sales = [
    [
        LpVariable(f'v_{i}_{j}', 0, market_limit[i][j], cat=const.LpInteger)
        for j in range(num_months)
    ]
    for i in range(num_products)
]
# Unidades em estoque de cada produto no fim de cada mês
# O valor máximo de 100 unidades por produto é uma restrição do problema
stock = [
    [
        LpVariable(f's_{i}_{j}', 0, 100, cat=const.LpInteger)
        for j in range(num_months)
    ]
    for i in range(num_products)
]

### Construção do problema

prob = LpProblem("factory_planning_1", LpMaximize)

# Função objetivo
# Soma sobre todos os produtos e meses do lucro das vendas menos o custo do
# estoque
prob += lpSum(
    [
        [
            profit_per_unit[i]*sales[i][j] - stock_cost_per_unit*stock[i][j]
            for j in range(num_months)
        ]
        for i in range(num_products)
    ]
)

# Restrição 1: conservação de material
# Todo o material que é vendido ou vai para o estoque no final do mês j
# veio da produção do mês ou do estoque do mês j-1
for i in range(num_products):
    prob += (
        stock[i][0] + sales[i][0] == production[i][0]
    )
    for j in range(1, num_months):
        prob += (
            stock[i][j] + sales[i][j] == stock[i][j-1] + production[i][j]
        )

# Restrição 2: estoques no último mês
# Todos os produtos devem ter 50 unidades em estoque no último mês
for i in range(num_products):
    prob += (
        stock[i][num_months-1] == 50
    )

# Restrição 3: capacidade horária de produção
# A produção deve respeitar a capacidade disponível em cada etapa/máquina
for k in range(num_production_steps):
    for j in range(num_months):
        prob += (
            lpSum(
                [
                    production_hours[i][k]*production[i][j]
                    for i in range(num_products)
                ]
            ) <= hours_available[k][j]
        )

### Resolução do problema e apresentação dos resultados

# Utiliza o solver padrão escolhido pelo PuLP
prob.solve()

# Apresenta status da solução, valor da função objetivo, e variáveis

print()
print("Status da solução:", LpStatus[prob.status])

print("Valor do objetivo =", value(prob.objective))

products = [f'PROD{i+1}' for i in range(num_products)]
months = [f'M{i+1}' for i in range(num_months)]

monthly_production = pd.DataFrame(
    data=[
        [production[i][j].varValue for j in range(num_months)]
        for i in range(num_products)
    ],
    index=products, columns=months, dtype='int'
)
print()
print("Produção por mês")
print(monthly_production)

monthly_stock = pd.DataFrame(
    data=[
        [stock[i][j].varValue for j in range(num_months)]
        for i in range(num_products)
    ],
    index=products, columns=months, dtype='int'
)
print()
print("Estoques por mês")
print(monthly_stock)

monthly_sales = pd.DataFrame(
    data=[
        [sales[i][j].varValue for j in range(num_months)]
        for i in range(num_products)
    ],
    index=products, columns=months, dtype='int'
)
print()
print("Vendas por mês")
print(monthly_sales)
